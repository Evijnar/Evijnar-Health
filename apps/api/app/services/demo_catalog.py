"""Shared demo data for the product-facing API endpoints.

The application already has a real database-backed ingestion and auth layer.
These helpers provide coherent working responses for the customer-facing
feature routes so the site can demonstrate end-to-end behavior even before
all production integrations are connected.
"""

from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timedelta
from typing import Any
from uuid import uuid4


def _now_iso() -> str:
    return datetime.utcnow().isoformat()


def _uuid() -> str:
    return str(uuid4())


PROCEDURE_NORMALIZATIONS: dict[str, dict[str, Any]] = {
    "27447": {
        "cpt_code": "27447",
        "cpt_description": "Arthroplasty, knee, condyle and plateau; medial and lateral compartments with or without patella resurfacing",
        "icd10_code": "M17.11",
        "icd10_description": "Unilateral primary osteoarthritis, right knee",
        "uhi_code": "UHI-KNEE-ARTHRO",
        "ehds_identifier": "EHDS-ORTHO-27447",
        "clinical_category": "Orthopedics",
        "complexity_score": 4,
        "us_median_cost_usd": 45200.0,
    },
    "47562": {
        "cpt_code": "47562",
        "cpt_description": "Laparoscopy, surgical; cholecystectomy",
        "icd10_code": "K80.20",
        "icd10_description": "Calculus of gallbladder without cholecystitis",
        "uhi_code": "UHI-GALLBLADDER-47562",
        "ehds_identifier": "EHDS-GI-47562",
        "clinical_category": "General Surgery",
        "complexity_score": 3,
        "us_median_cost_usd": 18950.0,
    },
    "58571": {
        "cpt_code": "58571",
        "cpt_description": "Laparoscopy, surgical, total hysterectomy, for uterus 250 g or less",
        "icd10_code": "D25.9",
        "icd10_description": "Leiomyoma of uterus, unspecified",
        "uhi_code": "UHI-HYST-58571",
        "ehds_identifier": "EHDS-GYN-58571",
        "clinical_category": "Gynecology",
        "complexity_score": 4,
        "us_median_cost_usd": 27800.0,
    },
}

