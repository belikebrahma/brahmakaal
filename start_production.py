#!/usr/bin/env python3
import os
import uvicorn
from kaal_engine.api.app import app

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    host = os.environ.get("HOST", "0.0.0.0")
    
    uvicorn.run(
        "kaal_engine.api.app:app",
        host=host,
        port=port,
        reload=False,
        log_level="info"
    )
