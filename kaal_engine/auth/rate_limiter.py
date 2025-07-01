"""
Rate Limiter with Subscription-based Limits
Redis-backed rate limiting with different tiers
"""

import time
import asyncio
from typing import Optional, Dict, Any, Tuple
from datetime import datetime, timedelta
from fastapi import HTTPException, Request
# import redis.asyncio as redis  # Commented out for now
from ..config import get_settings
from .models import SubscriptionTier, SUBSCRIPTION_LIMITS

settings = get_settings()

class RateLimiter:
    """Subscription-based rate limiter"""
    
    def __init__(self):
        self.redis_client = None  # Optional[redis.Redis] = None
        self.memory_cache: Dict[str, Dict[str, Any]] = {}
        self.cleanup_interval = 300  # 5 minutes
        self.last_cleanup = time.time()
        
    async def initialize(self):
        """Initialize Redis connection"""
        # Redis temporarily disabled
        self.redis_client = None
        print("ℹ️ Rate limiter using memory cache (Redis temporarily disabled)")
    
    async def close(self):
        """Close Redis connection"""
        if self.redis_client:
            await self.redis_client.close()
    
    def _memory_cleanup(self):
        """Clean up expired entries from memory cache"""
        current_time = time.time()
        if current_time - self.last_cleanup < self.cleanup_interval:
            return
        
        expired_keys = []
        for key, data in self.memory_cache.items():
            if data.get("expires", 0) < current_time:
                expired_keys.append(key)
        
        for key in expired_keys:
            del self.memory_cache[key]
        
        self.last_cleanup = current_time
    
    async def _get_count(self, key: str, window_seconds: int) -> int:
        """Get current request count for a key"""
        if self.redis_client:
            # Use Redis sliding window
            current_time = time.time()
            pipeline = self.redis_client.pipeline()
            
            # Remove expired entries
            pipeline.zremrangebyscore(key, 0, current_time - window_seconds)
            # Add current request
            pipeline.zadd(key, {str(current_time): current_time})
            # Get count
            pipeline.zcard(key)
            # Set expiration
            pipeline.expire(key, window_seconds)
            
            results = await pipeline.execute()
            return results[2]  # Count result
        else:
            # Use memory cache
            self._memory_cleanup()
            current_time = time.time()
            
            if key not in self.memory_cache:
                self.memory_cache[key] = {
                    "requests": [],
                    "expires": current_time + window_seconds
                }
            
            # Remove expired requests
            cache_data = self.memory_cache[key]
            cache_data["requests"] = [
                req_time for req_time in cache_data["requests"]
                if req_time > current_time - window_seconds
            ]
            
            # Add current request
            cache_data["requests"].append(current_time)
            cache_data["expires"] = current_time + window_seconds
            
            return len(cache_data["requests"])
    
    async def check_rate_limit(
        self,
        user_id: str,
        subscription_tier: SubscriptionTier,
        endpoint: str = "general"
    ) -> Tuple[bool, Dict[str, Any]]:
        """
        Check if request is within rate limits
        Returns (is_allowed, rate_limit_info)
        """
        limits = SUBSCRIPTION_LIMITS[subscription_tier]
        current_time = time.time()
        
        # Rate limit keys
        minute_key = f"rate_limit:{user_id}:minute:{int(current_time // 60)}"
        day_key = f"rate_limit:{user_id}:day:{int(current_time // 86400)}"
        
        # Check minute limit
        minute_count = await self._get_count(minute_key, 60)
        minute_limit = limits["requests_per_minute"]
        minute_remaining = max(0, minute_limit - minute_count)
        
        # Check daily limit
        day_count = await self._get_count(day_key, 86400)
        day_limit = limits["requests_per_day"]
        day_remaining = max(0, day_limit - day_count)
        
        # Determine if request is allowed
        is_allowed = minute_count <= minute_limit and day_count <= day_limit
        
        # Calculate reset times
        minute_reset = (int(current_time // 60) + 1) * 60
        day_reset = (int(current_time // 86400) + 1) * 86400
        
        rate_limit_info = {
            "tier": subscription_tier.value,
            "requests_per_minute": minute_limit,
            "requests_per_day": day_limit,
            "minute_count": minute_count,
            "minute_remaining": minute_remaining,
            "minute_reset": minute_reset,
            "day_count": day_count,
            "day_remaining": day_remaining,
            "day_reset": day_reset,
            "retry_after": 60 - (current_time % 60) if minute_count > minute_limit else None
        }
        
        return is_allowed, rate_limit_info
    
    async def increment_usage(
        self,
        user_id: str,
        endpoint: str,
        subscription_tier: SubscriptionTier
    ):
        """Increment usage counters (already done in check_rate_limit)"""
        # Usage is automatically incremented when checking rate limits
        pass
    
    def get_rate_limit_headers(self, rate_limit_info: Dict[str, Any]) -> Dict[str, str]:
        """Generate rate limit headers for API response"""
        headers = {
            "X-RateLimit-Tier": rate_limit_info["tier"],
            "X-RateLimit-Limit-Minute": str(rate_limit_info["requests_per_minute"]),
            "X-RateLimit-Limit-Day": str(rate_limit_info["requests_per_day"]),
            "X-RateLimit-Remaining-Minute": str(rate_limit_info["minute_remaining"]),
            "X-RateLimit-Remaining-Day": str(rate_limit_info["day_remaining"]),
            "X-RateLimit-Reset-Minute": str(rate_limit_info["minute_reset"]),
            "X-RateLimit-Reset-Day": str(rate_limit_info["day_reset"])
        }
        
        if rate_limit_info.get("retry_after"):
            headers["Retry-After"] = str(int(rate_limit_info["retry_after"]))
        
        return headers

class RateLimitMiddleware:
    """FastAPI middleware for rate limiting"""
    
    def __init__(self, rate_limiter: RateLimiter):
        self.rate_limiter = rate_limiter
    
    async def __call__(self, request: Request, call_next):
        """Process rate limiting for requests"""
        # Skip rate limiting for health and auth endpoints
        if request.url.path in ["/v1/health", "/v1/auth/login", "/v1/auth/register", "/docs", "/redoc", "/openapi.json"]:
            response = await call_next(request)
            return response
        
        # Get user info from request state (set by auth middleware)
        user_id = getattr(request.state, "user_id", None)
        subscription_tier = getattr(request.state, "subscription_tier", SubscriptionTier.FREE)
        
        if not user_id:
            # Allow unauthenticated requests but with strict limits
            user_id = f"anonymous:{request.client.host}"
            subscription_tier = SubscriptionTier.FREE
        
        # Check rate limits
        is_allowed, rate_limit_info = await self.rate_limiter.check_rate_limit(
            user_id=user_id,
            subscription_tier=subscription_tier,
            endpoint=request.url.path
        )
        
        if not is_allowed:
            headers = self.rate_limiter.get_rate_limit_headers(rate_limit_info)
            raise HTTPException(
                status_code=429,
                detail={
                    "error": "Rate limit exceeded",
                    "message": f"Too many requests. Limit: {rate_limit_info['requests_per_minute']}/minute",
                    "tier": subscription_tier.value,
                    "retry_after": rate_limit_info.get("retry_after", 60)
                },
                headers=headers
            )
        
        # Process request
        response = await call_next(request)
        
        # Add rate limit headers to response
        headers = self.rate_limiter.get_rate_limit_headers(rate_limit_info)
        for key, value in headers.items():
            response.headers[key] = value
        
        return response

# Global rate limiter instance
rate_limiter = RateLimiter() 