# apps/api/app/models/database.py
"""
SQLAlchemy ORM models for Evijnar database.
Defines all tables and relationships for the global health arbitrage platform.
"""

from datetime import datetime, timedelta
from enum import Enum
from uuid import uuid4

from sqlalchemy import (
    String, Integer, Float, Boolean, DateTime, Text, JSON, ForeignKey,
    Enum as SQEnum, UniqueConstraint, Index, ForeignKey, Numeric, Date,
)
from sqlalchemy.orm import declarative_base, relationship, Mapped, mapped_column
from sqlalchemy.sql import func
from typing import Optional, List

Base = declarative_base()


# ============================================================================
# ENUMS
# ============================================================================

class UserRole(str, Enum):
    PATIENT = "PATIENT"
    HEALTHCARE_PROVIDER = "HEALTHCARE_PROVIDER"
    SURGEON = "SURGEON"
    ADMIN = "ADMIN"


class HospitalType(str, Enum):
    SPECIALTY_CENTER = "SPECIALTY_CENTER"
    GENERAL_HOSPITAL = "GENERAL_HOSPITAL"
    DIAGNOSTIC_CENTER = "DIAGNOSTIC_CENTER"
    NURSING_HOME = "NURSING_HOME"


class RuralTier(str, Enum):
    TIER_1 = "TIER_1"
    TIER_2 = "TIER_2"
    TIER_3 = "TIER_3"


class BookingStatus(str, Enum):
    INQUIRY = "INQUIRY"
    ESTIMATED = "ESTIMATED"
    CONFIRMED = "CONFIRMED"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"
    REFUNDED = "REFUNDED"


class RecoveryStatus(str, Enum):
    ACTIVE = "ACTIVE"
    PAUSED = "PAUSED"
    COMPLETED = "COMPLETED"
    ESCALATED = "ESCALATED"
    CLOSED = "CLOSED"


class AlertSeverity(str, Enum):
    INFO = "INFO"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"


class FinancingType(str, Enum):
    UPI_MICRO_LOAN = "UPI_MICRO_LOAN"
    HEALTH_EMI = "HEALTH_EMI"
    SUBSIDY_GRANT = "SUBSIDY_GRANT"
    INSURANCE_CLAIM = "INSURANCE_CLAIM"


class FinancingStatus(str, Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    DISBURSED = "DISBURSED"
    PAYING = "PAYING"
    COMPLETED = "COMPLETED"
    DEFAULTED = "DEFAULTED"


# ============================================================================
# USER & AUTHENTICATION
# ============================================================================

class User(Base):
    """User account (Patient, Healthcare Provider, Surgeon, or Admin)"""
    __tablename__ = "user"

    id: Mapped[str] = mapped_column(String(255), primary_key=True, default=lambda: str(uuid4()))
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    phone_encrypted: Mapped[Optional[str]] = mapped_column(String(255))
    role: Mapped[UserRole] = mapped_column(SQEnum(UserRole), default=UserRole.PATIENT)

    # GDPR: Right to be forgotten
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime)

    # Authentication
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    mfa_enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    mfa_secret_encrypted: Mapped[Optional[str]] = mapped_column(String(255))

    # HIPAA: Audit trail
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login: Mapped[Optional[datetime]] = mapped_column(DateTime)

    # Relations
    patient: Mapped[Optional["Patient"]] = relationship("Patient", back_populates="user", uselist=False)
    healthcare_provider: Mapped[Optional["HealthcareProvider"]] = relationship("HealthcareProvider", back_populates="user", uselist=False)
    surgeon: Mapped[Optional["Surgeon"]] = relationship("Surgeon", back_populates="user", uselist=False)
    audit_logs: Mapped[List["AuditLog"]] = relationship("AuditLog", back_populates="user")
    recovery_sessions: Mapped[List["RecoverySession"]] = relationship("RecoverySession", back_populates="assigned_surgeon")
    financing_records: Mapped[List["RuralFinancing"]] = relationship("RuralFinancing", back_populates="user")


class AuditLog(Base):
    """HIPAA audit trail for all user actions"""
    __tablename__ = "audit_log"

    id: Mapped[str] = mapped_column(String(255), primary_key=True, default=lambda: str(uuid4()))
    user_id: Mapped[str] = mapped_column(String(255), ForeignKey("user.id", ondelete="CASCADE"), index=True)
    user: Mapped[User] = relationship("User", back_populates="audit_logs")

    action: Mapped[str] = mapped_column(String(255), nullable=False)  # e.g., VIEWED_PATIENT_DATA
    resource_type: Mapped[str] = mapped_column(String(255), nullable=False)  # e.g., Hospital
    resource_id: Mapped[str] = mapped_column(String(255), nullable=False)

    ip_address: Mapped[Optional[str]] = mapped_column(String(45))
    user_agent: Mapped[Optional[str]] = mapped_column(String(500))

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)

    __table_args__ = (
        Index("idx_audit_resource", "resource_type", "resource_id"),
    )


