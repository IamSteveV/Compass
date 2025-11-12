#!/usr/bin/env python3
"""
Architecture Validation Web Application

Run this file to start the web server.
"""

import uvicorn
from src.config import get_settings

if __name__ == "__main__":
    settings = get_settings()

    uvicorn.run(
        "src.api.main:app",
        host="0.0.0.0",
        port=settings.app_port,
        reload=settings.app_debug,
        log_level="info"
    )
