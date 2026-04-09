"""
Authentication service module.
Contains business logic for user authentication, MFA, and authorization.
"""

from .errors import (
    AuthError,
    InvalidCredentialsError,
    UserNotFoundError,
    EmailAlreadyExistsError,
    MFARequiredError,
    InvalidMFACodeError,
    TokenExpiredError,
    TokenInvalidError,
    InsufficientPermissionsError,
    MFAAlreadyEnabledError,
    PasswordInvalidError,
    EmailInvalidError,
)

__all__ = [
    "AuthError",
    "InvalidCredentialsError",
    "UserNotFoundError",
    "EmailAlreadyExistsError",
    "MFARequiredError",
    "InvalidMFACodeError",
    "TokenExpiredError",
    "TokenInvalidError",
    "InsufficientPermissionsError",
    "MFAAlreadyEnabledError",
    "PasswordInvalidError",
    "EmailInvalidError",
]