# ============================================================================
# PATIENT PROFILES
# ============================================================================

class Patient(Base):
    """Patient profile with encrypted PII"""
    __tablename__ = "patient"

    id: Mapped[str] = mapped_column(String(255), primary_key=True, default=lambda: str(uuid4()))
    user_id: Mapped[str] = mapped_column(String(255), ForeignKey("user.id", ondelete="CASCADE"), unique=True)
    user: Mapped[User] = relationship("User", back_populates="patient")

    # Encrypted PII
    first_name_encrypted: Mapped[Optional[str]] = mapped_column(String(500))
    last_name_encrypted: Mapped[Optional[str]] = mapped_column(String(500))
    date_of_birth_encrypted: Mapped[Optional[str]] = mapped_column(String(500))

    blood_group: Mapped[Optional[str]] = mapped_column(String(10))
    age_approximated: Mapped[Optional[int]] = mapped_column(Integer)

    # Geographic data
    country_code: Mapped[str] = mapped_column(String(2), nullable=False)
    state_province: Mapped[Optional[str]] = mapped_column(String(100))
    postal_code_prefix: Mapped[Optional[str]] = mapped_column(String(10))
    rural_tier: Mapped[RuralTier] = mapped_column(SQEnum(RuralTier), default=RuralTier.TIER_2)

    # GDPR
    consent_given: Mapped[bool] = mapped_column(Boolean, default=False)
    consent_timestamp: Mapped[Optional[datetime]] = mapped_column(DateTime)
    data_deletion_requested_at: Mapped[Optional[datetime]] = mapped_column(DateTime)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relations
    medical_records: Mapped[List["MedicalRecord"]] = relationship("MedicalRecord", back_populates="patient")
    bookings: Mapped[List["HospitalBooking"]] = relationship("HospitalBooking", back_populates="patient")

    __table_args__ = (
        Index("idx_patient_location", "country_code", "rural_tier"),
    )


class MedicalRecord(Base):
    """Patient medical records with encrypted data"""
    __tablename__ = "medical_record"

    id: Mapped[str] = mapped_column(String(255), primary_key=True, default=lambda: str(uuid4()))
    patient_id: Mapped[str] = mapped_column(String(255), ForeignKey("patient.id", ondelete="CASCADE"), index=True)
    patient: Mapped[Patient] = relationship("Patient", back_populates="medical_records")

    # Encrypted clinical data
    diagnosis_encrypted: Mapped[Optional[str]] = mapped_column(String(500))
    procedure_encrypted: Mapped[Optional[str]] = mapped_column(String(500))

    record_date: Mapped[datetime] = mapped_column(DateTime, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


# ============================================================================
# GLOBAL HOSPITALS
# ============================================================================

class GlobalHospital(Base):
    """Hospital registry with JCI/NABH accreditation"""
    __tablename__ = "global_hospital"

    id: Mapped[str] = mapped_column(String(255), primary_key=True, default=lambda: str(uuid4()))
    name: Mapped[str] = mapped_column(String(255), nullable=False)

    # Accreditation
    jci_accredited: Mapped[bool] = mapped_column(Boolean, default=False)
    jci_certificate_url: Mapped[Optional[str]] = mapped_column(String(500))
    jci_expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime)

    nabh_accredited: Mapped[bool] = mapped_column(Boolean, default=False)
    nabh_certificate_url: Mapped[Optional[str]] = mapped_column(String(500))
    nabh_expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime)

    # Geographic
    country_code: Mapped[str] = mapped_column(String(2), nullable=False)
    state_province: Mapped[str] = mapped_column(String(100), nullable=False)
    city: Mapped[str] = mapped_column(String(100), nullable=False)
    latitude: Mapped[float] = mapped_column(Float, nullable=False)
    longitude: Mapped[float] = mapped_column(Float, nullable=False)
    postal_code: Mapped[Optional[str]] = mapped_column(String(20))

    # Contact
    phone_primary: Mapped[str] = mapped_column(String(20), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False)
    website_url: Mapped[Optional[str]] = mapped_column(String(500))

    # Classification
    hospital_type: Mapped[HospitalType] = mapped_column(SQEnum(HospitalType), nullable=False)

    # Price data tracking
    price_data_verified_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    price_data_source: Mapped[Optional[str]] = mapped_column(String(100))

    # Quality metrics
    avg_quality_score: Mapped[float] = mapped_column(Float, default=0)
    complication_rate: Mapped[Optional[float]] = mapped_column(Float)
    readmission_rate: Mapped[Optional[float]] = mapped_column(Float)
    patient_reviews_count: Mapped[int] = mapped_column(Integer, default=0)

    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False)
    source_id: Mapped[Optional[str]] = mapped_column(String(255), index=True)  # Original source ID

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relations
    departments: Mapped[List["Department"]] = relationship("Department", back_populates="hospital")
    procedures: Mapped[List["ProcedurePrice"]] = relationship("ProcedurePrice", back_populates="hospital")
    bookings: Mapped[List["HospitalBooking"]] = relationship("HospitalBooking", back_populates="hospital")
    recovery_providers: Mapped[List["RecoveryProvider"]] = relationship("RecoveryProvider", back_populates="hospital")

    __table_args__ = (
        Index("idx_hospital_active", "country_code", "is_active"),
        Index("idx_hospital_geo", "latitude", "longitude"),
        Index("idx_hospital_accreditation", "jci_accredited", "nabh_accredited"),
    )


