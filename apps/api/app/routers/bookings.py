# apps/api/app/routers/bookings.py
"""Hospital booking and reservation endpoints"""

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

class CreateBookingRequest(BaseModel):
    hospital_id: str
    procedure_code: str
    scheduled_date: str  # ISO format

@router.post("/")
async def create_booking(request: CreateBookingRequest):
    """Create a new hospital booking"""
    # TODO: Implement
    return {"booking_id": "123", "status": "INQUIRY"}

@router.get("/{booking_id}")
async def get_booking(booking_id: str):
    """Get booking details"""
    # TODO: Implement
    return {"booking_id": booking_id}

@router.put("/{booking_id}/cancel")
async def cancel_booking(booking_id: str):
    """Cancel booking"""
    # TODO: Implement
    return {"booking_id": booking_id, "status": "CANCELLED"}
