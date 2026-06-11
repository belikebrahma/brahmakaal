#!/usr/bin/env python3
"""Production entry point with multiple workers and proper timeout."""
import os
import multiprocessing
import uvicorn

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8888))
    host = os.environ.get("HOST", "0.0.0.0")
    # Use 2 workers on ARM (or more on x86) to avoid blocking
    workers = int(os.environ.get("UVICORN_WORKERS", max(2, multiprocessing.cpu_count() // 2)))

    uvicorn.run(
        "kaal_engine.api.app:app",
        host=host,
        port=port,
        workers=workers,
        reload=False,
        log_level="info",
        timeout_keep_alive=120,
    )