class Department(Base):
    """Hospital departments/specializations"""
    __tablename__ = "department"

    id: Mapped[str] = mapped_column(String(255), primary_key=True, default=lambda: str(uuid4()))
    hospital_id: Mapped[str] = mapped_column(String(255), ForeignKey("global_hospital.id", ondelete="CASCADE"), index=True)
    hospital: Mapped[GlobalHospital] = relationship("GlobalHospital", back_populates="departments")

    name: Mapped[str] = mapped_column(String(150), nullable=False)
    specialization_code: Mapped[str] = mapped_column(String(10), nullable=False)
    head_name: Mapped[Optional[str]] = mapped_column(String(255))
    phone: Mapped[Optional[str]] = mapped_column(String(20))

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint("hospital_id", "specialization_code", name="uq_hospital_specialization"),
    )


# ============================================================================
# PRICE NORMALIZATION
# ============================================================================

class PriceNormalizer(Base):
    """Global medical code mapping (CPT → ICD-10 → UHI)"""
    __tablename__ = "price_normalizer"

    id: Mapped[str] = mapped_column(String(255), primary_key=True, default=lambda: str(uuid4()))

    # US CPT Code
    cpt_code: Mapped[str] = mapped_column(String(5), unique=True, nullable=False, index=True)
    cpt_description: Mapped[str] = mapped_column(String(500), nullable=False)

    # ICD-10 Standard
    icd10_code: Mapped[str] = mapped_column(String(7), nullable=False, index=True)
    icd10_description: Mapped[str] = mapped_column(String(500), nullable=False)

    # Regional codes
    uhi_code: Mapped[Optional[str]] = mapped_column(String(50), index=True)
    ehds_identifier: Mapped[Optional[str]] = mapped_column(String(50))

    # Clinical context
    clinical_category: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    complexity_score: Mapped[int] = mapped_column(Integer, default=1)

    # Reference cost
    us_median_cost_usd: Mapped[float] = mapped_column(Float, nullable=False)
    validation_date: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relations
    procedures: Mapped[List["ProcedurePrice"]] = relationship("ProcedurePrice", back_populates="normalizer")


# ============================================================================
# PROCEDURE PRICING
# ============================================================================

