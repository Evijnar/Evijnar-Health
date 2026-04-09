# apps/api/app/services/data_ingestion/models.py
"""
Data models for the ingestion pipeline.
Defines raw data formats from external sources and normalized formats for database storage.
"""

from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class IngestSource(str, Enum):
    """Source of ingested data"""
    HHS_TRANSPARENCY = "HHS_TRANSPARENCY"      # USA
    EHDS = "EHDS"                              # Europe
    ABDM = "ABDM"                              # India
    HOSPITAL_SELF_REPORT = "HOSPITAL_SELF_REPORT"


# ============================================================================
# RAW DATA MODELS (from external sources, potentially messy)
# ============================================================================

class RawProcedureData(BaseModel):
    """Messy procedure data as it comes from source"""
    description: str                # e.g., "Total Knee Replacement with Prosthesis"
    code: Optional[str] = None      # CPT, ICD-10, or UHI code
    price: Optional[float] = None
    currency: str = "USD"
    success_rate: Optional[float] = None    # Percentage if available
    complication_rate: Optional[float] = None


class RawDepartmentData(BaseModel):
    """Department/specialization data"""
    name: str                       # e.g., "Orthopedic Surgery" or "Service de Chirurgie"
    code: Optional[str] = None      # Specialization code if present
    head_name: Optional[str] = None
    phone: Optional[str] = None
    procedures: List[RawProcedureData] = []


class RawHospitalData(BaseModel):
    """
    Denormalized hospital data extracted from JSON source.
    May contain messy, non-standardized information.
    """
    # Identifiers
    source_id: str                  # ID from source (e.g., HHS facility CCN)
    source: IngestSource

    # Hospital info (potentially messy)
    name: str                       # Hospital name as in source (may be abbreviated)
    name_alternate: Optional[str] = None
    description: Optional[str] = None

    # Contact (messy format)
    phone: Optional[str] = None     # May not be E.164 format
    email: Optional[str] = None
    website: Optional[str] = None

    # Address (may be incomplete)
    street_address: Optional[str] = None
    city: str
    state_or_province: str          # ISO 3166-2 or full name
    postal_code: Optional[str] = None
    country_code: str = "US"        # ISO 3166-1

    # Hospital classification (raw from source)
    hospital_type_raw: Optional[str] = None  # e.g., "Acute Care Hospital"
    description_type: Optional[str] = None

    # Accreditation (if present in source)
    jci_accredited: Optional[bool] = None
    nabh_accredited: Optional[bool] = None    # India-specific
    other_accreditations: List[str] = []

    # Quality metrics (if present)
    quality_score: Optional[float] = None
    complication_rate: Optional[float] = None
    readmission_rate: Optional[float] = None
    reviews_count: Optional[int] = None

    # Departments and procedures
    departments: List[RawDepartmentData] = []
    procedures: List[RawProcedureData] = []  # Top-level procedures if present

    # Metadata
    data_verified_date: Optional[datetime] = None
    raw_json: Optional[Dict[str, Any]] = None  # Original JSON for reference


# ============================================================================
# NORMALIZED DATA MODELS (standardized for database)
# ============================================================================

class NormalizedHospitalData(BaseModel):
    """Normalized hospital data ready for GlobalHospital table"""
    name: str                       # Standardized name
    hospital_type: str              # One of: SPECIALTY_CENTER, GENERAL_HOSPITAL, DIAGNOSTIC_CENTER, NURSING_HOME

    # Address (standardized)
    country_code: str               # ISO 3166-1 alpha-2
    state_province: str
    city: str
    postal_code: Optional[str] = None

    # Contact (standardized format)
    phone_primary: Optional[str] = None  # E.164 format
    email: Optional[str] = None
    website_url: Optional[str] = None

    # Accreditation (binary flags)
    jci_accredited: bool = False
    jci_certificate_url: Optional[str] = None
    jci_expires_at: Optional[datetime] = None
    nabh_accredited: bool = False
    nabh_certificate_url: Optional[str] = None
    nabh_expires_at: Optional[datetime] = None

    # Quality metrics
    avg_quality_score: float = 0
    complication_rate: Optional[float] = None
    readmission_rate: Optional[float] = None
    patient_reviews_count: int = 0

    # Metadata
    price_data_source: IngestSource
    price_data_verified_at: datetime = Field(default_factory=datetime.utcnow)

    # Reference to source
    source_id: str                  # Original source ID for tracking


