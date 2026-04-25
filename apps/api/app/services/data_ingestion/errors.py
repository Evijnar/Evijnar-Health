# apps/api/app/services/data_ingestion/errors.py
"""
Custom exceptions for the data ingestion pipeline.
Provides granular error handling and categorization.
"""


class IngestError(Exception):
    """Base exception for ingestion pipeline"""
    def __init__(self, message: str, error_code: str = "INGEST_ERROR", details: dict = None):
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        super().__init__(self.message)

    def to_dict(self):
        return {
            "error_code": self.error_code,
            "message": self.message,
            "details": self.details,
        }


class LoaderError(IngestError):
    """Error during data loading from file"""
    def __init__(self, message: str, details: dict = None):
        super().__init__(message, "LOADER_ERROR", details)


class InvalidJsonError(LoaderError):
    """JSON file is invalid or malformed"""
    def __init__(self, message: str, details: dict = None):
        super().__init__(message, "INVALID_JSON", details)


class FormatError(LoaderError):
    """Data format doesn't match expected schema"""
    def __init__(self, message: str, details: dict = None):
        super().__init__(message, "FORMAT_ERROR", details)


class MapperError(IngestError):
    """Error during LLM-based mapping"""
    def __init__(self, message: str, details: dict = None):
        super().__init__(message, "MAPPER_ERROR", details)


class LLMError(MapperError):
    """Error calling Evijnar Health AI"""
    def __init__(self, message: str, details: dict = None):
        super().__init__(message, "LLM_ERROR", details)


class LLMParsingError(MapperError):
    """AI response couldn't be parsed"""
    def __init__(self, message: str, details: dict = None):
        super().__init__(message, "LLM_PARSING_ERROR", details)


class ValidationError(MapperError):
    """Normalized data failed validation"""
    def __init__(self, message: str, details: dict = None):
        super().__init__(message, "VALIDATION_ERROR", details)


class CacheError(IngestError):
    """Error accessing cache (Redis)"""
    def __init__(self, message: str, details: dict = None):
        super().__init__(message, "CACHE_ERROR", details)


class DatabaseError(IngestError):
    """Error writing to database"""
    def __init__(self, message: str, details: dict = None):
        super().__init__(message, "DATABASE_ERROR", details)


class DuplicateRecordError(DatabaseError):
    """Record already exists in database"""
    def __init__(self, message: str, details: dict = None):
        super().__init__(message, "DUPLICATE_RECORD", details)


class EngineError(IngestError):
    """Error in ingestion engine orchestration"""
    def __init__(self, message: str, details: dict = None):
        super().__init__(message, "ENGINE_ERROR", details)


class ConfigurationError(IngestError):
    """Configuration is invalid or missing"""
    def __init__(self, message: str, details: dict = None):
        super().__init__(message, "CONFIGURATION_ERROR", details)


class AuthenticationError(IngestError):
    """Authentication/authorization error"""
    def __init__(self, message: str, details: dict = None):
        super().__init__(message, "AUTHENTICATION_ERROR", details)
