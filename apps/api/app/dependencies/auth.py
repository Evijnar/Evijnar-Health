"""
FastAPI dependencies for authentication and authorization.
Provides JWT verification and RBAC (role-based access control) for route protection.
"""

from typing import Optional, List
import logging
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer
from fastapi.security.http import HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_session
from app.models import User, UserRole
from app.repositories import UserRepository
from app.utils import verify_token, extract_token_payload
from app.services.auth import (
    TokenInvalidError,
    TokenExpiredError,
    UserNotFoundError,
    InsufficientPermissionsError,
)

logger = logging.getLogger("evijnar.auth.dependencies")

security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    session: AsyncSession = Depends(get_session),
) -> User:
    """
    Extract and verify JWT token from Authorization header.
    Returns the current authenticated user.

    Usage in routes:
        @router.get("/protected")
        async def protected_endpoint(current_user: User = Depends(get_current_user)):
            return {"user_id": current_user.id}

    Raises:
        HTTPException: 401 if token is invalid/expired, 404 if user not found
    """
    token = credentials.credentials

    try:
        # Verify JWT token
        payload = verify_token(token)
    except Exception as e:
        logger.warning(f"JWT verification failed: {str(e)}")
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token",
            headers={"X-Error-Code": "TOKEN_INVALID"},
        )

    user_id = payload.get("sub")
    if not user_id:
        logger.warning("Token missing user ID (sub claim)")
        raise HTTPException(
            status_code=401,
            detail="Invalid token payload",
            headers={"X-Error-Code": "TOKEN_INVALID"},
        )

    # Get user from database
    try:
        user_repo = UserRepository(session)
        user = await user_repo.find_by_id(user_id)

        if not user:
            logger.warning(f"User not found for token: {user_id}")
            raise HTTPException(
                status_code=404,
                detail="User not found",
                headers={"X-Error-Code": "USER_NOT_FOUND"},
            )

        return user

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching user {user_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error",
        )


async def get_current_admin(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Verify current user is an admin.

    Usage:
        @router.get("/admin-only")
        async def admin_endpoint(current_user: User = Depends(get_current_admin)):
            return {"user_id": current_user.id}

    Raises:
        HTTPException: 403 if user is not an admin
    """
    if current_user.role != UserRole.ADMIN:
        logger.warning(
            f"Non-admin access attempt by user {current_user.id} ({current_user.role.value})"
        )
        raise HTTPException(
            status_code=403,
            detail="Admin access required",
            headers={"X-Error-Code": "INSUFFICIENT_PERMISSIONS"},
        )

    return current_user


async def get_current_healthcare_provider(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Verify current user is a healthcare provider.

    Raises:
        HTTPException: 403 if user is not a healthcare provider
    """
    if current_user.role != UserRole.HEALTHCARE_PROVIDER:
        logger.warning(
            f"Non-provider access attempt by user {current_user.id} ({current_user.role.value})"
        )
        raise HTTPException(
            status_code=403,
            detail="Healthcare provider access required",
            headers={"X-Error-Code": "INSUFFICIENT_PERMISSIONS"},
        )

    return current_user


async def get_current_surgeon(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Verify current user is a surgeon.

    Raises:
        HTTPException: 403 if user is not a surgeon
    """
    if current_user.role != UserRole.SURGEON:
        logger.warning(
            f"Non-surgeon access attempt by user {current_user.id} ({current_user.role.value})"
        )
        raise HTTPException(
            status_code=403,
            detail="Surgeon access required",
            headers={"X-Error-Code": "INSUFFICIENT_PERMISSIONS"},
        )

    return current_user


def require_role(*allowed_roles: UserRole):
    """
    Create a dependency that checks if user has one of the allowed roles.

    Usage:
        doctor_only = require_role(UserRole.SURGEON, UserRole.HEALTHCARE_PROVIDER)

        @router.get("/doctors-only")
        async def doctor_endpoint(current_user: User = Depends(doctor_only)):
            return {"user_id": current_user.id}

    Args:
        allowed_roles: Variable-length list of allowed roles

    Returns:
        FastAPI dependency function
    """

    async def check_role(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in allowed_roles:
            role_names = ", ".join(r.value for r in allowed_roles)
            logger.warning(
                f"Insufficient role access attempt by user {current_user.id}: "
                f"required {role_names}, got {current_user.role.value}"
            )
            raise HTTPException(
                status_code=403,
                detail=f"Access requires one of: {role_names}",
                headers={"X-Error-Code": "INSUFFICIENT_PERMISSIONS"},
            )
        return current_user

    return check_role


async def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False)),
    session: AsyncSession = Depends(get_session),
) -> Optional[User]:
    """
    Get current user if authenticated, return None otherwise.
    Useful for endpoints that work with or without authentication.

    Usage:
        @router.get("/maybe-protected")
        async def maybe_protected(current_user: Optional[User] = Depends(get_optional_user)):
            if current_user:
                return {"user_id": current_user.id}
            return {"message": "Anonymous access"}
    """
    if not credentials:
        return None

    try:
        return await get_current_user(credentials, session)
    except HTTPException:
        return None
