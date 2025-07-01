"""
Main FastAPI Application for Brahmakaal Enterprise API
Production-ready API with authentication, rate limiting, and comprehensive security
"""

import time
import logging
import traceback
from datetime import datetime
from typing import Dict, Any, Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, Response, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession
import uvicorn

# Configuration and database
from ..config import get_settings
from ..db.database import init_database, get_db, close_database

# Core engines
from ..kaal import Kaal
# from ..cache.redis_backend import RedisCache  # Commented out for now

# Authentication and security
from ..auth.jwt_handler import jwt_handler
from ..auth.rate_limiter import rate_limiter, RateLimitMiddleware
from ..auth.auth_middleware import AuthMiddleware
from ..auth.models import User, UsageLog, SubscriptionTier

# API routes
from .routes import health, panchang, ayanamsha, festivals, muhurta, auth, analytics

settings = get_settings()

# Initialize engines globally
kaal_engine: Optional[Kaal] = None
cache = None  # Optional[RedisCache] = None

# Security middleware instances
auth_middleware = AuthMiddleware()
rate_limit_middleware = RateLimitMiddleware(rate_limiter)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    await startup_event()
    try:
        yield
    finally:
        # Shutdown
        await shutdown_event()

async def startup_event():
    """Initialize application components"""
    global kaal_engine, cache
    
    print("🚀 Starting Brahmakaal Enterprise API...")
    
    # Initialize database
    try:
        await init_database()
        print("✅ Database connection established")
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        raise
    
    # Initialize cache (temporarily disabled)
    cache = None
    print("⚠️ Cache system temporarily disabled")
    
    # Initialize rate limiter
    try:
        await rate_limiter.initialize()
        print("✅ Rate limiter initialized")
    except Exception as e:
        print(f"⚠️ Rate limiter initialization failed: {e}")
    
    # Initialize Kaal engine
    try:
        kaal_engine = Kaal(settings.ephemeris_file_path)
        print("✅ Kaal engine initialized")
    except Exception as e:
        print(f"❌ Kaal engine initialization failed: {e}")
        # Don't raise - some endpoints might work without ephemeris
    
    print("🎉 Brahmakaal Enterprise API started successfully!")

async def shutdown_event():
    """Cleanup application components"""
    print("🛑 Shutting down Brahmakaal Enterprise API...")
    
    # Close rate limiter
    try:
        await rate_limiter.close()
        print("✅ Rate limiter closed")
    except Exception as e:
        print(f"⚠️ Rate limiter cleanup failed: {e}")
    
    # Close cache
    if cache:
        try:
            await cache.close()
            print("✅ Cache closed")
        except Exception as e:
            print(f"⚠️ Cache cleanup failed: {e}")
    
    # Close database
    try:
        await close_database()
        print("✅ Database connection closed")
    except Exception as e:
        print(f"⚠️ Database cleanup failed: {e}")
    
    print("👋 Brahmakaal Enterprise API shutdown complete")

# FastAPI app initialization
app = FastAPI(
    title="Brahmakaal Enterprise API",
    description="""
    🕉️ **Brahmakaal Enterprise API** - The world's most comprehensive Vedic astronomical calculation service

    ## 🌟 **Features**
    
    ### 📅 **Panchang System**
    - Complete lunar calendar calculations with 50+ parameters
    - Multiple ayanamsha support (Lahiri, Krishnamurti, Raman, etc.)
    - High-precision astronomical calculations using DE421 ephemeris
    
    ### 🎉 **Festival Calendar**
    - 50+ Hindu festivals with precise timing
    - 16 regional variations across India
    - Multiple export formats (JSON, iCal, CSV)
    
    ### ⏰ **Muhurta (Electional Astrology)**
    - 6 types of muhurta calculations (Marriage, Business, Travel, etc.)
    - Traditional Vedic analysis with modern precision
    - Quality scoring and auspicious time recommendations
    
    ### 🔐 **Enterprise Security**
    - JWT-based authentication with API key support
    - Subscription-based rate limiting (Free, Basic, Premium, Enterprise)
    - Comprehensive usage analytics and monitoring
    
    ### 🚀 **Performance**
    - Redis-backed caching for sub-second responses
    - Async PostgreSQL database with connection pooling
    - Production-ready with monitoring and observability
    
    ## 📋 **Subscription Tiers**
    
    | Tier | Requests/Min | Requests/Day | Features |
    |------|--------------|--------------|----------|
    | **Free** | 10 | 100 | Basic APIs, JSON export |
    | **Basic** | 60 | 5,000 | All APIs, iCal export, $29/month |
    | **Premium** | 300 | 50,000 | All formats, webhooks, $99/month |
    | **Enterprise** | 1,000 | 200,000 | Custom integration, SLA, $299/month |
    
    ## 🔑 **Authentication**
    
    Use either method:
    1. **JWT Bearer Token**: Include `Authorization: Bearer <token>` header
    2. **API Key**: Include `X-API-Key: <your-api-key>` header
    
    ## 📚 **Quick Start**
    
    1. Register account: `POST /v1/auth/register`
    2. Login: `POST /v1/auth/login` 
    3. Create API key: `POST /v1/auth/api-keys`
    4. Start making API calls with authentication headers
    
    Built with ❤️ for the global Vedic astronomy community.
    """,
    version="1.0.0",
    contact={
        "name": "Brahmakaal Support",
        "email": "support@brahmakaal.com"
    },
    license_info={
        "name": "Commercial License",
        "url": "https://brahmakaal.com/license"
    },
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan
)

