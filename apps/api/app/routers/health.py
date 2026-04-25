# apps/api/app/routers/health.py
"""Health check endpoint"""

from fastapi import APIRouter
from fastapi.responses import JSONResponse
from sqlalchemy import text

from app.db import get_session_factory
from app.config import settings

router = APIRouter()

@router.get("/health")
async def health_check():
    """Health check endpoint for load balancers and monitoring"""
    return {
        "status": "healthy",
        "service": "Evijnar API",
        "version": settings.app_version,
        "environment": settings.app_env,
    }

@router.get("/ready")
async def readiness_check():
    """Readiness check - returns 200 when API is ready to accept traffic"""
    try:
        session_factory = get_session_factory()
        async with session_factory() as session:
            await session.execute(text("SELECT 1"))

        return {"ready": True, "database": "connected"}
    except Exception as exc:
        return JSONResponse(
            status_code=503,
            content={"ready": False, "database": "unavailable", "detail": str(exc)},
        )
