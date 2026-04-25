# apps/api/app/routers/patients.py
"""Patient profile and medical records endpoints"""

from typing import Optional

from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.services.demo_catalog import get_patient_profile, _now_iso

router = APIRouter()


class UpdatePatientRequest(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    country_code: Optional[str] = Field(default=None, min_length=2, max_length=2)
    state_province: Optional[str] = None
    rural_tier: Optional[str] = None
    consent_given: Optional[bool] = None

@router.get("/{patient_id}")
async def get_patient(patient_id: str):
    """Get patient profile (private)"""
    return {
        "status": "success",
        "data": get_patient_profile(patient_id),
    }

@router.put("/{patient_id}")
async def update_patient(patient_id: str, request: UpdatePatientRequest):
    """Update patient profile"""
    profile = get_patient_profile(patient_id)
    updates = request.model_dump(exclude_none=True)
    profile.update(updates)
    profile["updated_at"] = _now_iso()
    return {
        "status": "success",
        "data": profile,
    }

@router.get("/{patient_id}/records")
async def get_medical_records(patient_id: str):
    """Get patient medical records"""
    profile = get_patient_profile(patient_id)
    return {
        "status": "success",
        "patient_id": patient_id,
        "records": profile.get("records", []),
    }
