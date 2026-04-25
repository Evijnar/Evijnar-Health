# apps/api/app/routers/financing.py
"""Rural financing and Health-EMI endpoints"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.demo_catalog import (
    FINANCING_RECORDS,
    create_financing_plan,
    get_financing_record,
    record_financing_payment,
)

router = APIRouter()

class CreateFinancingRequest(BaseModel):
    booking_id: str
    financing_type: str  # UPI_MICRO_LOAN | HEALTH_EMI | SUBSIDY_GRANT
    amount: float
    currency_code: str
    tenure_months: int

@router.post("/")
async def create_financing(request: CreateFinancingRequest):
    """Create financing for hospital procedure"""
    record = create_financing_plan(request.model_dump())
    return {
        "status": "success",
        "data": record,
    }

@router.get("/{financing_id}")
async def get_financing(financing_id: str):
    """Get financing details and EMI schedule"""
    record = get_financing_record(financing_id)
    return {
        "status": "success",
        "data": record,
    }

@router.post("/{financing_id}/payment")
async def record_payment(financing_id: str):
    """Record payment (from UPI or bank transfer)"""
    if financing_id not in FINANCING_RECORDS:
        raise HTTPException(status_code=404, detail="Financing record not found")

    return {
        "status": "success",
        "data": record_financing_payment(financing_id),
    }

@router.get("/{financing_id}/emi-schedule")
async def get_emi_schedule(financing_id: str):
    """Get EMI payment schedule"""
    record = get_financing_record(financing_id)
    return {
        "financing_id": financing_id,
        "emi_schedule": record.get("emi_schedule", []),
        "monthly_payment": record.get("monthly_payment"),
        "total_payable": record.get("total_payable"),
    }
