# apps/api/app/routers/auth.py
"""Authentication endpoints for signup, login, MFA, and token management"""

from datetime import datetime
from typing import Optional
import logging
from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.db import get_session
from app.models import User, UserRole
from app.repositories import UserRepository, AuditRepository
from app.dependencies import get_current_user
from app.utils import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    verify_token,
    generate_mfa_secret,
    verify_mfa_code,
    encrypt_mfa_secret,
    decrypt_mfa_secret,
    generate_backup_codes,
)
from app.services.auth import (
    InvalidCredentialsError,
    UserNotFoundError,
    EmailAlreadyExistsError,
    MFARequiredError,
    InvalidMFACodeError,
    TokenInvalidError,
    MFAAlreadyEnabledError,
    PasswordInvalidError,
)

logger = logging.getLogger("evijnar.auth")

router = APIRouter()

# ============================================================================
# PYDANTIC MODELS
# ============================================================================


class SignupRequest(BaseModel):
    """User signup request"""

    email: EmailStr
    password: str = Field(
        ...,
        min_length=8,
        description="Password must be at least 8 characters",
    )
    role: UserRole = Field(default=UserRole.PATIENT)

    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "password": "SecurePassword123!",
                "role": "PATIENT",
            }
        }


class LoginRequest(BaseModel):
    """User login request"""

    email: EmailStr
    password: str

    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "password": "SecurePassword123!",
            }
        }


class MFAVerifyRequest(BaseModel):
    """MFA code verification"""

    mfa_code: str = Field(..., min_length=6, max_length=6, pattern=r"^\d{6}$")

    class Config:
        json_schema_extra = {"example": {"mfa_code": "123456"}}


class RefreshTokenRequest(BaseModel):
    """Token refresh request"""

    refresh_token: str


class MFADisableRequest(BaseModel):
    """MFA disable request (requires password confirmation)"""

    password: str


class UserResponse(BaseModel):
    """User response model (no sensitive data)"""

    id: str
    email: str
    role: str
    mfa_enabled: bool
    created_at: datetime


class TokenResponse(BaseModel):
    """Token response"""

    access_token: str
    token_type: str = "bearer"
    mfa_required: Optional[bool] = None
    expires_in: Optional[int] = None

    class Config:
        json_schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "mfa_required": False,
                "expires_in": 86400,
            }
        }


class MFASetupResponse(BaseModel):
    """MFA setup response with QR code"""

    mfa_secret: str
    qr_code: str
    backup_codes: list[str]


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================


async def _create_audit_log(
    session: AsyncSession,
    user_id: str,
    action: str,
    resource_type: str = "User",
    resource_id: str = "",
) -> None:
    """Helper to log authentication actions"""
    try:
        audit_repo = AuditRepository(session)
        await audit_repo.create(
            user_id=user_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id or user_id,
        )
    except Exception as e:
        logger.warning(f"Failed to create audit log: {str(e)}")


# ============================================================================
# ENDPOINTS
# ============================================================================