HOSPITALS: list[dict[str, Any]] = [
    {
        "id": "hosp-mayo-rochester",
        "source_id": "HHS-HOSP-001",
        "name": "Mayo Clinic Rochester",
        "country_code": "US",
        "state_province": "MN",
        "city": "Rochester",
        "latitude": 44.0225,
        "longitude": -92.4666,
        "postal_code": "55905",
        "phone_primary": "+1-507-284-2511",
        "email": "info@mayo.edu",
        "website_url": "https://www.mayoclinic.org",
        "hospital_type": "SPECIALTY_CENTER",
        "jci_accredited": True,
        "nabh_accredited": False,
        "price_data_source": "HHS_TRANSPARENCY",
        "avg_quality_score": 95.5,
        "complication_rate": 2.1,
        "readmission_rate": 4.0,
        "patient_reviews_count": 1840,
        "departments": [
            {"name": "Orthopedics", "specialization_code": "ORT", "head_name": "Dr. Elena Parker", "phone": "+1-507-555-1101"},
            {"name": "Cardiology", "specialization_code": "CAR", "head_name": "Dr. Martin Lee", "phone": "+1-507-555-1201"},
        ],
        "procedures": [
            {
                "code": "27447",
                "description": "Total knee replacement with prosthesis",
                "base_price": 44500.0,
                "facility_fee": 6200.0,
                "anesthesia_fee": 1300.0,
                "surgeon_fee": 5400.0,
                "currency_code": "USD",
                "success_rate": 96.8,
                "complication_rate": 2.1,
                "estimated_total_usd": 57400.0,
            },
            {
                "code": "47562",
                "description": "Laparoscopic cholecystectomy",
                "base_price": 18150.0,
                "facility_fee": 2200.0,
                "anesthesia_fee": 950.0,
                "surgeon_fee": 3100.0,
                "currency_code": "USD",
                "success_rate": 97.9,
                "complication_rate": 1.7,
                "estimated_total_usd": 24400.0,
            },
        ],
    },
    {
        "id": "hosp-apollo-delhi",
        "source_id": "ABDM-HOSP-100",
        "name": "Apollo Hospitals, Delhi",
        "country_code": "IN",
        "state_province": "Delhi",
        "city": "New Delhi",
        "latitude": 28.5672,
        "longitude": 77.2100,
        "postal_code": "110076",
        "phone_primary": "+91-11-2658-8500",
        "email": "contact@apollohospitals.com",
        "website_url": "https://www.apollohospitals.com",
        "hospital_type": "SPECIALTY_CENTER",
        "jci_accredited": True,
        "nabh_accredited": True,
        "price_data_source": "ABDM",
        "avg_quality_score": 98.4,
        "complication_rate": 1.2,
        "readmission_rate": 2.8,
        "patient_reviews_count": 2640,
        "departments": [
            {"name": "Orthopedics", "specialization_code": "ORT", "head_name": "Dr. Rajesh Kumar", "phone": "+91-11-5555-0101"},
            {"name": "Oncology", "specialization_code": "ONC", "head_name": "Dr. Meera Shah", "phone": "+91-11-5555-0102"},
        ],
        "procedures": [
            {
                "code": "27447",
                "description": "Total knee replacement with prosthesis",
                "base_price": 8500.0,
                "facility_fee": 1100.0,
                "anesthesia_fee": 500.0,
                "surgeon_fee": 1200.0,
                "currency_code": "USD",
                "success_rate": 98.7,
                "complication_rate": 1.3,
                "estimated_total_usd": 11300.0,
            },
            {
                "code": "58571",
                "description": "Total laparoscopic hysterectomy",
                "base_price": 6900.0,
                "facility_fee": 950.0,
                "anesthesia_fee": 460.0,
                "surgeon_fee": 900.0,
                "currency_code": "USD",
                "success_rate": 99.0,
                "complication_rate": 0.9,
                "estimated_total_usd": 9210.0,
            },
        ],
    },
    {
        "id": "hosp-charite-berlin",
        "source_id": "EHDS-HOSP-042",
        "name": "Charite University Hospital",
        "country_code": "DE",
        "state_province": "Berlin",
        "city": "Berlin",
        "latitude": 52.5317,
        "longitude": 13.3780,
        "postal_code": "10117",
        "phone_primary": "+49-30-450-50",
        "email": "info@charite.de",
        "website_url": "https://www.charite.de",
        "hospital_type": "GENERAL_HOSPITAL",
        "jci_accredited": True,
        "nabh_accredited": False,
        "price_data_source": "EHDS",
        "avg_quality_score": 97.1,
        "complication_rate": 1.5,
        "readmission_rate": 3.1,
        "patient_reviews_count": 1210,
        "departments": [
            {"name": "Orthopedics", "specialization_code": "ORT", "head_name": "Dr. Lars Becker", "phone": "+49-30-555-0101"},
            {"name": "Digestive Surgery", "specialization_code": "GI", "head_name": "Dr. Nina Hofmann", "phone": "+49-30-555-0102"},
        ],
        "procedures": [
            {
                "code": "27447",
                "description": "Total knee replacement with prosthesis",
                "base_price": 16200.0,
                "facility_fee": 2100.0,
                "anesthesia_fee": 700.0,
                "surgeon_fee": 2600.0,
                "currency_code": "USD",
                "success_rate": 97.8,
                "complication_rate": 1.5,
                "estimated_total_usd": 21600.0,
            },
            {
                "code": "47562",
                "description": "Laparoscopic cholecystectomy",
                "base_price": 9450.0,
                "facility_fee": 1400.0,
                "anesthesia_fee": 620.0,
                "surgeon_fee": 1600.0,
                "currency_code": "USD",
                "success_rate": 98.1,
                "complication_rate": 1.4,
                "estimated_total_usd": 13070.0,
            },
        ],
    },
]