class ProcedurePrice(Base):
    """Hospital-specific procedure pricing"""
    __tablename__ = "procedure_price"

    id: Mapped[str] = mapped_column(String(255), primary_key=True, default=lambda: str(uuid4()))
    hospital_id: Mapped[str] = mapped_column(String(255), ForeignKey("global_hospital.id", ondelete="CASCADE"), index=True)
    hospital: Mapped[GlobalHospital] = relationship("GlobalHospital", back_populates="procedures")

    normalizer_id: Mapped[str] = mapped_column(String(255), ForeignKey("price_normalizer.id"), index=True)
    normalizer: Mapped[PriceNormalizer] = relationship("PriceNormalizer", back_populates="procedures")

    # Pricing breakdown (transparent & auditable)
    base_price: Mapped[float] = mapped_column(Float, nullable=False)
    facility_fee: Mapped[Optional[float]] = mapped_column(Float)
    anesthesia_fee: Mapped[Optional[float]] = mapped_column(Float)
    surgeon_fee: Mapped[Optional[float]] = mapped_column(Float)
    currency_code: Mapped[str] = mapped_column(String(3), default="USD")

    # Timing
    effective_date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime)

    # Outcome data (for Success-Adjusted Value ranking)
    success_rate: Mapped[Optional[float]] = mapped_column(Float)
    complication_rate: Mapped[Optional[float]] = mapped_column(Float)

    verified_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    data_source: Mapped[str] = mapped_column(String(100), nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relations
    bookings: Mapped[List["HospitalBooking"]] = relationship("HospitalBooking", back_populates="procedure")

    __table_args__ = (
        UniqueConstraint("hospital_id", "normalizer_id", "effective_date", name="uq_hospital_procedure_date"),
    )


# ============================================================================
# HOSPITAL BOOKINGS
# ============================================================================

class HospitalBooking(Base):
    """Patient hospital booking/procedure reservation"""
    __tablename__ = "hospital_booking"

    id: Mapped[str] = mapped_column(String(255), primary_key=True, default=lambda: str(uuid4()))
    patient_id: Mapped[str] = mapped_column(String(255), ForeignKey("patient.id", ondelete="CASCADE"), index=True)
    patient: Mapped[Patient] = relationship("Patient", back_populates="bookings")

    hospital_id: Mapped[str] = mapped_column(String(255), ForeignKey("global_hospital.id"), index=True)
    hospital: Mapped[GlobalHospital] = relationship("GlobalHospital", back_populates="bookings")

    procedure_id: Mapped[str] = mapped_column(String(255), ForeignKey("procedure_price.id"), index=True)
    procedure: Mapped[ProcedurePrice] = relationship("ProcedurePrice", back_populates="bookings")

    # Booking details
    status: Mapped[BookingStatus] = mapped_column(SQEnum(BookingStatus), default=BookingStatus.INQUIRY, index=True)
    scheduled_date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    estimated_duration_days: Mapped[Optional[int]] = mapped_column(Integer)

    # Success-Adjusted Value Score
    value_score: Mapped[Optional[float]] = mapped_column(Float)
    cost_component: Mapped[Optional[float]] = mapped_column(Float)
    risk_component: Mapped[Optional[float]] = mapped_column(Float)
    quality_component: Mapped[Optional[float]] = mapped_column(Float)

    # Financial
    estimated_total_usd: Mapped[Optional[float]] = mapped_column(Float)
    currency_applied: Mapped[Optional[str]] = mapped_column(String(3))

    notes: Mapped[Optional[str]] = mapped_column(String(500))  # Can be encrypted

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    cancelled_at: Mapped[Optional[datetime]] = mapped_column(DateTime)

    # Relations
    recovery_session: Mapped[Optional["RecoverySession"]] = relationship("RecoverySession", back_populates="booking", uselist=False)


# ============================================================================
# RECOVERY BRIDGE (IoMT Monitoring)
# ============================================================================

class RecoverySession(Base):
    """30-day post-operative recovery monitoring session"""
    __tablename__ = "recovery_session"

    id: Mapped[str] = mapped_column(String(255), primary_key=True, default=lambda: str(uuid4()))
    booking_id: Mapped[str] = mapped_column(String(255), ForeignKey("hospital_booking.id", ondelete="CASCADE"), unique=True)
    booking: Mapped[HospitalBooking] = relationship("HospitalBooking", back_populates="recovery_session")

    patient_id: Mapped[str] = mapped_column(String(255), ForeignKey("patient.id", ondelete="CASCADE"), index=True)
    patient: Mapped[Patient] = relationship("Patient", foreign_keys=[patient_id])

    # Surgeon assignment
    assigned_surgeon_id: Mapped[Optional[str]] = mapped_column(String(255), ForeignKey("surgeon.id"))
    assigned_surgeon: Mapped[Optional["Surgeon"]] = relationship("Surgeon")

    # Local clinic assignment
    assigned_provider_id: Mapped[Optional[str]] = mapped_column(String(255), ForeignKey("recovery_provider.id"))
    assigned_provider: Mapped[Optional["RecoveryProvider"]] = relationship("RecoveryProvider")

    # Timeline
    start_date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    end_date: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=lambda: datetime.utcnow() + timedelta(days=30))

    recovery_status: Mapped[RecoveryStatus] = mapped_column(SQEnum(RecoveryStatus), default=RecoveryStatus.ACTIVE, index=True)

    # Alert tracking
    alert_count: Mapped[int] = mapped_column(Integer, default=0)
    critical_alert_count: Mapped[int] = mapped_column(Integer, default=0)
    has_escalated: Mapped[bool] = mapped_column(Boolean, default=False)
    escalation_at: Mapped[Optional[datetime]] = mapped_column(DateTime)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relations
    vitals: Mapped[List["RecoveryVital"]] = relationship("RecoveryVital", back_populates="recovery_session")
    alerts: Mapped[List["RecoveryAlert"]] = relationship("RecoveryAlert", back_populates="recovery_session")

    __table_args__ = (
        Index("idx_recovery_status", "recovery_status"),
        Index("idx_recovery_dates", "start_date"),
    )


