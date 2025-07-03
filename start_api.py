#!/usr/bin/env python3
"""
Brahmakaal Enterprise API Server Startup Script
Initializes database and starts the FastAPI application
"""

import os
import sys
import asyncio
import uvicorn
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from kaal_engine.db.database import init_database
from kaal_engine.config import get_settings

async def initialize_system():
    """Initialize database and other system components"""
    print("🚀 Starting Brahmakaal Enterprise API...")
    print("=" * 60)
    
    try:
        # Initialize database
        print("📊 Initializing database...")
        await init_database()
        print("✅ Database initialized successfully")
        
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        # Continue anyway - some deployment environments handle DB separately
        print("⚠️ Continuing without database initialization...")

def main():
    """Main startup function"""
    settings = get_settings()
    
    # Get port from environment or default
    port = int(os.environ.get("PORT", 8000))
    host = os.environ.get("HOST", "0.0.0.0")
    
    print(f"\n🌟 Configuration:")
    print(f"   Host: {host}")
    print(f"   Port: {port}")
    print(f"   Environment: {settings.environment}")
    print(f"   Email enabled: {settings.email_enabled}")
    print(f"   Webhook enabled: {settings.webhook_enabled}")
    
    # Initialize system
    try:
        asyncio.run(initialize_system())
    except Exception as e:
        print(f"⚠️ System initialization warning: {e}")
    
    print(f"\n🎯 API Documentation:")
    print(f"   Swagger UI: http://{host}:{port}/docs")
    print(f"   ReDoc: http://{host}:{port}/redoc")
    print(f"   Health Check: http://{host}:{port}/v1/health")
    
    print(f"\n🔑 Use your never-expiring token for testing:")
    try:
        with open("never_expiring_token.txt", "r") as f:
            token = f.read().strip()
            print(f"   Authorization: Bearer {token}")
    except:
        print("   Run: python generate_test_token.py")
    
    print(f"\n🚀 Starting server on {host}:{port}...")
    print("=" * 60)
    
    # Start the server
    uvicorn.run(
        "kaal_engine.api.app:app",
        host=host,
        port=port,
        reload=False,
        log_level="info",
        access_log=True
    )

if __name__ == "__main__":
    main()