@router.post("/signup", status_code=status.HTTP_201_CREATED)
async def signup(
    request: SignupRequest,
    session: AsyncSession = Depends(get_session),
):
    """
    Register a new user.

    - **email**: Valid email address (must be unique)
    - **password**: At least 8 characters
    - **role**: PATIENT, HEALTHCARE_PROVIDER, or SURGEON

    Returns: Created user data (201)
    """
    try:
        # Validate password strength
        if not any(c.isupper() for c in request.password):
            raise PasswordInvalidError(
                "Password must contain at least one uppercase letter"
            )
        if not any(c.isdigit() for c in request.password):
            raise PasswordInvalidError("Password must contain at least one digit")

        # Hash password
        password_hash = hash_password(request.password)

        # Create user
        user_repo = UserRepository(session)
        user = await user_repo.create(
            email=request.email,
            password_hash=password_hash,
            role=request.role,
        )

        # Audit log
        await _create_audit_log(session, user.id, "SIGNUP", "User", user.id)

        # Commit transaction
        await session.commit()

        logger.info(f"User registered: {user.id} ({request.email})")

        return {
            "status": "success",
            "data": {
                "user_id": user.id,
                "email": user.email,
                "role": user.role.value,
                "mfa_enabled": user.mfa_enabled,
            },
            "timestamp": datetime.utcnow().isoformat(),
        }

    except PasswordInvalidError as e:
        raise HTTPException(
            status_code=e.status_code,
            detail=e.message,
            headers={"X-Error-Code": e.error_code},
        )
    except IntegrityError:
        raise HTTPException(
            status_code=409,
            detail="Email already registered",
            headers={"X-Error-Code": "EMAIL_ALREADY_EXISTS"},
        )
    except Exception as e:
        logger.error(f"Signup error: {str(e)}")
        await session.rollback()
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/login")
async def login(
    request: LoginRequest,
    session: AsyncSession = Depends(get_session),
):
    """
    Login user and get access token.

    Returns: JWT access token (and mfa_required flag if MFA is enabled)
    """
    try:
        # Find user
        user_repo = UserRepository(session)
        user = await user_repo.find_by_email(request.email)

        if not user:
            logger.warning(f"Login failed: User not found ({request.email})")
            raise HTTPException(
                status_code=401,
                detail="Invalid email or password",
                headers={"X-Error-Code": "INVALID_CREDENTIALS"},
            )

        # Verify password
        if not verify_password(request.password, user.password_hash):
            logger.warning(f"Login failed: Invalid password ({request.email})")
            raise HTTPException(
                status_code=401,
                detail="Invalid email or password",
                headers={"X-Error-Code": "INVALID_CREDENTIALS"},
            )

        # Check if MFA is enabled
        if user.mfa_enabled:
            # User must verify MFA code at /auth/verify-mfa endpoint
            logger.info(f"Login: MFA required for {user.id}")
            await _create_audit_log(session, user.id, "LOGIN_MFA_REQUIRED", "User", user.id)
            await session.commit()

            return {
                "status": "success",
                "data": {
                    "mfa_required": True,
                },
                "timestamp": datetime.utcnow().isoformat(),
            }

        # Generate JWT token
        access_token = create_access_token(user_id=user.id, role=user.role)

        # Update last login
        await user_repo.update_last_login(user.id)

        # Audit log
        await _create_audit_log(session, user.id, "LOGIN_SUCCESS", "User", user.id)
        await session.commit()

        logger.info(f"User logged in: {user.id}")

        expires_in = settings.jwt_expiration_hours * 3600

        return {
            "status": "success",
            "data": {
                "access_token": access_token,
                "token_type": "bearer",
                "expires_in": expires_in,
            },
            "timestamp": datetime.utcnow().isoformat(),
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        await session.rollback()
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/verify-mfa")
async def verify_mfa(
    request: MFAVerifyRequest,
    session: AsyncSession = Depends(get_session),
):
    """
    Verify MFA code and get access token.
    Use this after login if MFA is required.
    """
    try:
        # For now, we need email from request body or from session
        # In production, use session storage or cache
        # For MVP: client must provide email with MFA code
        # We'll expect it in an optional field
        class MFAVerifyWithEmailRequest(MFAVerifyRequest):
            email: EmailStr = None

        # Alternative: Use a temporary session cache with Redis
        # For now, we'll require email
        raise HTTPException(
            status_code=400,
            detail="This endpoint requires session context (email stored in Redis cache during login)",
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"MFA verify error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/refresh")
async def refresh_token(
    request: RefreshTokenRequest,
    session: AsyncSession = Depends(get_session),
):
    """
    Refresh JWT access token using a valid refresh token.
    """
    try:
        # Verify refresh token
        payload = verify_token(request.refresh_token)

        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=401,
                detail="Invalid token type",
                headers={"X-Error-Code": "TOKEN_INVALID"},
            )

        user_id = payload.get("sub")

        # Get user
        user_repo = UserRepository(session)
        user = await user_repo.find_by_id(user_id)

        if not user:
            raise HTTPException(
                status_code=404,
                detail="User not found",
                headers={"X-Error-Code": "USER_NOT_FOUND"},
            )

        # Generate new access token
        access_token = create_access_token(user_id=user.id, role=user.role)

        # Audit log
        await _create_audit_log(session, user.id, "TOKEN_REFRESH", "Token", user.id)
        await session.commit()

        expires_in = settings.jwt_expiration_hours * 3600

        return {
            "status": "success",
            "data": {
                "access_token": access_token,
                "token_type": "bearer",
                "expires_in": expires_in,
            },
            "timestamp": datetime.utcnow().isoformat(),
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Token refresh error: {str(e)}")
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired refresh token",
            headers={"X-Error-Code": "TOKEN_INVALID"},
        )