class RecoveryVital(Base):
    """Real-time IoMT wearable vital signs"""
    __tablename__ = "recovery_vital"

    id: Mapped[str] = mapped_column(String(255), primary_key=True, default=lambda: str(uuid4()))
    recovery_session_id: Mapped[str] = mapped_column(String(255), ForeignKey("recovery_session.id", ondelete="CASCADE"), index=True)
    recovery_session: Mapped[RecoverySession] = relationship("RecoverySession", back_populates="vitals")

    # IoMT data
    heart_rate: Mapped[Optional[int]] = mapped_column(Integer)
    blood_oxygen_spo2: Mapped[Optional[int]] = mapped_column(Integer)
    temperature_celsius: Mapped[Optional[float]] = mapped_column(Float)
    systolic_bp: Mapped[Optional[int]] = mapped_column(Integer)
    diastolic_bp: Mapped[Optional[int]] = mapped_column(Integer)
    respiratory_rate: Mapped[Optional[int]] = mapped_column(Integer)

    # Encrypted notes
    symptom_notes_encrypted: Mapped[Optional[str]] = mapped_column(String(500))

    # Alert
    alert_trigger: Mapped[bool] = mapped_column(Boolean, default=False)
    alert_severity: Mapped[Optional[AlertSeverity]] = mapped_column(SQEnum(AlertSeverity))

    # Device metadata
    device_id: Mapped[Optional[str]] = mapped_column(String(255))
    device_type: Mapped[Optional[str]] = mapped_column(String(100))

    collected_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relations
    alerts: Mapped[List["RecoveryAlert"]] = relationship("RecoveryAlert", back_populates="vital")

    __table_args__ = (
        Index("idx_vital_alert", "alert_trigger"),
    )


class RecoveryAlert(Base):
    """Clinical alerts triggered during recovery"""
    __tablename__ = "recovery_alert"

    id: Mapped[str] = mapped_column(String(255), primary_key=True, default=lambda: str(uuid4()))
    recovery_session_id: Mapped[str] = mapped_column(String(255), ForeignKey("recovery_session.id", ondelete="CASCADE"), index=True)
    recovery_session: Mapped[RecoverySession] = relationship("RecoverySession", back_populates="alerts")

    vital_id: Mapped[Optional[str]] = mapped_column(String(255), ForeignKey("recovery_vital.id"))
    vital: Mapped[Optional[RecoveryVital]] = relationship("RecoveryVital", back_populates="alerts")

    alert_type: Mapped[str] = mapped_column(String(100), nullable=False)
    severity: Mapped[AlertSeverity] = mapped_column(SQEnum(AlertSeverity), index=True)

    # Context
    patient_value: Mapped[Optional[str]] = mapped_column(String(100))
    normal_range: Mapped[Optional[str]] = mapped_column(String(100))
    recommendation: Mapped[Optional[str]] = mapped_column(String(500))

    # Escalation
    acknowledged_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    acknowledged_by_id: Mapped[Optional[str]] = mapped_column(String(255), ForeignKey("user.id"))
    action_taken: Mapped[Optional[str]] = mapped_column(String(500))
    resolved_at: Mapped[Optional[datetime]] = mapped_column(DateTime)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


# ============================================================================
# HEALTHCARE RESOURCES
# ============================================================================

