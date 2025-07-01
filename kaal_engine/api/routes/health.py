"""
Health Check and Status Endpoints
"""

import time
from datetime import datetime
from typing import Dict, Any
import os

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from ..models import HealthResponse
from ...db.database import get_db
from ...config import get_settings

router = APIRouter()

# Track server start time for uptime calculation
server_start_time = time.time()

@router.get("/health", response_model=HealthResponse)
async def health_check(
    db: AsyncSession = Depends(get_db),
    cache = Depends(lambda: None)  # Will be properly injected in main app
):
    """
    Comprehensive health check endpoint
    
    Returns system status including:
    - API service status
    - Database connectivity
    - Cache system status  
    - Ephemeris file availability
    """
    settings = get_settings()
    
    # Check database connection
    database_connected = True
    try:
        # Simple query to test connection
        await db.execute(text("SELECT 1"))
    except Exception as e:
        print(f"Database health check failed: {e}")
        database_connected = False
    
    # Check cache connection
    cache_connected = True
    try:
        if cache:
            await cache.set("health_check", "ok", ttl=60)
            cache_connected = await cache.get("health_check") == "ok"
        else:
            cache_connected = False  # Cache is disabled
    except Exception as e:
        print(f"Cache health check failed: {e}")
        cache_connected = False
    
    # Check ephemeris file
    ephemeris_loaded = os.path.exists(settings.ephemeris_file_path)
    
    # Calculate uptime
    uptime_seconds = int(time.time() - server_start_time)
    
    # Determine overall status
    status = "healthy"
    if not database_connected or not ephemeris_loaded:
        status = "degraded"
    if not database_connected:
        status = "unhealthy"
    
    return HealthResponse(
        status=status,
        version=settings.version,
        uptime_seconds=uptime_seconds,
        database_connected=database_connected,
        cache_connected=cache_connected,
        ephemeris_loaded=ephemeris_loaded,
        timestamp=datetime.utcnow()
    )

@router.get("/status", response_model=Dict[str, Any])
async def detailed_status(
    cache = Depends(lambda: None)
):
    """
    Detailed system status with performance metrics
    """
    settings = get_settings()
    
    # Get cache statistics
    cache_stats = {}
    if cache:
        try:
            cache_stats = await cache.get_stats()
        except Exception as e:
            cache_stats = {"error": str(e)}
    else:
        cache_stats = {"status": "disabled"}
    
    return {
        "service": "Brahmakaal API",
        "version": settings.version,
        "environment": settings.environment,
        "uptime_seconds": int(time.time() - server_start_time),
        "cache_statistics": cache_stats,
        "configuration": {
            "rate_limit_storage": settings.rate_limit_storage,
            "database_url": "***configured***",
            "redis_enabled": settings.redis_enabled,
            "ephemeris_file_path": settings.ephemeris_file_path,
            "log_level": settings.log_level,
            "debug": settings.debug
        },
        "features": {
            "authentication": True,
            "rate_limiting": True,
            "usage_tracking": settings.usage_tracking_enabled,
            "analytics": settings.analytics_enabled,
            "caching": settings.redis_enabled
        },
        "timestamp": datetime.utcnow()
    } 