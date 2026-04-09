"""
Repository pattern for data access layer.
Isolates database operations from business logic.
"""

from .hospital import HospitalRepository
from .procedure import ProcedureRepository
from .normalizer import NormalizerRepository
from .audit import AuditRepository
from .user import UserRepository

__all__ = [
    "HospitalRepository",
    "ProcedureRepository",
    "NormalizerRepository",
    "AuditRepository",
    "UserRepository",
]
