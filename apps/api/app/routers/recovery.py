"""Recovery Bridge endpoints: IoMT vitals ingestion and alerting."""

from __future__ import annotations

from typing import Optional, List
from datetime import datetime, timezone
import logging

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db import get_session
from app.dependencies.auth import get_current_user
from app.repositories.audit import AuditRepository
from app.models import (
    RecoverySession,
    RecoveryVital,
    RecoveryAlert,
    AlertSeverity,
)
from app.utils.encryption import encrypt_data

logger = logging.getLogger("evijnar.recovery")

router = APIRouter()


class VitalsIngestRequest(BaseModel):
    recovery_session_id: str = Field(..., description="Recovery session UUID")
    device_id: str = Field(..., description="Device identifier (for idempotency)")
    collected_at: datetime = Field(..., description="ISO timestamp when measurement was taken")
    heart_rate: Optional[int] = None
    spo2: Optional[int] = None
    temperature_c: Optional[float] = None
    systolic_bp: Optional[int] = None
    diastolic_bp: Optional[int] = None
    respiratory_rate: Optional[int] = None
    symptom_notes: Optional[str] = None


class VitalsIngestResponse(BaseModel):
    vital_id: str
    created: bool
    alerts_created: int


class AlertResponse(BaseModel):
    id: str
    alert_type: str
    severity: AlertSeverity
    patient_value: Optional[str]
    normal_range: Optional[str]
    recommendation: Optional[str]
    acknowledged_at: Optional[datetime]
    action_taken: Optional[str]
    created_at: datetime


async def _notify_on_critical(alert_id: str) -> None:
    """Placeholder notification for critical alerts.

    In production this should call the configured webhook/SMS/phone layer.
    """
    logger.info("Notify critical alert: %s", alert_id)


