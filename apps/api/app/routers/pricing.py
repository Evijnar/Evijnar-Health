# apps/api/app/routers/pricing.py
"""Procedure pricing and price normalization endpoints"""

from fastapi import APIRouter

from app.services.demo_catalog import (
    get_hospital_procedures as demo_get_hospital_procedures,
    get_normalization,
    search_hospitals as demo_search_hospitals,
)

router = APIRouter()

@router.get("/normalize/{cpt_code}")
async def normalize_price(cpt_code: str):
    """Normalize CPT code to ICD-10 and UHI standards"""
    mapping = get_normalization(cpt_code)
    return {
        "cpt_code": cpt_code,
        "mappings": mapping,
    }

@router.get("/hospital/{hospital_id}/procedures")
async def get_hospital_procedures(hospital_id: str):
    """Get all procedures and prices for a hospital"""
    procedures = demo_get_hospital_procedures(hospital_id)
    return {
        "hospital_id": hospital_id,
        "count": len(procedures),
        "procedures": procedures,
    }

@router.get("/compare")
async def compare_prices(procedure_code: str, countries: list[str] = None):
    """Compare prices across hospitals (Success-Adjusted Value ranking)"""
    comparable = demo_search_hospitals(procedure_code, countries=countries)
    return {
        "procedure_code": procedure_code,
        "count": len(comparable),
        "comparable": comparable,
    }
