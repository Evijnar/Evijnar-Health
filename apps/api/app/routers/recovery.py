# apps/api/app/routers/recovery.py
"""Recovery Bridge 30-day IoMT monitoring endpoints"""

from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.demo_catalog import (
    RECOVERY_ALERTS,
    acknowledge_recovery_alert,
    evaluate_vitals,
    get_recovery_session_state,
    _now_iso,
    _uuid,
)

router = APIRouter()

class RecoveryVitalData(BaseModel):
    heart_rate: int
    blood_oxygen_spo2: int
    temperature_celsius: float
    systolic_bp: int
    diastolic_bp: int
    respiratory_rate: int

@router.get("/session/{booking_id}")
async def get_recovery_session(booking_id: str):
    """Get recovery session for a booking"""
    session = get_recovery_session_state(booking_id)
    return {
        "status": "success",
        "session": session,
        "alerts": RECOVERY_ALERTS.get(session["session_id"], []),
    }

@router.post("/vitals")
async def post_vitals(vital_data: RecoveryVitalData, booking_id: Optional[str] = None, session_id: Optional[str] = None):
    """Submit IoMT vital signs from wearable devices"""
    active_booking_id = booking_id or "booking-demo"
    session = get_recovery_session_state(active_booking_id)
    active_session_id = session_id or session["session_id"]
    evaluation = evaluate_vitals(vital_data.model_dump(), active_session_id)

    session["latest_vitals"] = vital_data.model_dump()
    session["status"] = "ESCALATED" if evaluation["severity"] == "CRITICAL" else session["status"]
    session["alert_count"] = len(RECOVERY_ALERTS.get(active_session_id, []))
    session["critical_alert_count"] = sum(
        1 for alert in RECOVERY_ALERTS.get(active_session_id, []) if alert["severity"] == "CRITICAL"
    )

    return {
        "received": True,
        "session_id": active_session_id,
        "status": session["status"],
        "evaluation": evaluation,
        "latest_vitals": session["latest_vitals"],
    }

@router.get("/session/{session_id}/alerts")
async def get_recovery_alerts(session_id: str):
    """Get alerts for recovery session"""
    return {
        "session_id": session_id,
        "alerts": RECOVERY_ALERTS.get(session_id, []),
    }

@router.post("/alerts/{alert_id}/acknowledge")
async def acknowledge_alert(alert_id: str):
    """Acknowledge alert (surgeon/provider)"""
    result = acknowledge_recovery_alert(alert_id)
    if not result:
        raise HTTPException(status_code=404, detail="Alert not found")
    return result