@router.post("/vitals", response_model=VitalsIngestResponse)
async def ingest_vitals(
    payload: VitalsIngestRequest,
    background: BackgroundTasks,
    session: AsyncSession = Depends(get_session),
    current_user=Depends(get_current_user),
):
    """Ingest vitals from a wearable device.

    - Idempotent by (`device_id`, `collected_at`).
    - Creates `RecoveryVital` and per-threshold `RecoveryAlert` rows.
    - CRITICAL alerts trigger an async notification task and immediate escalation.
    """
    # Normalize timestamp to UTC
    collected_at = payload.collected_at.astimezone(timezone.utc).replace(tzinfo=None)

    # Verify session exists
    result = await session.execute(
        select(RecoverySession).where(RecoverySession.id == payload.recovery_session_id)
    )
    recovery_session = result.scalar_one_or_none()
    if not recovery_session:
        raise HTTPException(status_code=404, detail="Recovery session not found")

    # Idempotency check
    existing = await session.execute(
        select(RecoveryVital).where(
            RecoveryVital.device_id == payload.device_id,
            RecoveryVital.collected_at == collected_at,
            RecoveryVital.recovery_session_id == payload.recovery_session_id,
        )
    )
    existing_vital = existing.scalar_one_or_none()
    if existing_vital:
        # Audit the read (PHI access)
        try:
            audit = AuditRepository(session)
            await audit.log_action(
                user_id=current_user.id,
                action="VITALS_INGEST_IDEMPOTENT",
                resource_type="RecoveryVital",
                resource_id=existing_vital.id,
            )
        except Exception:
            logger.exception("Failed to write audit log for idempotent ingest")

        return VitalsIngestResponse(vital_id=existing_vital.id, created=False, alerts_created=0)

    # Create RecoveryVital
    vital = RecoveryVital(
        recovery_session_id=payload.recovery_session_id,
        heart_rate=payload.heart_rate,
        blood_oxygen_spo2=payload.spo2,
        temperature_celsius=payload.temperature_c,
        systolic_bp=payload.systolic_bp,
        diastolic_bp=payload.diastolic_bp,
        respiratory_rate=payload.respiratory_rate,
        device_id=payload.device_id,
        device_type=None,
        collected_at=collected_at,
    )

    # Encrypt symptom notes if present
    if payload.symptom_notes:
        try:
            vital.symptom_notes_encrypted = encrypt_data(payload.symptom_notes)
        except Exception:
            logger.exception("Failed to encrypt symptom notes; aborting ingest")
            raise HTTPException(status_code=500, detail="Encryption failure")

    session.add(vital)
    await session.flush()

    alerts_created = 0
    critical_found = False

    # Threshold checks
    def _make_alert(alert_type: str, severity: AlertSeverity, patient_value: str, normal_range: str, recommendation: str):
        nonlocal alerts_created, critical_found
        alert = RecoveryAlert(
            recovery_session_id=payload.recovery_session_id,
            vital_id=vital.id,
            alert_type=alert_type,
            severity=severity,
            patient_value=patient_value,
            normal_range=normal_range,
            recommendation=recommendation,
            created_at=datetime.utcnow(),
        )
        session.add(alert)
        alerts_created += 1
        if severity == AlertSeverity.CRITICAL:
            critical_found = True

    # Heart rate
    if payload.heart_rate is not None:
        if payload.heart_rate < 50 or payload.heart_rate > 120:
            _make_alert(
                "heart_rate",
                AlertSeverity.HIGH,
                str(payload.heart_rate),
                "50-120 bpm",
                "Contact care team if symptomatic",
            )

    # SpO2
    if payload.spo2 is not None and payload.spo2 < 92:
        _make_alert(
            "spo2",
            AlertSeverity.CRITICAL,
            str(payload.spo2),
            ">=92%",
            "Seek immediate medical attention; escalate",
        )

    # Temperature
    if payload.temperature_c is not None and payload.temperature_c > 38.5:
        _make_alert(
            "temperature_c",
            AlertSeverity.MEDIUM,
            str(payload.temperature_c),
            "<=38.5 C",
            "Monitor and take antipyretics; contact provider if persists",
        )

    # Systolic BP
    if payload.systolic_bp is not None and payload.systolic_bp > 160:
        _make_alert(
            "systolic_bp",
            AlertSeverity.HIGH,
            str(payload.systolic_bp),
            "<=160 mmHg",
            "Re-check and contact provider for urgent review",
        )

    # Persist alerts and update session counters
    await session.flush()

    if alerts_created:
        recovery_session.alert_count = (recovery_session.alert_count or 0) + alerts_created

    if critical_found:
        recovery_session.critical_alert_count = (recovery_session.critical_alert_count or 0) + 1
        recovery_session.has_escalated = True
        recovery_session.escalation_at = datetime.utcnow()

    await session.commit()

    # Background notification for critical alerts
    if critical_found:
        # find created critical alerts for this vital and enqueue notifications
        res = await session.execute(
            select(RecoveryAlert).where(RecoveryAlert.vital_id == vital.id, RecoveryAlert.severity == AlertSeverity.CRITICAL)
        )
        critical_alerts = res.scalars().all()
        for a in critical_alerts:
            background.add_task(_notify_on_critical, a.id)

    # Audit
    try:
        audit = AuditRepository(session)
        await audit.log_action(
            user_id=current_user.id,
            action="VITALS_INGEST",
            resource_type="RecoveryVital",
            resource_id=vital.id,
        )
    except Exception:
        logger.exception("Failed to write audit log for vitals ingest")

    return VitalsIngestResponse(vital_id=vital.id, created=True, alerts_created=alerts_created)


