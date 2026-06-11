"""
Intelligent Cache Optimizer for Astronomical Calculations
Provides smart caching with astronomical-aware TTL and invalidation
"""

import json
import time
import hashlib
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, Union
from functools import wraps

import redis
from fastapi import HTTPException


class SmartCache:
    """
    Astronomical-aware intelligent caching system.
    Automatically adjusts TTL based on astronomical events.
    """
    
    def __init__(self, redis_client=None):
        self.redis = redis_client or redis.Redis(decode_responses=True)
        self.logger = logging.getLogger(__name__)
        
        # Cache TTL strategies by endpoint
        self.ttl_strategies = {
            "panchang": self._panchang_ttl_strategy,
            "horoscope": self._horoscope_ttl_strategy,
            "muhurta": self._muhurta_ttl_strategy,
            "transits": self._transits_ttl_strategy,
            "panchaka-periods": self._panchaka_ttl_strategy,
            "udaya-lagna-periods": self._udaya_lagna_ttl_strategy,
            "complete-muhurta-periods": self._complete_muhurta_ttl_strategy,
            "inauspicious-periods": self._inauspicious_ttl_strategy,
            "extended-calendar-systems": self._calendar_ttl_strategy
        }
        
        # Performance tracking
        self.cache_hits = 0
        self.cache_misses = 0
        self.total_requests = 0
    
    def make_key(self, endpoint: str, *args, **kwargs) -> str:
        """Generate intelligent cache key."""
        
        # Create base key components
        key_components = [endpoint]
        
        # Add positional arguments
        for arg in args:
            if isinstance(arg, (int, float)):
                key_components.append(f"{arg:.6f}")
            else:
                key_components.append(str(arg))
        
        # Add keyword arguments (sorted for consistency)
        for key, value in sorted(kwargs.items()):
            if key in ['latitude', 'longitude']:
                # Round coordinates to reduce cache fragmentation
                key_components.append(f"{key}:{float(value):.4f}")
            elif key == 'date':
                key_components.append(f"{key}:{value}")
            elif key == 'time':
                # Round time to nearest minute for caching
                if ':' in str(value):
                    time_parts = str(value).split(':')
                    rounded_time = f"{time_parts[0]}:{time_parts[1]}:00"
                    key_components.append(f"{key}:{rounded_time}")
                else:
                    key_components.append(f"{key}:{value}")
            else:
                key_components.append(f"{key}:{value}")
        
        # Create hash for very long keys
        cache_key = ":".join(key_components)
        if len(cache_key) > 200:
            cache_key = f"{endpoint}:{hashlib.md5(cache_key.encode()).hexdigest()}"
        
        return f"brahmakaal:{cache_key}"
    
    def get(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """Get data from cache with performance tracking."""
        self.total_requests += 1
        
        try:
            cached_data = self.redis.get(cache_key)
            if cached_data:
                self.cache_hits += 1
                data = json.loads(cached_data)
                
                # Add cache metadata
                data['_cache_info'] = {
                    'hit': True,
                    'retrieved_at': datetime.utcnow().isoformat(),
                    'key': cache_key.split(':')[-1][:20] + '...' if len(cache_key) > 50 else cache_key
                }
                
                return data
            else:
                self.cache_misses += 1
                return None
                
        except (redis.RedisError, json.JSONDecodeError) as e:
            self.logger.warning(f"Cache get error for key {cache_key}: {e}")
            self.cache_misses += 1
            return None
    
    def set(self, cache_key: str, data: Dict[str, Any], data_type: str = "general") -> bool:
        """Set data in cache with intelligent TTL."""
        
        try:
            # Calculate intelligent TTL
            ttl = self._calculate_intelligent_ttl(data_type, data)
            
            # Add cache metadata
            cache_data = data.copy()
            cache_data['_cache_info'] = {
                'cached_at': datetime.utcnow().isoformat(),
                'ttl_seconds': ttl,
                'data_type': data_type,
                'expires_at': (datetime.utcnow() + timedelta(seconds=ttl)).isoformat()
            }
            
            # Store in Redis
            success = self.redis.setex(
                cache_key,
                ttl,
                json.dumps(cache_data, default=str)
            )
            
            if success:
                self.logger.debug(f"Cached {data_type} data for {ttl}s with key {cache_key}")
            
            return success
            
        except (redis.RedisError, TypeError) as e:
            self.logger.warning(f"Cache set error for key {cache_key}: {e}")
            return False
    
    def _calculate_intelligent_ttl(self, data_type: str, data: Dict[str, Any]) -> int:
        """Calculate TTL based on data type and astronomical events."""
        
        if data_type in self.ttl_strategies:
            return self.ttl_strategies[data_type](data)
        
        # Default TTL: 1 hour
        return 3600
    
    def _panchang_ttl_strategy(self, data: Dict[str, Any]) -> int:
        """Smart TTL for panchang data based on next astronomical event."""
        
        try:
            # Get tithi and nakshatra end times
            tithi_end = data.get('tithi_end_time', {}).get('end_time')
            nakshatra_end = data.get('nakshatra_end_time', {}).get('end_time')
            
            if tithi_end and nakshatra_end:
                # Parse end times
                tithi_dt = datetime.fromisoformat(tithi_end.replace('Z', '+00:00'))
                nakshatra_dt = datetime.fromisoformat(nakshatra_end.replace('Z', '+00:00'))
                
                # Find the next event
                next_event = min(tithi_dt, nakshatra_dt)
                now = datetime.utcnow()
                
                if next_event > now:
                    # Cache until next event (with 5-minute buffer)
                    ttl = int((next_event - now).total_seconds()) - 300
                    return max(ttl, 300)  # Minimum 5 minutes
            
            # Default: 2 hours
            return 7200
            
        except Exception as e:
            self.logger.warning(f"Error calculating panchang TTL: {e}")
            return 3600
    
    def _horoscope_ttl_strategy(self, data: Dict[str, Any]) -> int:
        """Horoscopes never change - long TTL."""
        return 24 * 3600  # 24 hours
    
    def _muhurta_ttl_strategy(self, data: Dict[str, Any]) -> int:
        """Muhurta changes every few hours."""
        return 4 * 3600  # 4 hours
    
    def _transits_ttl_strategy(self, data: Dict[str, Any]) -> int:
        """Transits change daily."""
        return 6 * 3600  # 6 hours
    
    def _panchaka_ttl_strategy(self, data: Dict[str, Any]) -> int:
        """Panchaka periods are hourly - short TTL."""
        return 3600  # 1 hour
    
    def _udaya_lagna_ttl_strategy(self, data: Dict[str, Any]) -> int:
        """Udaya lagna changes every 2 hours approximately."""
        return 2 * 3600  # 2 hours
    
    def _complete_muhurta_ttl_strategy(self, data: Dict[str, Any]) -> int:
        """Complete muhurta periods are calculated daily."""
        return 12 * 3600  # 12 hours
    
    def _inauspicious_ttl_strategy(self, data: Dict[str, Any]) -> int:
        """Inauspicious periods calculated daily."""
        return 8 * 3600  # 8 hours
    
    def _calendar_ttl_strategy(self, data: Dict[str, Any]) -> int:
        """Calendar systems change rarely."""
        return 24 * 3600  # 24 hours
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache performance statistics."""
        
        hit_rate = (self.cache_hits / self.total_requests * 100) if self.total_requests > 0 else 0
        
        return {
            "total_requests": self.total_requests,
            "cache_hits": self.cache_hits,
            "cache_misses": self.cache_misses,
            "hit_rate_percentage": round(hit_rate, 2),
            "redis_info": self._get_redis_stats()
        }
    
    def _get_redis_stats(self) -> Dict[str, Any]:
        """Get Redis statistics."""
        try:
            info = self.redis.info()
            return {
                "used_memory_human": info.get('used_memory_human', 'N/A'),
                "connected_clients": info.get('connected_clients', 0),
                "total_commands_processed": info.get('total_commands_processed', 0),
                "keyspace_hits": info.get('keyspace_hits', 0),
                "keyspace_misses": info.get('keyspace_misses', 0)
            }
        except Exception as e:
            return {"error": str(e)}
    
    def warm_cache(self, locations: list, dates: list):
        """Pre-warm cache with popular locations and dates."""
        
        self.logger.info(f"Warming cache for {len(locations)} locations and {len(dates)} dates")
        
        # This would be implemented to pre-calculate popular combinations
        # For now, just log the intention
        for location in locations:
            for date in dates:
                self.logger.debug(f"Would warm cache for {location} on {date}")


class CacheOptimizer:
    """
    High-level cache optimization manager.
    Provides decorators and optimization strategies.
    """
    
    def __init__(self, cache: SmartCache):
        self.cache = cache
        self.logger = logging.getLogger(__name__)
    
    def cached_endpoint(self, data_type: str = "general", cache_on_error: bool = False):
        """
        Decorator for caching API endpoint responses.
        
        Args:
            data_type: Type of data being cached (affects TTL strategy)
            cache_on_error: Whether to return cached data on calculation errors
        """
        def decorator(func):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                # Generate cache key
                cache_key = self.cache.make_key(data_type, *args, **kwargs)
                
                # Try to get from cache
                cached_result = self.cache.get(cache_key)
                if cached_result:
                    # Remove cache metadata for clean response
                    clean_result = cached_result.copy()
                    clean_result.pop('_cache_info', None)
                    return clean_result
                
                try:
                    # Calculate new result
                    result = await func(*args, **kwargs)
                    
                    # Cache the result
                    if result:
                        self.cache.set(cache_key, result, data_type)
                    
                    return result
                    
                except Exception as e:
                    if cache_on_error and cached_result:
                        self.logger.warning(f"Returning stale cache due to error: {e}")
                        clean_result = cached_result.copy()
                        clean_result.pop('_cache_info', None)
                        clean_result['_warning'] = 'Stale data due to calculation error'
                        return clean_result
                    else:
                        raise
            
            return wrapper
        return decorator
    
    def invalidate_pattern(self, pattern: str) -> int:
        """Invalidate cache keys matching a pattern."""
        
        try:
            keys = self.cache.redis.keys(f"brahmakaal:{pattern}")
            if keys:
                deleted = self.cache.redis.delete(*keys)
                self.logger.info(f"Invalidated {deleted} cache keys matching pattern: {pattern}")
                return deleted
            return 0
        except Exception as e:
            self.logger.error(f"Error invalidating cache pattern {pattern}: {e}")
            return 0
    
    def cleanup_expired(self) -> Dict[str, int]:
        """Clean up expired cache entries."""
        
        # Redis automatically handles TTL, but we can scan for cleanup
        try:
            info = self.cache.redis.info()
            return {
                "expired_keys": info.get('expired_keys', 0),
                "evicted_keys": info.get('evicted_keys', 0)
            }
        except Exception as e:
            self.logger.error(f"Error getting cleanup stats: {e}")
            return {"error": str(e)}


# Global cache instance
_smart_cache = None
_cache_optimizer = None


def get_smart_cache() -> SmartCache:
    """Get global smart cache instance."""
    global _smart_cache
    if _smart_cache is None:
        try:
            _smart_cache = SmartCache()
        except Exception as e:
            logging.warning(f"Failed to initialize Redis cache: {e}")
            # Return a dummy cache that does nothing
            _smart_cache = DummyCache()
    return _smart_cache


def get_cache_optimizer() -> CacheOptimizer:
    """Get global cache optimizer instance."""
    global _cache_optimizer
    if _cache_optimizer is None:
        _cache_optimizer = CacheOptimizer(get_smart_cache())
    return _cache_optimizer


class DummyCache:
    """Dummy cache for when Redis is not available."""
    
    def make_key(self, *args, **kwargs) -> str:
        return "dummy_key"
    
    def get(self, cache_key: str) -> None:
        return None
    
    def set(self, cache_key: str, data: Dict[str, Any], data_type: str = "general") -> bool:
        return False
    
    def get_cache_stats(self) -> Dict[str, Any]:
        return {"status": "disabled", "reason": "Redis not available"} 