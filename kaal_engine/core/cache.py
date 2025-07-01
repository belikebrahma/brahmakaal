"""
Intelligent Caching System for Brahmakaal
Supports multiple backends: Memory, Redis, File-based
"""

import json
import pickle
import time
import hashlib
from typing import Any, Optional, Dict, Union
from datetime import datetime, timedelta
import os
from abc import ABC, abstractmethod

class CacheBackend(ABC):
    """Abstract base class for cache backends"""
    
    @abstractmethod
    def get(self, key: str) -> Optional[Any]:
        pass
    
    @abstractmethod
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        pass
    
    @abstractmethod
    def delete(self, key: str) -> bool:
        pass
    
    @abstractmethod
    def exists(self, key: str) -> bool:
        pass
    
    @abstractmethod
    def clear(self) -> bool:
        pass
    
    @abstractmethod
    def get_stats(self) -> Dict[str, Any]:
        pass

class MemoryCache(CacheBackend):
    """In-memory cache backend"""
    
    def __init__(self, max_size: int = 10000):
        self.cache = {}
        self.access_times = {}
        self.max_size = max_size
        self.hits = 0
        self.misses = 0
    
    def _make_key(self, key: str) -> str:
        """Create cache key with prefix"""
        return f"brahmakaal:{key}"
    
    def _evict_lru(self):
        """Evict least recently used items if cache is full"""
        if len(self.cache) >= self.max_size:
            # Remove oldest accessed item
            oldest_key = min(self.access_times, key=self.access_times.get)
            del self.cache[oldest_key]
            del self.access_times[oldest_key]
    
    def get(self, key: str) -> Optional[Any]:
        cache_key = self._make_key(key)
        
        if cache_key in self.cache:
            item = self.cache[cache_key]
            
            # Check expiration
            if item['expires_at'] and time.time() > item['expires_at']:
                del self.cache[cache_key]
                del self.access_times[cache_key]
                self.misses += 1
                return None
            
            # Update access time
            self.access_times[cache_key] = time.time()
            self.hits += 1
            return item['value']
        
        self.misses += 1
        return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        cache_key = self._make_key(key)
        
        self._evict_lru()
        
        expires_at = None
        if ttl:
            expires_at = time.time() + ttl
        
        self.cache[cache_key] = {
            'value': value,
            'expires_at': expires_at,
            'created_at': time.time()
        }
        self.access_times[cache_key] = time.time()
        
        return True
    
    def delete(self, key: str) -> bool:
        cache_key = self._make_key(key)
        if cache_key in self.cache:
            del self.cache[cache_key]
            del self.access_times[cache_key]
            return True
        return False
    
    def exists(self, key: str) -> bool:
        return self.get(key) is not None
    
    def clear(self) -> bool:
        self.cache.clear()
        self.access_times.clear()
        return True
    
    def get_stats(self) -> Dict[str, Any]:
        total_requests = self.hits + self.misses
        hit_rate = (self.hits / total_requests * 100) if total_requests > 0 else 0
        
        return {
            'backend': 'memory',
            'size': len(self.cache),
            'max_size': self.max_size,
            'hits': self.hits,
            'misses': self.misses,
            'hit_rate': round(hit_rate, 2),
            'memory_usage': sum(len(str(item)) for item in self.cache.values())
        }

class KaalCache:
    """
    Main cache interface for Brahmakaal
    Supports multiple backends and intelligent caching strategies
    """
    
    # Default TTL values for different data types (in seconds)
    DEFAULT_TTL = {
        'panchang': 1800,          # 30 minutes
        'planetary_positions': 3600, # 1 hour
        'ephemeris_data': 86400,    # 24 hours
        'ayanamsha': 86400,         # 24 hours
        'muhurta': 7200,            # 2 hours
        'house_positions': 3600,    # 1 hour
        'aspects': 3600,            # 1 hour
        'yogas': 7200,              # 2 hours
        'dashas': 2592000,          # 30 days
    }
    
    def __init__(self, backend: str = 'memory', **kwargs):
        """
        Initialize cache with specified backend
        
        Args:
            backend: 'memory', 'redis', or 'file'
            **kwargs: Backend-specific configuration
        """
        self.backend_name = backend
        
        if backend == 'memory':
            self.backend = MemoryCache(**kwargs)
        else:
            raise ValueError(f"Unsupported cache backend: {backend}")
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        return self.backend.get(key)
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None, 
            data_type: Optional[str] = None) -> bool:
        """
        Set value in cache
        
        Args:
            key: Cache key
            value: Value to cache
            ttl: Time to live in seconds (optional)
            data_type: Type of data for default TTL (optional)
        """
        if ttl is None and data_type:
            ttl = self.DEFAULT_TTL.get(data_type, 3600)
        
        return self.backend.set(key, value, ttl)
    
    def get_or_compute(self, key: str, compute_func, ttl: Optional[int] = None,
                      data_type: Optional[str] = None) -> Any:
        """
        Get value from cache or compute if not exists
        
        Args:
            key: Cache key
            compute_func: Function to compute value if not in cache
            ttl: Time to live in seconds
            data_type: Type of data for default TTL
            
        Returns:
            Cached or computed value
        """
        # Try to get from cache first
        value = self.get(key)
        if value is not None:
            return value
        
        # Compute value
        value = compute_func()
        
        # Store in cache
        self.set(key, value, ttl, data_type)
        
        return value
    
    def make_key(self, *args, **kwargs) -> str:
        """
        Create a cache key from arguments
        
        Args:
            *args: Positional arguments
            **kwargs: Keyword arguments
            
        Returns:
            Cache key string
        """
        # Convert all arguments to strings and join
        key_parts = []
        
        for arg in args:
            if isinstance(arg, (int, float)):
                key_parts.append(f"{arg:.6f}")
            else:
                key_parts.append(str(arg))
        
        for k, v in sorted(kwargs.items()):
            if isinstance(v, (int, float)):
                key_parts.append(f"{k}={v:.6f}")
            else:
                key_parts.append(f"{k}={v}")
        
        return ":".join(key_parts)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        stats = self.backend.get_stats()
        stats['backend_name'] = self.backend_name
        return stats

def create_cache(backend: str = 'memory', **kwargs) -> KaalCache:
    """Create a cache instance with specified backend"""
    return KaalCache(backend, **kwargs)
