"""Dashboard overview endpoints for the product shell."""

from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter

from app.config import settings
from app.services import demo_catalog

router = APIRouter()


def _build_top_hospitals() -> list[dict[str, object]]:
    results = demo_catalog.search_hospitals("33533")[:3]
    return [
        {
            "id": item["hospital_id"],
            "name": item["hospital_name"],
            "country": item["country_code"],
            "city": item["city"],
            "price": item["price"],
            "success_rate": item["success_rate"],
            "complication_rate": item["complication_rate"],
            "score": item["value_score"],
            "savings_usd": item["estimated_savings_usd"],
        }
        for item in results
    ]


@router.get("/overview")
async def dashboard_overview() -> dict[str, object]:
    """High-signal dashboard payload for the web shell."""
    top_hospitals = _build_top_hospitals()
    return {
        "status": "success",
        "timestamp": datetime.utcnow().isoformat(),
        "service": settings.app_name,
        "connected": True,
        "backend": {
            "health": "healthy",
            "ready": True,
            "database": "demo-connected",
        },
        "market": {
            "live_procedure": "33533",
            "country_spread": ["US", "DE", "IN"],
            "arbitrage_opportunity_usd": 46100,
        },
        "top_hospitals": top_hospitals,
        "alerts": {
            "recovery_mode": "demo",
            "critical_active": 0,
        },
    }
