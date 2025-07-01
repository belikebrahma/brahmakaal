"""
Database Management for Brahmakaal Enterprise API
Async PostgreSQL database with SQLAlchemy 2.0
"""

import uuid
from typing import AsyncGenerator, Optional
from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import event, text
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse

from ..config import get_settings

settings = get_settings()

class Base(DeclarativeBase):
    """Base class for all database models"""
    pass

# Database engine and session factory
engine: Optional[create_async_engine] = None
SessionLocal: Optional[async_sessionmaker[AsyncSession]] = None

def process_database_url_for_asyncpg(url: str) -> tuple[str, dict]:
    """Process database URL for asyncpg compatibility and extract connect_args"""
    # Convert postgres:// to postgresql+asyncpg://
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql+asyncpg://", 1)
    elif not url.startswith("postgresql+asyncpg://"):
        # Convert postgresql:// to postgresql+asyncpg://
        url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
    
    # Parse URL to handle SSL parameters
    parsed = urlparse(url)
    query_params = parse_qs(parsed.query)
    
    # Extract SSL-related parameters that need special handling
    connect_args = {}
    
    # Handle sslmode parameter - convert to ssl parameter for asyncpg
    if 'sslmode' in query_params:
        sslmode = query_params['sslmode'][0]
        if sslmode in ['disable', 'allow', 'prefer', 'require', 'verify-ca', 'verify-full']:
            connect_args['ssl'] = sslmode
        # Remove from URL params
        del query_params['sslmode']
    
    # Keep other SSL parameters in the URL as asyncpg supports them there
    allowed_url_params = {
        'sslcert', 'sslkey', 'sslrootcert', 'sslcrl', 'sslpassword',
        'ssl_min_protocol_version', 'ssl_max_protocol_version',
        'connect_timeout', 'command_timeout', 'server_settings'
    }
    
    # Filter parameters for the URL
    filtered_params = {}
    for key, values in query_params.items():
        if key in allowed_url_params:
            filtered_params[key] = values
    
    # Rebuild the URL with filtered parameters
    new_query = urlencode(filtered_params, doseq=True)
    new_parsed = parsed._replace(query=new_query)
    clean_url = urlunparse(new_parsed)
    
    return clean_url, connect_args

async def init_database():
    """Initialize database connection and create tables"""
    global engine, SessionLocal
    
    try:
        # Process the database URL for asyncpg compatibility
        db_url, connect_args = process_database_url_for_asyncpg(settings.database_url)
        
        print(f"🔗 Connecting to database...")
        # Show sanitized URL (hide credentials)
        safe_url = db_url.split('@')[0] + '@***'
        print(f"🔗 Database URL: {safe_url}")
        if connect_args:
            print(f"🔗 Connect args: {connect_args}")
        
        # Create engine with SSL parameters passed via connect_args
        engine = create_async_engine(
            db_url,
            echo=settings.debug,
            future=True,
            pool_size=settings.database_pool_size,
            max_overflow=settings.database_max_overflow,
            pool_timeout=settings.database_pool_timeout,
            pool_recycle=settings.database_pool_recycle,
            connect_args=connect_args,  # Pass SSL parameters here
        )
        
        # Create session factory
        SessionLocal = async_sessionmaker(
            engine,
            class_=AsyncSession,
            expire_on_commit=False
        )
        
        # Test connection
        async with engine.begin() as conn:
            await conn.execute(text("SELECT 1"))
        
        print("✅ Database connection established")
        
        # Create tables
        await create_tables()
        
        return True
        
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        raise

async def close_database():
    """Close database connection"""
    global engine
    if engine:
        await engine.dispose()
        print("✅ Database connection closed")

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency to get database session"""
    if not SessionLocal:
        raise RuntimeError("Database not initialized")
    
    async with SessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

@asynccontextmanager
async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """Context manager to get database session"""
    if not SessionLocal:
        raise RuntimeError("Database not initialized")
    
    async with SessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

async def create_tables():
    """Create database tables"""
    global engine
    if not engine:
        raise RuntimeError("Database engine not initialized")
    
    # Import all models to ensure they're registered
    from ..auth.models import User, APIKey, Subscription, UsageLog
    from .models import (
        PanchangCalculation, MuhurtaCalculation, FestivalCalendar,
        AyanamshaComparison, ApiUsageLog, CacheStatistics
    )
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    print("✅ Database tables created/updated")

# Health check function
async def check_database_health() -> dict:
    """Check database connection health"""
    if not engine:
        return {"status": "disconnected", "error": "Database not initialized"}
    
    try:
        async with engine.begin() as conn:
            result = await conn.execute(text("SELECT 1 as health_check"))
            row = result.fetchone()
            
            if row and row[0] == 1:
                return {
                    "status": "healthy",
                    "connection": "active",
                    "pool_size": engine.pool.size(),
                    "checked_out": engine.pool.checkedout()
                }
            else:
                return {"status": "unhealthy", "error": "Invalid response"}
                
    except Exception as e:
        return {"status": "error", "error": str(e)} 