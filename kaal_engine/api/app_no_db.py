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
from .routes.health import router as health_router
from .routes.panchang import router as panchang_router
from .routes.muhurta import router as muhurta_router
from .routes.festivals import router as festivals_router
from .routes.ayanamsha import router as ayanamsha_router

settings = get_settings()

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
    print("🚀 Starting Brahmakaal Enterprise API (No DB Mode)...")
    print("✅ Core Kaal engine initialized")
    print("⚠️  Database features disabled for testing")

async def shutdown_event():
    """Application shutdown tasks"""
    print("👋 Brahmakaal Enterprise API stopped")

# Include working routers
app.include_router(health_router, prefix="/v1", tags=["Health"])
app.include_router(panchang_router, prefix="/v1", tags=["Panchang"])
app.include_router(muhurta_router, prefix="/v1", tags=["Muhurta"])
app.include_router(festivals_router, prefix="/v1", tags=["Festivals"])
app.include_router(ayanamsha_router, prefix="/v1", tags=["Ayanamsha"])

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