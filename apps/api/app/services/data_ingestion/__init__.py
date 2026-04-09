# apps/api/app/services/data_ingestion/__init__.py
"""
Data ingestion service for Evijnar.
Handles loading, mapping, and persisting hospital price transparency data.
"""

from .models import (
    RawHospitalData,
    RawProcedureData,
    RawDepartmentData,
    NormalizedHospitalData,
    NormalizedProcedureData,
    NormalizedPriceNormalizerData,
    IngestReport,
    IngestError as IngestErrorModel,
    IngestSource,
)

from .errors import (
    IngestError,
    LoaderError,
    InvalidJsonError,
    FormatError,
    MapperError,
    LLMError,
    LLMParsingError,
    ValidationError,
    CacheError,
    DatabaseError,
    DuplicateRecordError,
    EngineError,
    ConfigurationError,
    AuthenticationError,
)

__all__ = [
    # Models
    "RawHospitalData",
    "RawProcedureData",
    "RawDepartmentData",
    "NormalizedHospitalData",
    "NormalizedProcedureData",
    "NormalizedPriceNormalizerData",
    "IngestReport",
    "IngestErrorModel",
    "IngestSource",
    # Errors
    "IngestError",
    "LoaderError",
    "InvalidJsonError",
    "FormatError",
    "MapperError",
    "LLMError",
    "LLMParsingError",
    "ValidationError",
    "CacheError",
    "DatabaseError",
    "DuplicateRecordError",
    "EngineError",
    "ConfigurationError",
    "AuthenticationError",
]
