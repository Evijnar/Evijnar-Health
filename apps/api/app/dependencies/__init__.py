"""
FastAPI dependencies for authentication, authorization, and other cross-cutting concerns.
"""

from .auth import (
    get_current_user,
    get_current_admin,
    get_current_healthcare_provider,
    get_current_surgeon,
    get_optional_user,
    require_role,
)

__all__ = [
    "get_current_user",
    "get_current_admin",
    "get_current_healthcare_provider",
    "get_current_surgeon",
    "get_optional_user",
    "require_role",
]