PATIENT_PROFILES: dict[str, dict[str, Any]] = {}
BOOKINGS: dict[str, dict[str, Any]] = {}
RECOVERY_SESSIONS: dict[str, dict[str, Any]] = {}
RECOVERY_ALERTS: dict[str, list[dict[str, Any]]] = {}
FINANCING_RECORDS: dict[str, dict[str, Any]] = {}


def get_normalization(cpt_code: str) -> dict[str, Any]:
    data = deepcopy(PROCEDURE_NORMALIZATIONS.get(cpt_code, {}))
    if data:
        return data

    return {
        "cpt_code": cpt_code,
        "cpt_description": "Unmapped procedure code",
        "icd10_code": "Z00.00",
        "icd10_description": "General examination without complaint",
        "uhi_code": f"UHI-{cpt_code}",
        "ehds_identifier": f"EHDS-{cpt_code}",
        "clinical_category": "Unmapped",
        "complexity_score": 1,
        "us_median_cost_usd": 1000.0,
    }


def get_hospital(hospital_id: str) -> dict[str, Any] | None:
    for hospital in HOSPITALS:
        if hospital["id"] == hospital_id:
            return deepcopy(hospital)
    return None


def get_hospital_by_source_id(source_id: str) -> dict[str, Any] | None:
    for hospital in HOSPITALS:
        if hospital["source_id"] == source_id:
            return deepcopy(hospital)
    return None


def get_hospital_procedures(hospital_id: str) -> list[dict[str, Any]]:
    hospital = get_hospital(hospital_id)
    if not hospital:
        return []
    return [deepcopy(item) for item in hospital.get("procedures", [])]


def get_departments(hospital_id: str) -> list[dict[str, Any]]:
    hospital = get_hospital(hospital_id)
    if not hospital:
        return []
    return [deepcopy(item) for item in hospital.get("departments", [])]


def search_hospitals(procedure_code: str, countries: list[str] | None = None) -> list[dict[str, Any]]:
    countries = [country.upper() for country in (countries or [])]
    normalization = get_normalization(procedure_code)
    comparable: list[dict[str, Any]] = []

    for hospital in HOSPITALS:
        if countries and hospital["country_code"] not in countries:
            continue

        for procedure in hospital.get("procedures", []):
            if procedure["code"] != procedure_code:
                continue

            estimated_savings = round(max(normalization["us_median_cost_usd"] - procedure["base_price"], 0), 2)
            price_ratio = procedure["base_price"] / max(normalization["us_median_cost_usd"], 1)
            value_score = round((procedure["success_rate"] / max(price_ratio, 0.01)) - (procedure["complication_rate"] * 10), 2)

            comparable.append(
                {
                    "hospital_id": hospital["id"],
                    "hospital_name": hospital["name"],
                    "country_code": hospital["country_code"],
                    "city": hospital["city"],
                    "state_province": hospital["state_province"],
                    "jci_accredited": hospital["jci_accredited"],
                    "nabh_accredited": hospital["nabh_accredited"],
                    "price": procedure["base_price"],
                    "currency_code": procedure["currency_code"],
                    "success_rate": procedure["success_rate"],
                    "complication_rate": procedure["complication_rate"],
                    "estimated_savings_usd": estimated_savings,
                    "value_score": value_score,
                    "clinical_category": normalization["clinical_category"],
                    "complexity_score": normalization["complexity_score"],
                }
            )

    comparable.sort(key=lambda item: item["value_score"], reverse=True)
    return comparable


def build_booking_summary(booking: dict[str, Any]) -> dict[str, Any]:
    return {
        "booking_id": booking["booking_id"],
        "hospital_id": booking["hospital_id"],
        "procedure_code": booking["procedure_code"],
        "scheduled_date": booking["scheduled_date"],
        "status": booking["status"],
        "estimated_total_usd": booking["estimated_total_usd"],
        "value_score": booking["value_score"],
        "created_at": booking["created_at"],
        "updated_at": booking["updated_at"],
        "cancelled_at": booking.get("cancelled_at"),
    }