@router.post("/logout")
async def logout(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """
    Logout user (invalidate token).
    In production, add token to blacklist in Redis.
    """
    try:
        # TODO: Add token to Redis blacklist
        # For now, on client side: delete token from localStorage

        # Audit log
        await _create_audit_log(session, current_user.id, "LOGOUT", "User", current_user.id)
        await session.commit()

        logger.info(f"User logged out: {current_user.id}")

        return {
            "status": "success",
            "message": "Logged out successfully",
            "timestamp": datetime.utcnow().isoformat(),
        }

    except Exception as e:
        logger.error(f"Logout error: {str(e)}")
        await session.rollback()
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/mfa/setup")
async def setup_mfa(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """
    Setup MFA for user account.
    Returns QR code to scan with authenticator app.
    """
    try:
        if current_user.mfa_enabled:
            raise HTTPException(
                status_code=409,
                detail="MFA already enabled for this account",
                headers={"X-Error-Code": "MFA_ALREADY_ENABLED"},
            )

        # Generate MFA secret
        mfa_secret, qr_code = generate_mfa_secret(current_user.email)
        backup_codes = generate_backup_codes()

        # Store temporary secret + backup codes in session
        # TODO: Store in Redis with 15-minute TTL
        # For MVP: Return to client, expect verification at /mfa/verify

        logger.info(f"MFA setup initiated for user {current_user.id}")

        return {
            "status": "success",
            "data": {
                "mfa_secret": mfa_secret,
                "qr_code": qr_code,
                "backup_codes": backup_codes,
            },
            "timestamp": datetime.utcnow().isoformat(),
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"MFA setup error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/mfa/verify")
async def verify_mfa_setup(
    request: MFAVerifyRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """
    Verify MFA code and enable MFA on account.
    Must be called after /mfa/setup.
    """
    try:
        # TODO: Get temporary MFA secret from Redis session
        # For MVP: We need to enhance this with session management

        raise HTTPException(
            status_code=501,
            detail="MFA verification requires Redis session storage (planned for Phase 2)",
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"MFA verify setup error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/mfa/disable")
async def disable_mfa(
    request: MFADisableRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """Disable MFA for user account (requires password confirmation)"""
    try:
        if not current_user.mfa_enabled:
            raise HTTPException(
                status_code=400,
                detail="MFA is not enabled for this account",
            )

        # Verify password
        if not verify_password(request.password, current_user.password_hash):
            raise HTTPException(
                status_code=401,
                detail="Invalid password",
                headers={"X-Error-Code": "INVALID_CREDENTIALS"},
            )

        # Disable MFA
        user_repo = UserRepository(session)
        await user_repo.update_mfa(
            user_id=current_user.id,
            mfa_enabled=False,
            mfa_secret_encrypted=None,
        )

        # Audit log
        await _create_audit_log(session, current_user.id, "MFA_DISABLED", "User", current_user.id)
        await session.commit()

        logger.info(f"MFA disabled for user {current_user.id}")

        return {
            "status": "success",
            "message": "MFA disabled successfully",
            "timestamp": datetime.utcnow().isoformat(),
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"MFA disable error: {str(e)}")
        await session.rollback()
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/me")
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current authenticated user info"""
    return {
        "status": "success",
        "data": {
            "user_id": current_user.id,
            "email": current_user.email,
            "role": current_user.role.value,
            "mfa_enabled": current_user.mfa_enabled,
            "last_login": current_user.last_login.isoformat() if current_user.last_login else None,
            "created_at": current_user.created_at.isoformat(),
        },
        "timestamp": datetime.utcnow().isoformat(),
    }
