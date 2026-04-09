"""
Authentication and authorization errors.
Custom exceptions for auth-related operations.
"""


class AuthError(Exception):
    """Base authentication error"""

    def __init__(
        self,
        message: str,
        error_code: str,
        status_code: int,
        details: dict = None,
    ):
        """
        Args:
            message: Human-readable error message
            error_code: Machine-readable error code (e.g., INVALID_CREDENTIALS)
            status_code: HTTP status code (401, 409, etc.)
            details: Additional error details
        """
        self.message = message
        self.error_code = error_code
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)

    def to_dict(self):
        """Convert to dictionary for API responses"""
        return {
            "error_code": self.error_code,
            "message": self.message,
            "details": self.details,
        }


class InvalidCredentialsError(AuthError):
    """Invalid email/password combination (401)"""

    def __init__(self, message: str = "Invalid email or password"):
        super().__init__(
            message=message,
            error_code="INVALID_CREDENTIALS",
            status_code=401,
        )


class UserNotFoundError(AuthError):
    """User not found (404)"""

    def __init__(self, message: str = "User not found"):
        super().__init__(
            message=message,
            error_code="USER_NOT_FOUND",
            status_code=404,
        )


class EmailAlreadyExistsError(AuthError):
    """Email already registered (409)"""

    def __init__(self, email: str = ""):
        message = f"Email already registered" + (f": {email}" if email else "")
        super().__init__(
            message=message,
            error_code="EMAIL_ALREADY_EXISTS",
            status_code=409,
            details={"email": email} if email else {},
        )


class MFARequiredError(AuthError):
    """MFA verification required (401)"""

    def __init__(self, message: str = "Multi-factor authentication required"):
        super().__init__(
            message=message,
            error_code="MFA_REQUIRED",
            status_code=401,
        )


class InvalidMFACodeError(AuthError):
    """Invalid MFA code (401)"""

    def __init__(self, message: str = "Invalid MFA code"):
        super().__init__(
            message=message,
            error_code="INVALID_MFA_CODE",
            status_code=401,
        )


class TokenExpiredError(AuthError):
    """JWT token expired (401)"""

    def __init__(self, message: str = "Token expired"):
        super().__init__(
            message=message,
            error_code="TOKEN_EXPIRED",
            status_code=401,
        )


class TokenInvalidError(AuthError):
    """JWT token invalid or malformed (401)"""

    def __init__(self, message: str = "Invalid or malformed token"):
        super().__init__(
            message=message,
            error_code="TOKEN_INVALID",
            status_code=401,
        )


class InsufficientPermissionsError(AuthError):
    """User doesn't have required permissions (403)"""

    def __init__(self, message: str = "Insufficient permissions"):
        super().__init__(
            message=message,
            error_code="INSUFFICIENT_PERMISSIONS",
            status_code=403,
        )


class MFAAlreadyEnabledError(AuthError):
    """User already has MFA enabled (409)"""

    def __init__(self, message: str = "MFA already enabled for this account"):
        super().__init__(
            message=message,
            error_code="MFA_ALREADY_ENABLED",
            status_code=409,
        )


class PasswordInvalidError(AuthError):
    """Password doesn't meet requirements (400)"""

    def __init__(self, message: str = None, details: dict = None):
        if message is None:
            message = "Password does not meet security requirements"
        super().__init__(
            message=message,
            error_code="PASSWORD_INVALID",
            status_code=400,
            details=details,
        )


class EmailInvalidError(AuthError):
    """Email format invalid (400)"""

    def __init__(self, message: str = None):
        if message is None:
            message = "Invalid email format"
        super().__init__(
            message=message,
            error_code="EMAIL_INVALID",
            status_code=400,
        )
