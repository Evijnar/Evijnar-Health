# apps/api/app/routers/hospitals.py
"""Hospital search and details endpoints"""

from typing import Optional

from fastapi import APIRouter, Query

from app.services.demo_catalog import (
    get_departments as demo_get_departments,
    get_hospital as demo_get_hospital,
    search_hospitals as demo_search_hospitals,
)

router = APIRouter()

@router.get("/search")
async def search_hospitals(
    procedure_code: str = Query(...),
    country: Optional[str] = None,
    latitude: Optional[float] = None,
    longitude: Optional[float] = None,
    radius_km: Optional[int] = 500,
):
    """Search hospitals by procedure and location"""
    countries = [country] if country else None
    hospitals = demo_search_hospitals(procedure_code, countries=countries)

    if latitude is not None and longitude is not None:
        for hospital in hospitals:
            hospital["search_context"] = {
                "latitude": latitude,
                "longitude": longitude,
                "radius_km": radius_km,
            }

    return {
        "procedure_code": procedure_code,
        "count": len(hospitals),
        "hospitals": hospitals,
    }

@router.get("/{hospital_id}")
async def get_hospital(hospital_id: str):
    """Get hospital details including accreditation and departments"""
    hospital = demo_get_hospital(hospital_id)
    if not hospital:
        return {
            "hospital_id": hospital_id,
            "found": False,
            "departments": [],
        }

    return {
        "found": True,
        "hospital": hospital,
        "departments": demo_get_departments(hospital_id),
    }

@router.get("/{hospital_id}/departments")
async def get_departments(hospital_id: str):
    """Get hospital departments"""
    return {
        "hospital_id": hospital_id,
        "departments": demo_get_departments(hospital_id),
    }
