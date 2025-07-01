"""
Redis Cache Backend for Brahmakaal Enterprise API
Async Redis operations with connection pooling and fallback
"""

import json
import asyncio
from typing import Any, Optional, Dict, Union
from datetime import datetime, timedelta

try:
    import redis.asyncio as aioredis
    from redis.asyncio import Redis
    REDIS_AVAILABLE = True
except ImportError:
    try:
        # Fallback to older aioredis if redis.asyncio not available
        import aioredis
        from aioredis import Redis
        REDIS_AVAILABLE = True
    except (ImportError, TypeError):
        # Handle both import errors and compatibility issues
        REDIS_AVAILABLE = False
        Redis = None
        aioredis = None

from ..config import get_settings

settings = get_settings()

class RedisCache:
    """Redis cache backend with fallback to memory"""
    
    def __init__(self):
        self.redis_pool: Optional[Redis] = None
        self.memory_cache: Dict[str, Dict[str, Any]] = {}
        self.redis_available = REDIS_AVAILABLE and settings.redis_enabled
        
    async def initialize(self):
        """Initialize Redis connection pool"""
        if not self.redis_available:
            print("⚠️ Redis not available, using memory cache")
            return
        
        try:
            # Try redis.asyncio first (redis >= 4.2.0)
            if hasattr(aioredis, 'from_url'):
                self.redis_pool = aioredis.from_url(
                    settings.redis_url,
                    encoding="utf-8",
                    decode_responses=True,
                    max_connections=settings.redis_pool_size,
                    socket_timeout=settings.redis_timeout,
                    socket_connect_timeout=settings.redis_timeout,
                    retry_on_timeout=True
                )
            else:
                # Fallback for older aioredis
                self.redis_pool = await aioredis.create_redis_pool(
                    settings.redis_url,
                    encoding="utf-8",
                    maxsize=settings.redis_pool_size,
                    timeout=settings.redis_timeout
                )
            
            # Test connection
            await self.redis_pool.ping()
            print("✅ Redis cache initialized")
            
        except Exception as e:
            print(f"⚠️ Redis initialization failed: {e}")
            print("Falling back to memory cache")
            self.redis_available = False
            self.redis_pool = None
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        cache_key = f"{settings.cache_prefix}:{key}"
        
        if self.redis_available and self.redis_pool:
            try:
                value = await self.redis_pool.get(cache_key)
                if value:
                    return json.loads(value)
                return None
            except Exception as e:
                print(f"Redis get error: {e}")
                # Fall through to memory cache
        
        # Memory cache fallback
        if cache_key in self.memory_cache:
            cache_item = self.memory_cache[cache_key]
            if cache_item['expires_at'] > datetime.utcnow():
                return cache_item['value']
            else:
                # Expired
                del self.memory_cache[cache_key]
        
        return None
    
    async def set(self, key: str, value: Any, ttl: int = None) -> bool:
        """Set value in cache with optional TTL"""
        cache_key = f"{settings.cache_prefix}:{key}"
        ttl = ttl or settings.cache_ttl_seconds
        
        if self.redis_available and self.redis_pool:
            try:
                serialized_value = json.dumps(value, default=str)
                await self.redis_pool.setex(cache_key, ttl, serialized_value)
                return True
            except Exception as e:
                print(f"Redis set error: {e}")
                # Fall through to memory cache
        
        # Memory cache fallback
        self.memory_cache[cache_key] = {
            'value': value,
            'expires_at': datetime.utcnow() + timedelta(seconds=ttl)
        }
        
        # Clean up expired memory cache entries periodically
        await self._cleanup_memory_cache()
        return True
    
    async def delete(self, key: str) -> bool:
        """Delete value from cache"""
        cache_key = f"{settings.cache_prefix}:{key}"
        
        if self.redis_available and self.redis_pool:
            try:
                await self.redis_pool.delete(cache_key)
                return True
            except Exception as e:
                print(f"Redis delete error: {e}")
        
        # Memory cache
        if cache_key in self.memory_cache:
            del self.memory_cache[cache_key]
        
        return True
    
    async def exists(self, key: str) -> bool:
        """Check if key exists in cache"""
        cache_key = f"{settings.cache_prefix}:{key}"
        
        if self.redis_available and self.redis_pool:
            try:
                return await self.redis_pool.exists(cache_key) > 0
            except Exception as e:
                print(f"Redis exists error: {e}")
        
        # Memory cache
        if cache_key in self.memory_cache:
            cache_item = self.memory_cache[cache_key]
            if cache_item['expires_at'] > datetime.utcnow():
                return True
            else:
                del self.memory_cache[cache_key]
        
        return False
    
    async def clear_pattern(self, pattern: str) -> int:
        """Clear all keys matching pattern"""
        pattern_key = f"{settings.cache_prefix}:{pattern}"
        
        if self.redis_available and self.redis_pool:
            try:
                keys = await self.redis_pool.keys(pattern_key)
                if keys:
                    await self.redis_pool.delete(*keys)
                    return len(keys)
                return 0
            except Exception as e:
                print(f"Redis clear pattern error: {e}")
        
        # Memory cache
        keys_to_delete = [k for k in self.memory_cache.keys() if pattern in k]
        for key in keys_to_delete:
            del self.memory_cache[key]
        
        return len(keys_to_delete)
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        stats = {
            "backend": "redis" if self.redis_available else "memory",
            "redis_available": self.redis_available,
            "memory_cache_size": len(self.memory_cache)
        }
        
        if self.redis_available and self.redis_pool:
            try:
                info = await self.redis_pool.info()
                stats.update({
                    "redis_memory_used": info.get("used_memory_human", "unknown"),
                    "redis_connected_clients": info.get("connected_clients", 0),
                    "redis_total_commands": info.get("total_commands_processed", 0)
                })
            except Exception as e:
                stats["redis_error"] = str(e)
        
        return stats
    
    async def _cleanup_memory_cache(self):
        """Clean up expired entries from memory cache"""
        if len(self.memory_cache) < 1000:  # Only cleanup if getting large
            return
        
        now = datetime.utcnow()
        expired_keys = [
            key for key, item in self.memory_cache.items()
            if item['expires_at'] <= now
        ]
        
        for key in expired_keys:
            del self.memory_cache[key]
    
    async def close(self):
        """Close Redis connection"""
        if self.redis_pool:
            await self.redis_pool.close()
            print("✅ Redis connection closed")

# Create cache instance
cache = RedisCache()

# Cache decorator for functions
def cached(ttl: int = None, key_prefix: str = ""):
    """Decorator to cache function results"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # Generate cache key
            key_parts = [key_prefix, func.__name__]
            key_parts.extend(str(arg) for arg in args)
            key_parts.extend(f"{k}={v}" for k, v in sorted(kwargs.items()))
            cache_key = ":".join(filter(None, key_parts))
            
            # Try to get from cache
            cached_result = await cache.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # Execute function and cache result
            result = await func(*args, **kwargs)
            await cache.set(cache_key, result, ttl)
            
            return result
        return wrapper
    return decorator 