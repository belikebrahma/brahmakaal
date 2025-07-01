"""
Brahmakaal Simple API Startup Script (No Database)
For testing core functionality without database dependencies
"""

import uvicorn
import sys
from kaal_engine.config import get_settings

def main():
    """Start the simplified Brahmakaal API server"""
    
    # Get settings
    settings = get_settings()
    
    print("🚀 Starting Brahmakaal Simple API (No Database Mode)...")
    print("=" * 60)
    print(f"📍 Environment: {settings.environment}")
    print(f"🔐 Security: DISABLED (testing mode)")
    print(f"💾 Database: DISABLED (testing mode)")
    print(f"⚡ Cache: DISABLED (testing mode)")
    print(f"📊 Analytics: DISABLED (testing mode)")
    print("=" * 60)
    print(f"🌐 Server will start at: http://localhost:8000")
    print(f"📚 API Documentation: http://localhost:8000/docs")
    print(f"🔍 Health Check: http://localhost:8000/v1/health")
    print()
    print("🎯 Available Features:")
    print("• Panchang calculations")
    print("• Muhurta analysis")
    print("• Festival calendar")
    print("• Ayanamsha calculations")
    print("• Vedic astronomy engine")
    print()
    print("=" * 60)
    
    # Start the server
    try:
        uvicorn.run(
            "kaal_engine.api.app_no_db:app",
            host="0.0.0.0",
            port=8000,
            reload=settings.debug,
            log_level=settings.log_level.lower(),
            access_log=True,
            workers=1,
            loop="auto"
        )
    except Exception as e:
        print(f"❌ Failed to start server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 