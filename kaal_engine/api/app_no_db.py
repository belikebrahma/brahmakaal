"""
Simplified Brahmakaal API without database dependencies for testing
"""

import time
import logging
from datetime import datetime
from typing import Dict, Any
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# Configuration
from ..config import get_settings

# Core engines (working ones)
from ..kaal import Kaal

# Import working routes (non-auth ones)
from .routes import health as health_routes
from .routes import panchang as panchang_routes
from .routes import muhurta as muhurta_routes
from .routes import festivals as festivals_routes
from .routes import ayanamsha as ayanamsha_routes
from ..db.database import get_db
from ..core.muhurta import MuhurtaEngine
from ..core.festivals import FestivalEngine
from ..core.ayanamsha import AyanamshaEngine

settings = get_settings()
kaal_engine = None

class DummyDBSession:
    """No-op async DB session used by no-database mode."""

    def add(self, *_args, **_kwargs):
        return None

    async def commit(self):
        return None

    async def rollback(self):
        return None

    async def close(self):
        return None

    async def execute(self, *_args, **_kwargs):
        return None

dummy_db = DummyDBSession()

async def get_dummy_db():
    return dummy_db

async def get_dummy_cache():
    return None

async def get_no_db_kaal_engine():
    if kaal_engine is None:
        from fastapi import HTTPException
        raise HTTPException(status_code=503, detail="Kaal engine not initialized")
    return kaal_engine

async def get_no_db_muhurta_engine():
    return MuhurtaEngine(await get_no_db_kaal_engine())

async def get_no_db_festival_engine():
    from ..core.festivals import FestivalEngine
    kaal = await get_no_db_kaal_engine()
    return FestivalEngine(kaal, lat=28.6139, lod=77.2090, timezone_offset=5.5)

async def get_no_db_ayanamsha_engine():
    return AyanamshaEngine()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager - simplified without database"""
    await startup_event()
    yield
    await shutdown_event()

# Create FastAPI application
app = FastAPI(
    title="Brahmakaal Enterprise API (No DB Mode)",
    description="Comprehensive Vedic Astronomy and Panchang API - Testing Mode",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=settings.cors_allow_credentials,
    allow_methods=settings.cors_allow_methods,
    allow_headers=settings.cors_allow_headers,
)

# Add request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all requests with timing"""
    start_time = time.time()
    
    # Process request
    response = await call_next(request)
    
    # Calculate processing time
    process_time = time.time() - start_time
    
    # Log request details
    logging.info(
        f"{request.method} {request.url} - "
        f"Status: {response.status_code} - "
        f"Time: {process_time:.4f}s"
    )
    
    # Add performance headers
    response.headers["X-Process-Time"] = str(process_time)
    response.headers["X-Timestamp"] = str(int(time.time()))
    
    return response

async def startup_event():
    """Application startup tasks - simplified"""
    global kaal_engine
    print("🚀 Starting Brahmakaal Enterprise API (No DB Mode)...")
    kaal_engine = Kaal(settings.ephemeris_file_path)
    print(f"✅ Core Kaal engine initialized from {settings.ephemeris_file_path}")
    print("⚠️  Database features disabled for testing")

async def shutdown_event():
    """Application shutdown tasks"""
    print("👋 Brahmakaal Enterprise API stopped")

# Include working routers
app.include_router(health_routes.router, prefix="/v1", tags=["Health"])
app.include_router(panchang_routes.router, prefix="/v1", tags=["Panchang"])
app.include_router(muhurta_routes.router, prefix="/v1", tags=["Muhurta"])
app.include_router(festivals_routes.router, prefix="/v1", tags=["Festivals"])
app.include_router(ayanamsha_routes.router, prefix="/v1", tags=["Ayanamsha"])

# Replace full-app/database dependencies with no-DB implementations.
app.dependency_overrides[get_db] = get_dummy_db
app.dependency_overrides[panchang_routes.get_kaal_engine] = get_no_db_kaal_engine
app.dependency_overrides[panchang_routes.get_cache] = get_dummy_cache
app.dependency_overrides[muhurta_routes.get_muhurta_engine] = get_no_db_muhurta_engine
app.dependency_overrides[muhurta_routes.get_cache] = get_dummy_cache
app.dependency_overrides[festivals_routes.get_festival_engine] = get_no_db_festival_engine
app.dependency_overrides[festivals_routes.get_cache] = get_dummy_cache
app.dependency_overrides[ayanamsha_routes.get_ayanamsha_engine] = get_no_db_ayanamsha_engine
app.dependency_overrides[ayanamsha_routes.get_cache] = get_dummy_cache

@app.get("/")
async def root():
    """Welcome endpoint"""
    return {
        "message": "Welcome to Brahmakaal Enterprise API",
        "version": "1.0.0",
        "mode": "No Database Testing Mode",
        "status": "operational",
        "features": [
            "Panchang calculations",
            "Muhurta analysis", 
            "Festival calendar",
            "Ayanamsha calculations",
            "Vedic astronomy engine"
        ],
        "docs": "/docs",
        "health": "/v1/health",
        "timestamp": datetime.utcnow().isoformat(),
        "note": "Authentication features disabled in testing mode"
    }

@app.get("/status")
async def status():
    """Simple status endpoint"""
    return {
        "status": "healthy",
        "mode": "testing",
        "timestamp": datetime.utcnow().isoformat(),
        "uptime": "unknown"
    } 