def ensure_booking(booking_id: str) -> dict[str, Any]:
    if booking_id in BOOKINGS:
        return BOOKINGS[booking_id]

    default = {
        "booking_id": booking_id,
        "hospital_id": HOSPITALS[1]["id"],
        "procedure_code": "27447",
        "scheduled_date": (datetime.utcnow() + timedelta(days=21)).isoformat(),
        "status": "CONFIRMED",
        "estimated_total_usd": 11300.0,
        "value_score": 91.7,
        "created_at": _now_iso(),
        "updated_at": _now_iso(),
        "cancelled_at": None,
    }
    BOOKINGS[booking_id] = default
    return default


def get_patient_profile(patient_id: str) -> dict[str, Any]:
    if patient_id in PATIENT_PROFILES:
        return deepcopy(PATIENT_PROFILES[patient_id])

    profile = {
        "patient_id": patient_id,
        "country_code": "IN",
        "state_province": "Karnataka",
        "rural_tier": "TIER_2",
        "consent_given": True,
        "age_approximated": 48,
        "blood_group": "O+",
        "records": [
            {
                "id": _uuid(),
                "record_date": (datetime.utcnow() - timedelta(days=19)).isoformat(),
                "diagnosis": "Knee osteoarthritis",
                "procedure": "Total knee replacement planning",
            }
        ],
    }
    PATIENT_PROFILES[patient_id] = profile
    return deepcopy(profile)


def get_recovery_session_state(booking_id: str) -> dict[str, Any]:
    if booking_id in RECOVERY_SESSIONS:
        return RECOVERY_SESSIONS[booking_id]

    session_id = f"rec-{booking_id}"
    session = {
        "session_id": session_id,
        "booking_id": booking_id,
        "status": "ACTIVE",
        "surgeon_name": "Dr. Rajesh Kumar",
        "hospital_name": "Apollo Hospitals, Delhi",
        "start_date": _now_iso(),
        "end_date": (datetime.utcnow() + timedelta(days=30)).isoformat(),
        "alert_count": 0,
        "critical_alert_count": 0,
        "latest_vitals": {
            "heart_rate": 74,
            "blood_oxygen_spo2": 98,
            "temperature_celsius": 37.1,
            "systolic_bp": 122,
            "diastolic_bp": 80,
            "respiratory_rate": 16,
        },
    }
    RECOVERY_SESSIONS[booking_id] = session
    RECOVERY_ALERTS[session_id] = [
        {
            "alert_id": _uuid(),
            "severity": "INFO",
            "message": "Routine post-op monitoring started.",
            "acknowledged": False,
            "created_at": _now_iso(),
        }
    ]
    return session


def evaluate_vitals(vital_data: dict[str, Any], session_id: str | None = None) -> dict[str, Any]:
    alerts: list[dict[str, Any]] = []
    severity = "INFO"

    if vital_data["blood_oxygen_spo2"] < 94:
        severity = "CRITICAL"
        alerts.append({"field": "blood_oxygen_spo2", "message": "SpO2 below safe threshold", "severity": severity})
    if vital_data["temperature_celsius"] >= 38.0:
        severity = "WARNING" if severity == "INFO" else severity
        alerts.append({"field": "temperature_celsius", "message": "Temperature elevated", "severity": "WARNING"})
    if vital_data["systolic_bp"] >= 145 or vital_data["systolic_bp"] <= 90:
        severity = "WARNING" if severity == "INFO" else severity
        alerts.append({"field": "systolic_bp", "message": "Blood pressure outside expected range", "severity": "WARNING"})
    if vital_data["heart_rate"] >= 110 or vital_data["heart_rate"] <= 55:
        severity = "WARNING" if severity == "INFO" else severity
        alerts.append({"field": "heart_rate", "message": "Heart rate outside expected range", "severity": "WARNING"})
    if vital_data["respiratory_rate"] >= 24 or vital_data["respiratory_rate"] <= 10:
        severity = "WARNING" if severity == "INFO" else severity
        alerts.append({"field": "respiratory_rate", "message": "Respiratory rate outside expected range", "severity": "WARNING"})

    if session_id:
        RECOVERY_ALERTS.setdefault(session_id, [])
        for alert in alerts:
            RECOVERY_ALERTS[session_id].append(
                {
                    "alert_id": _uuid(),
                    "severity": alert["severity"],
                    "message": alert["message"],
                    "field": alert["field"],
                    "acknowledged": False,
                    "created_at": _now_iso(),
                }
            )

    return {
        "severity": severity,
        "alert_triggered": bool(alerts),
        "alerts": alerts,
        "recommendation": "Continue monitoring" if not alerts else "Notify the care team and review the vitals",
    }