@router.get("/session/{booking_id}")
async def get_recovery_session_by_booking(
    booking_id: str,
    session: AsyncSession = Depends(get_session),
    current_user=Depends(get_current_user),
):
    """Return recovery session details by booking id (unique)."""
    res = await session.execute(select(RecoverySession).where(RecoverySession.booking_id == booking_id))
    recovery = res.scalar_one_or_none()
    if not recovery:
        raise HTTPException(status_code=404, detail="Recovery session not found")

    # Audit PHI read
    try:
        audit = AuditRepository(session)
        await audit.log_action(
            user_id=current_user.id,
            action="VITALS_READ",
            resource_type="RecoverySession",
            resource_id=recovery.id,
        )
    except Exception:
        logger.exception("Failed to write audit log for session read")

    # Minimal session payload
    return {
        "id": recovery.id,
        "booking_id": recovery.booking_id,
        "patient_id": recovery.patient_id,
        "start_date": recovery.start_date,
        "end_date": recovery.end_date,
        "recovery_status": recovery.recovery_status.value if recovery.recovery_status else None,
        "alert_count": recovery.alert_count,
        "critical_alert_count": recovery.critical_alert_count,
    }


@router.get("/session/{session_id}/alerts", response_model=List[AlertResponse])
async def list_session_alerts(
    session_id: str,
    session: AsyncSession = Depends(get_session),
    current_user=Depends(get_current_user),
):
    res = await session.execute(select(RecoveryAlert).where(RecoveryAlert.recovery_session_id == session_id).order_by(RecoveryAlert.created_at.desc()))
    alerts = res.scalars().all()

    # Audit
    try:
        audit = AuditRepository(session)
        await audit.log_action(
            user_id=current_user.id,
            action="ALERT_ACCESS",
            resource_type="RecoverySessionAlerts",
            resource_id=session_id,
        )
    except Exception:
        logger.exception("Failed to write audit log for alerts list")

    out: List[AlertResponse] = []
    for a in alerts:
        out.append(
            AlertResponse(
                id=a.id,
                alert_type=a.alert_type,
                severity=a.severity,
                patient_value=a.patient_value,
                normal_range=a.normal_range,
                recommendation=a.recommendation,
                acknowledged_at=a.acknowledged_at,
                action_taken=a.action_taken,
                created_at=a.created_at,
            )
        )

    return out


@router.post("/alerts/{alert_id}/acknowledge")
async def acknowledge_alert(
    alert_id: str,
    session: AsyncSession = Depends(get_session),
    current_user=Depends(get_current_user),
):
    res = await session.execute(select(RecoveryAlert).where(RecoveryAlert.id == alert_id))
    alert = res.scalar_one_or_none()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")

    alert.acknowledged_at = datetime.utcnow()
    alert.acknowledged_by_id = current_user.id
    alert.action_taken = (alert.action_taken or "") + ";ACKNOWLEDGED"
    await session.flush()
    await session.commit()

    # Audit
    try:
        audit = AuditRepository(session)
        await audit.log_action(
            user_id=current_user.id,
            action="ALERT_ACCESS",
            resource_type="RecoveryAlert",
            resource_id=alert_id,
        )
    except Exception:
        logger.exception("Failed to write audit log for alert acknowledge")

    return {"ok": True, "alert_id": alert_id, "acknowledged_at": alert.acknowledged_at}


@router.put("/alerts/{alert_id}/escalate")
async def escalate_alert(
    alert_id: str,
    background: BackgroundTasks,
    session: AsyncSession = Depends(get_session),
    current_user=Depends(get_current_user),
):
    res = await session.execute(select(RecoveryAlert).where(RecoveryAlert.id == alert_id))
    alert = res.scalar_one_or_none()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")

    # mark escalation
    alert.action_taken = (alert.action_taken or "") + ";ESCALATED"
    # mark session escalated
    rs = await session.execute(select(RecoverySession).where(RecoverySession.id == alert.recovery_session_id))
    recovery = rs.scalar_one_or_none()
    if recovery:
        recovery.has_escalated = True
        recovery.escalation_at = datetime.utcnow()

    await session.flush()
    await session.commit()

    # background notify
    background.add_task(_notify_on_critical, alert.id)

    # Audit
    try:
        audit = AuditRepository(session)
        await audit.log_action(
            user_id=current_user.id,
            action="ALERT_ESCALATE",
            resource_type="RecoveryAlert",
            resource_id=alert_id,
        )
    except Exception:
        logger.exception("Failed to write audit log for alert escalate")

    return {"ok": True, "alert_id": alert_id, "escalated": True}
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