class NormalizedProcedureData(BaseModel):
    """Normalized procedure with clinical codes"""
    # CPT / ICD-10 references
    cpt_code: Optional[str] = None
    icd10_code: str                 # Required: standardized code (e.g., M17.11)
    uhi_code: Optional[str] = None  # India-specific
    ehds_identifier: Optional[str] = None

    # Clinical classification
    clinical_category: str          # e.g., "Orthopedic Surgery", "Oncology"
    complexity_score: int = Field(ge=1, le=10)  # 1-10 scale

    # Pricing
    base_price: float               # Core procedure cost
    facility_fee: Optional[float] = None
    anesthesia_fee: Optional[float] = None
    surgeon_fee: Optional[float] = None
    currency_code: str = "USD"

    # Outcomes
    success_rate: Optional[float] = None
    complication_rate: Optional[float] = None

    # Metadata
    data_source: IngestSource
    verified_at: datetime = Field(default_factory=datetime.utcnow)


class NormalizedPriceNormalizerData(BaseModel):
    """
    Normalized data for PriceNormalizer table.
    Maps CPT → ICD-10 → UHI medical codes.
    """
    cpt_code: str                   # US CPT code
    cpt_description: str
    icd10_code: str                 # Global ICD-10 code
    icd10_description: str
    uhi_code: Optional[str] = None  # India UHI code
    ehds_identifier: Optional[str] = None  # Europe EHDS code
    clinical_category: str          # Specialization
    complexity_score: int = Field(ge=1, le=10)
    us_median_cost_usd: float

    @field_validator('cpt_code')
    def validate_cpt_code(cls, v):
        """CPT codes are 5 characters"""
        if len(v) != 5 or not v.isdigit():
            raise ValueError("CPT code must be 5 digits")
        return v

    @field_validator('icd10_code')
    def validate_icd10_code(cls, v):
        """ICD-10 codes follow pattern ABC.DE"""
        if len(v) not in [5, 6] or (len(v) == 6 and v[3] != '.'):
            raise ValueError("ICD-10 code must be format ABC.DE")
        return v


# ============================================================================
# INGESTION REPORTING
# ============================================================================

class IngestError(BaseModel):
    """Record of a failed ingestion"""
    source_id: str                  # ID from source
    error_message: str
    error_type: str                 # e.g., "VALIDATION_ERROR", "LLM_ERROR", "DB_ERROR"
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    raw_data_snippet: Optional[Dict[str, Any]] = None


class IngestReport(BaseModel):
    """
    Summary of an ingestion job.
    Tracks success/failure statistics.
    """
    job_id: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    source: IngestSource
    filename: Optional[str] = None

    total_records: int = 0
    succeeded: int = 0
    failed: int = 0
    skipped: int = 0              # Duplicates or already-ingested records

    hospitals_created: int = 0
    procedures_created: int = 0
    normalizers_created: int = 0

    errors: List[IngestError] = []
    warnings: List[str] = []

    start_time: datetime = Field(default_factory=datetime.utcnow)
    end_time: Optional[datetime] = None
    processing_time_seconds: Optional[float] = None

    @property
    def success_rate(self) -> float:
        """Percentage of records successfully ingested"""
        if self.total_records == 0:
            return 0
        return (self.succeeded / self.total_records) * 100

    @property
    def is_complete(self) -> bool:
        """True if all records processed"""
        return (self.succeeded + self.failed + self.skipped) == self.total_records


class IngestMetrics(BaseModel):
    """Metrics for LLM usage and performance"""
    total_llm_calls: int = 0
    total_tokens_used: int = 0
    total_llm_cost_usd: float = 0
    average_mapping_time_ms: float = 0
    cache_hit_rate: float = 0  # Percentage of cached results


# ============================================================================
# VALIDATION SCHEMAS
# ============================================================================

class HospitalMapperInput(BaseModel):
    """Input to Claude for hospital mapping"""
    name: str
    address_components: Dict[str, str]  # city, state, postal_code, country
    phone: Optional[str] = None
    description: Optional[str] = None
    hospital_type_hint: Optional[str] = None


class ProcedureMapperInput(BaseModel):
    """Input to Claude for procedure mapping"""
    description: str
    price: Optional[float] = None
    code_hint: Optional[str] = None  # May have partial code
    source: IngestSource


class NormalizerMapperInput(BaseModel):
    """Input to Claude for normalizer/CPT mapping"""
    cpt_code: str
    cpt_description: str
    source: IngestSource
    historical_mapping: Optional[Dict[str, str]] = None  # Previous mappings for reference