class Surgeon(Base):
    """Surgeon profile and credentials"""
    __tablename__ = "surgeon"

    id: Mapped[str] = mapped_column(String(255), primary_key=True, default=lambda: str(uuid4()))
    user_id: Mapped[str] = mapped_column(String(255), ForeignKey("user.id", ondelete="CASCADE"), unique=True)
    user: Mapped[User] = relationship("User", back_populates="surgeon")

    license_number: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    country_of_license: Mapped[str] = mapped_column(String(2), nullable=False, index=True)
    specialization: Mapped[str] = mapped_column(String(150), nullable=False)

    # Credentials
    years_experience: Mapped[int] = mapped_column(Integer, nullable=False)
    total_procedures: Mapped[int] = mapped_column(Integer, default=0)
    success_rate: Mapped[Optional[float]] = mapped_column(Float)

    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    verified_at: Mapped[Optional[datetime]] = mapped_column(DateTime)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relations
    recovery_sessions: Mapped[List[RecoverySession]] = relationship("RecoverySession", back_populates="assigned_surgeon")


class HealthcareProvider(Base):
    """Referral partner healthcare provider"""
    __tablename__ = "healthcare_provider"

    id: Mapped[str] = mapped_column(String(255), primary_key=True, default=lambda: str(uuid4()))
    user_id: Mapped[str] = mapped_column(String(255), ForeignKey("user.id", ondelete="CASCADE"), unique=True)
    user: Mapped[User] = relationship("User", back_populates="healthcare_provider")

    organization_name: Mapped[str] = mapped_column(String(255), nullable=False)
    license_number: Mapped[str] = mapped_column(String(100), nullable=False)
    country_code: Mapped[str] = mapped_column(String(2), nullable=False, index=True)

    api_key_encrypted: Mapped[str] = mapped_column(String(500), nullable=False)
    webhook_url: Mapped[Optional[str]] = mapped_column(String(500))

    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    verified_at: Mapped[Optional[datetime]] = mapped_column(DateTime)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class RecoveryProvider(Base):
    """Local recovery clinic for post-operative monitoring"""
    __tablename__ = "recovery_provider"

    id: Mapped[str] = mapped_column(String(255), primary_key=True, default=lambda: str(uuid4()))
    hospital_id: Mapped[str] = mapped_column(String(255), ForeignKey("global_hospital.id", ondelete="CASCADE"), index=True)
    hospital: Mapped[GlobalHospital] = relationship("GlobalHospital", back_populates="recovery_providers")

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    phone: Mapped[str] = mapped_column(String(20), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False)

    # Capacity
    current_patients: Mapped[int] = mapped_column(Integer, default=0)
    max_concurrent: Mapped[int] = mapped_column(Integer, default=10)

    # Coverage
    coverage_radius_km: Mapped[int] = mapped_column(Integer, default=50)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relations
    recovery_sessions: Mapped[List[RecoverySession]] = relationship("RecoverySession", back_populates="assigned_provider")

    __table_args__ = (
        Index("idx_provider_hospital_active", "hospital_id", "is_active"),
    )


# ============================================================================
# RURAL FINANCING
# ============================================================================

class RuralFinancing(Base):
    """UPI 2.0 micro-financing and Health EMI for rural patients"""
    __tablename__ = "rural_financing"

    id: Mapped[str] = mapped_column(String(255), primary_key=True, default=lambda: str(uuid4()))
    patient_id: Mapped[str] = mapped_column(String(255), ForeignKey("user.id", ondelete="CASCADE"), index=True)
    user: Mapped[User] = relationship("User", back_populates="financing_records")

    booking_id: Mapped[Optional[str]] = mapped_column(String(255))  # Link to hospital booking

    # Financing type
    financing_type: Mapped[FinancingType] = mapped_column(SQEnum(FinancingType), nullable=False)

    # UPI 2.0 Details
    upi_transaction_id: Mapped[Optional[str]] = mapped_column(String(255), unique=True, index=True)
    upi_merchant_id: Mapped[Optional[str]] = mapped_column(String(255))

    # Amount & terms
    principal_amount: Mapped[float] = mapped_column(Float, nullable=False)
    currency_code: Mapped[str] = mapped_column(String(3), default="INR")

    interest_rate: Mapped[float] = mapped_column(Float, default=0)
    tenure_months: Mapped[int] = mapped_column(Integer, nullable=False)

    emi_amount: Mapped[float] = mapped_column(Float, nullable=False)
    emi_schedule: Mapped[str] = mapped_column(Text, nullable=False)  # JSON: [{due_date, amount, status}, ...]

    # Payment tracking
    total_paid: Mapped[float] = mapped_column(Float, default=0)
    next_due_date: Mapped[Optional[datetime]] = mapped_column(DateTime)
    last_payment_date: Mapped[Optional[datetime]] = mapped_column(DateTime)

    # Status
    status: Mapped[FinancingStatus] = mapped_column(SQEnum(FinancingStatus), default=FinancingStatus.PENDING, index=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