# Security middleware
if not settings.is_development:
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["*"]  # Configure with actual domains in production
    )

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=settings.cors_allow_credentials,
    allow_methods=settings.cors_allow_methods,
    allow_headers=settings.cors_allow_headers,
)

# Custom middleware for logging and monitoring
@app.middleware("http")
async def request_logging_middleware(request: Request, call_next):
    """Log requests and add performance headers"""
    start_time = time.time()
    
    # Process request
    response = await call_next(request)
    
    # Calculate response time
    process_time = time.time() - start_time
    
    # Add performance headers
    response.headers["X-Process-Time"] = str(round(process_time * 1000, 2))
    response.headers["X-Timestamp"] = datetime.utcnow().isoformat()
    
    # Log request (exclude health checks)
    if not request.url.path.startswith("/v1/health"):
        print(f"📊 {request.method} {request.url.path} - {response.status_code} - {process_time*1000:.2f}ms")
    
    return response

# Authentication middleware
@app.middleware("http")
async def authentication_middleware(request: Request, call_next):
    """Handle authentication and set user context"""
    return await auth_middleware(request, call_next)

# Rate limiting middleware  
@app.middleware("http")
async def rate_limiting_middleware(request: Request, call_next):
    """Handle rate limiting based on subscription tiers"""
    return await rate_limit_middleware(request, call_next)

# Usage tracking middleware
@app.middleware("http")
async def usage_tracking_middleware(request: Request, call_next):
    """Track API usage for analytics and billing"""
    if not settings.usage_tracking_enabled:
        return await call_next(request)
    
    start_time = time.time()
    
    # Process request
    response = await call_next(request)
    
    # Calculate metrics
    response_time = (time.time() - start_time) * 1000  # Convert to milliseconds
    
    # Skip tracking for health and docs endpoints
    if request.url.path in ["/v1/health", "/docs", "/redoc", "/openapi.json"]:
        return response
    
    # Log usage asynchronously (don't block response)
    try:
        await log_usage_async(request, response, response_time)
    except Exception as e:
        print(f"⚠️ Usage tracking failed: {e}")
    
    return response

async def log_usage_async(request: Request, response: Response, response_time: float):
    """Log API usage for analytics"""
    try:
        user_id = getattr(request.state, "user_id", None)
        api_key = getattr(request.state, "api_key", None)
        
        if not user_id:
            return  # Skip anonymous requests
        
        # Create usage log entry
        usage_log = UsageLog(
            user_id=user_id,
            api_key_id=api_key,
            endpoint=request.url.path,
            method=request.method,
            status_code=response.status_code,
            response_time_ms=response_time,
            ip_address=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent"),
            referer=request.headers.get("referer"),
            request_size_bytes=int(request.headers.get("content-length", 0)),
            response_size_bytes=len(response.body) if hasattr(response, 'body') else 0,
            cache_hit=response.headers.get("X-Cache-Status") == "HIT",
            timestamp=datetime.utcnow()
        )
        
        # Save to database
        async with get_db() as db:
            db.add(usage_log)
            await db.commit()
            
    except Exception as e:
        # Don't let logging errors affect the API response
        print(f"Usage logging error: {e}")

# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions with detailed error responses"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "type": "http_error",
                "code": exc.status_code,
                "message": exc.detail,
                "timestamp": datetime.utcnow().isoformat(),
                "path": request.url.path
            }
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle unexpected exceptions"""
    error_id = str(int(time.time()))
    
    # Log error details
    print(f"❌ Unexpected error [{error_id}]: {str(exc)}")
    if settings.debug:
        print(traceback.format_exc())
    
    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "type": "internal_error",
                "code": 500,
                "message": "Internal server error occurred",
                "error_id": error_id,
                "timestamp": datetime.utcnow().isoformat(),
                "path": request.url.path
            }
        }
    )

# Dependency providers
async def get_kaal_engine() -> Optional[Kaal]:
    """Get initialized Kaal engine"""
    return kaal_engine

async def get_cache():
    """Get cache instance"""
    return cache

# Include API routes with dependency overrides
app.include_router(health.router, prefix="/v1")
app.include_router(auth.router, prefix="/v1")
app.include_router(panchang.router, prefix="/v1")
app.include_router(ayanamsha.router, prefix="/v1")
app.include_router(festivals.router, prefix="/v1")
app.include_router(muhurta.router, prefix="/v1")
app.include_router(analytics.router, prefix="/v1")

# Override dependencies
app.dependency_overrides[get_kaal_engine] = lambda: kaal_engine
app.dependency_overrides[get_cache] = lambda: cache

# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    """API root endpoint with service information"""
    return {
        "service": "Brahmakaal Enterprise API",
        "version": "1.0.0",
        "description": "The world's most comprehensive Vedic astronomical calculation service",
        "documentation": "/docs",
        "status": "operational",
        "features": {
            "panchang": "Complete lunar calendar calculations",
            "festivals": "50+ Hindu festivals with regional variations",
            "muhurta": "Electional astrology with traditional analysis",
            "ayanamsha": "Multiple calculation systems supported"
        },
        "authentication": {
            "methods": ["JWT Bearer Token", "API Key"],
            "endpoints": {
                "register": "/v1/auth/register",
                "login": "/v1/auth/login",
                "create_api_key": "/v1/auth/api-keys"
            }
        },
        "subscription_tiers": ["free", "basic", "premium", "enterprise"],
        "support": {
            "email": "support@brahmakaal.com",
            "documentation": "/docs"
        }
    }

# Development server
if __name__ == "__main__":
    uvicorn.run(
        "kaal_engine.api.app:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_level=settings.log_level.lower(),
        access_log=True
    ) 