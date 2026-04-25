# apps/api/app/routers/bookings.py
"""Hospital booking and reservation endpoints"""

from datetime import datetime, timedelta

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.demo_catalog import BOOKINGS, build_booking_summary, ensure_booking, get_hospital, get_normalization, _now_iso, _uuid

router = APIRouter()

class CreateBookingRequest(BaseModel):
    hospital_id: str
    procedure_code: str
    scheduled_date: str  # ISO format

@router.post("/")
async def create_booking(request: CreateBookingRequest):
    """Create a new hospital booking"""
    hospital = get_hospital(request.hospital_id)
    if not hospital:
        raise HTTPException(status_code=404, detail="Hospital not found")

    normalization = get_normalization(request.procedure_code)
    hospital_procedure = next(
        (procedure for procedure in hospital.get("procedures", []) if procedure["code"] == request.procedure_code),
        None,
    )

    booking_id = f"book-{_uuid()}"
    scheduled_date = request.scheduled_date
    if "T" not in scheduled_date:
        scheduled_date = f"{scheduled_date}T09:00:00"

    booking = {
        "booking_id": booking_id,
        "hospital_id": request.hospital_id,
        "procedure_code": request.procedure_code,
        "scheduled_date": scheduled_date,
        "status": "CONFIRMED" if hospital_procedure else "INQUIRY",
        "estimated_total_usd": hospital_procedure["estimated_total_usd"] if hospital_procedure else normalization["us_median_cost_usd"],
        "value_score": 90.0 if hospital_procedure else 75.0,
        "created_at": _now_iso(),
        "updated_at": _now_iso(),
        "cancelled_at": None,
    }
    BOOKINGS[booking_id] = booking

    if hospital_procedure:
        booking["cost_breakdown"] = {
            "base_price": hospital_procedure["base_price"],
            "facility_fee": hospital_procedure["facility_fee"],
            "anesthesia_fee": hospital_procedure["anesthesia_fee"],
            "surgeon_fee": hospital_procedure["surgeon_fee"],
        }

    return {
        "status": "success",
        "data": build_booking_summary(booking),
    }

@router.get("/{booking_id}")
async def get_booking(booking_id: str):
    """Get booking details"""
    booking = BOOKINGS.get(booking_id) or ensure_booking(booking_id)
    return {
        "status": "success",
        "data": build_booking_summary(booking),
    }

@router.put("/{booking_id}/cancel")
async def cancel_booking(booking_id: str):
    """Cancel booking"""
    booking = BOOKINGS.get(booking_id) or ensure_booking(booking_id)
    booking["status"] = "CANCELLED"
    booking["cancelled_at"] = _now_iso()
    booking["updated_at"] = _now_iso()
    BOOKINGS[booking_id] = booking

    return {
        "status": "success",
        "data": build_booking_summary(booking),
    }
