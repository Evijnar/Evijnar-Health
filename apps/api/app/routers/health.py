# apps/api/app/routers/health.py
"""Health check endpoint"""

from fastapi import APIRouter
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
    # TODO: Add database connectivity check
    return {"ready": True}