def create_financing_plan(request: dict[str, Any]) -> dict[str, Any]:
    financing_id = f"fin-{_uuid()}"
    annual_rate = {
        "UPI_MICRO_LOAN": 0.12,
        "HEALTH_EMI": 0.0,
        "SUBSIDY_GRANT": 0.0,
    }.get(request["financing_type"], 0.14)

    tenure_months = max(int(request["tenure_months"]), 1)
    principal = float(request["amount"])
    monthly_rate = annual_rate / 12

    if monthly_rate == 0:
        monthly_payment = principal / tenure_months
    else:
        monthly_payment = principal * monthly_rate / (1 - (1 + monthly_rate) ** (-tenure_months))

    schedule: list[dict[str, Any]] = []
    remaining = principal
    due_date = datetime.utcnow()
    for month in range(1, tenure_months + 1):
        due_date = due_date + timedelta(days=30)
        interest = remaining * monthly_rate
        principal_component = monthly_payment - interest
        remaining = max(remaining - principal_component, 0)
        schedule.append(
            {
                "installment": month,
                "due_date": due_date.date().isoformat(),
                "payment_amount": round(monthly_payment, 2),
                "principal_component": round(principal_component, 2),
                "interest_component": round(interest, 2),
                "remaining_balance": round(remaining, 2),
            }
        )

    record = {
        "financing_id": financing_id,
        "booking_id": request["booking_id"],
        "financing_type": request["financing_type"],
        "amount": principal,
        "currency_code": request["currency_code"],
        "tenure_months": tenure_months,
        "annual_rate": annual_rate,
        "monthly_payment": round(monthly_payment, 2),
        "total_payable": round(monthly_payment * tenure_months, 2),
        "status": "PENDING",
        "created_at": _now_iso(),
        "emi_schedule": schedule,
        "payments": [],
    }
    FINANCING_RECORDS[financing_id] = record
    return deepcopy(record)


def get_financing_record(financing_id: str) -> dict[str, Any]:
    if financing_id in FINANCING_RECORDS:
        return deepcopy(FINANCING_RECORDS[financing_id])

    booking = ensure_booking("booking-default")
    record = create_financing_plan(
        {
            "booking_id": booking["booking_id"],
            "financing_type": "HEALTH_EMI",
            "amount": booking["estimated_total_usd"],
            "currency_code": "USD",
            "tenure_months": 12,
        }
    )
    record["financing_id"] = financing_id
    FINANCING_RECORDS[financing_id] = record
    return deepcopy(record)


def record_financing_payment(financing_id: str) -> dict[str, Any]:
    record = get_financing_record(financing_id)
    payment = {
        "payment_id": _uuid(),
        "paid_at": _now_iso(),
        "amount": record["monthly_payment"],
        "status": "RECORDED",
    }
    record.setdefault("payments", []).append(payment)
    record["status"] = "PAYING"
    FINANCING_RECORDS[financing_id] = record
    return {"financing_id": financing_id, "payment_recorded": True, "payment": payment, "status": record["status"]}


def acknowledge_recovery_alert(alert_id: str) -> dict[str, Any] | None:
    for session_id, alerts in RECOVERY_ALERTS.items():
        for alert in alerts:
            if alert["alert_id"] == alert_id:
                alert["acknowledged"] = True
                alert["acknowledged_at"] = _now_iso()
                return {
                    "session_id": session_id,
                    "alert_id": alert_id,
                    "acknowledged": True,
                    "acknowledged_at": alert["acknowledged_at"],
                }
    return None
