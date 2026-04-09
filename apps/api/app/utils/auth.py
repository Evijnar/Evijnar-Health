"""
Authentication utilities for JWT token management and password hashing.
Handles password hashing with bcrypt and JWT token creation/verification.
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import logging
from jose import JWTError, jwt
from passlib.context import CryptContext
from app.config import settings
from app.models import UserRole

logger = logging.getLogger("evijnar.auth")

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """
    Hash a plaintext password using bcrypt.

    Args:
        password: Plaintext password to hash

    Returns:
        Hashed password string
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, password_hash: str) -> bool:
    """
    Verify a plaintext password against a bcrypt hash.

    Args:
        plain_password: Plaintext password to verify
        password_hash: Hashed password from database

    Returns:
        True if password matches, False otherwise
    """
    return pwd_context.verify(plain_password, password_hash)


def create_access_token(user_id: str, role: UserRole, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token.

    Args:
        user_id: User UUID
        role: User role (PATIENT, HEALTHCARE_PROVIDER, SURGEON, ADMIN)
        expires_delta: Optional custom expiration delta (default: jwt_expiration_hours from config)

    Returns:
        Signed JWT token
    """
    if expires_delta is None:
        expires_delta = timedelta(hours=settings.jwt_expiration_hours)

    expire = datetime.utcnow() + expires_delta

    payload = {
        "sub": user_id,  # Subject (user ID)
        "role": role.value,
        "type": "access",
        "exp": expire,
        "iat": datetime.utcnow(),
    }

    encoded_jwt = jwt.encode(
        payload,
        settings.jwt_secret,
        algorithm=settings.jwt_algorithm,
    )

    logger.info(f"Created access token for user {user_id}")
    return encoded_jwt


def create_refresh_token(user_id: str) -> str:
    """
    Create a JWT refresh token with longer expiration.

    Args:
        user_id: User UUID

    Returns:
        Signed JWT refresh token
    """
    expires_delta = timedelta(days=settings.jwt_refresh_expiration_days)
    expire = datetime.utcnow() + expires_delta

    payload = {
        "sub": user_id,
        "type": "refresh",
        "exp": expire,
        "iat": datetime.utcnow(),
    }

    encoded_jwt = jwt.encode(
        payload,
        settings.jwt_secret,
        algorithm=settings.jwt_algorithm,
    )

    logger.info(f"Created refresh token for user {user_id}")
    return encoded_jwt


def verify_token(token: str) -> Dict[str, Any]:
    """
    Verify a JWT token and return its payload.

    Args:
        token: JWT token to verify

    Returns:
        Token payload dictionary

    Raises:
        JWTError: If token is invalid, expired, or malformed
    """
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret,
            algorithms=[settings.jwt_algorithm],
        )
        return payload
    except JWTError as e:
        logger.warning(f"Invalid token: {str(e)}")
        raise


def extract_token_payload(token: str) -> Optional[Dict[str, Any]]:
    """
    Safely extract JWT payload without raising exceptions.

    Args:
        token: JWT token to extract from

    Returns:
        Token payload if valid, None otherwise
    """
    try:
        return verify_token(token)
    except JWTError:
        return None


def get_user_id_from_token(token: str) -> Optional[str]:
    """
    Extract user ID from a valid JWT token.

    Args:
        token: JWT token

    Returns:
        User ID if valid, None otherwise
    """
    payload = extract_token_payload(token)
    if payload:
        return payload.get("sub")
    return None


def get_user_role_from_token(token: str) -> Optional[str]:
    """
    Extract user role from a valid JWT token.

    Args:
        token: JWT token

    Returns:
        User role if valid, None otherwise
    """
    payload = extract_token_payload(token)
    if payload:
        return payload.get("role")
    return None
