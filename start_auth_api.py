#!/usr/bin/env python3
"""
Brahmakaal Enterprise API Startup Script
Starts the API server with authentication and security features
"""

import uvicorn
import asyncio
import os
import sys

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from kaal_engine.config import get_settings

def main():
    """Start the Brahmakaal Enterprise API server with authentication"""
    
    # Get settings
    settings = get_settings()
    
    print("🚀 Starting Brahmakaal Enterprise API with Authentication...")
    print("=" * 60)
    print(f"📍 Environment: {settings.environment}")
    print(f"🔐 Security: JWT + API Keys + Rate Limiting")
    print(f"💾 Database: PostgreSQL")
    print(f"⚡ Cache: Redis ({'enabled' if settings.redis_enabled else 'disabled'})")
    print(f"📊 Analytics: {'enabled' if settings.analytics_enabled else 'disabled'}")
    print("=" * 60)
    print(f"🌐 Server will start at: http://localhost:8000")
    print(f"📚 API Documentation: http://localhost:8000/docs")
    print(f"🔑 Authentication endpoints: http://localhost:8000/v1/auth/")
    print()
    print("🎯 Quick Start:")
    print("1. Register: POST /v1/auth/register")
    print("2. Login: POST /v1/auth/login")
    print("3. Create API Key: POST /v1/auth/api-keys")
    print("4. Use with X-API-Key header or Authorization: Bearer <token>")
    print()
    print("=" * 60)
    
    # Start the server
    try:
        uvicorn.run(
            "kaal_engine.api.app:app",
            host="0.0.0.0",
            port=8000,  # Back to 8000 since we cleared the port
            reload=settings.debug,
            log_level=settings.log_level.lower(),
            access_log=True,
            workers=1,  # Single worker for development
            loop="auto"
        )
    except Exception as e:
        print(f"❌ Failed to start server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 