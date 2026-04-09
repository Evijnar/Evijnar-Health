#!/usr/bin/env python
# apps/api/run.py
"""
Development server entry point
Usage: python run.py
"""

import uvicorn
from app.config import settings

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug,
        log_level="info",
    )
