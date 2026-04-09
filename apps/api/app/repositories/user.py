"""
Repository for user database operations.
Handles CRUD and special operations for User entities with full audit trail.
"""

from typing import Optional
from datetime import datetime
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import User, UserRole
import logging

logger = logging.getLogger("evijnar.repo.user")


class UserRepository:
    """Data access layer for user operations"""

    def __init__(self, session: AsyncSession):
        """
        Initialize repository with database session.

        Args:
            session: AsyncSession for database operations
        """
        self.session = session

    async def create(
        self,
        email: str,
        password_hash: str,
        role: UserRole = UserRole.PATIENT,
    ) -> User:
        """
        Create a new user with duplicate check.

        Args:
            email: User email (must be unique)
            password_hash: Hashed password
            role: User role (default: PATIENT)

        Returns:
            Created User object

        Raises:
            IntegrityError: If email already exists
        """
        try:
            # Check if email already exists
            existing = await self.find_by_email(email)
            if existing:
                logger.warning(f"Signup attempt with existing email: {email}")
                raise IntegrityError(
                    statement="User.email",
                    params={"email": email},
                    orig=Exception(f"Email already exists: {email}"),
                )

            # Create new user
            user = User(
                email=email,
                password_hash=password_hash,
                role=role,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            )

            self.session.add(user)
            await self.session.flush()  # Flush to get the user ID

            logger.info(f"Created user: {user.id} ({email}) with role {role.value}")
            return user

        except IntegrityError as e:
            logger.error(f"Integrity error creating user: {str(e)}")
            await self.session.rollback()
            raise
        except Exception as e:
            logger.error(f"Error creating user: {str(e)}")
            await self.session.rollback()
            raise

    async def find_by_email(self, email: str) -> Optional[User]:
        """
        Find user by email.

        Args:
            email: User email

        Returns:
            User object if found, None otherwise
        """
        try:
            result = await self.session.execute(
                select(User).where(
                    (User.email == email) & (User.is_deleted == False)
                )
            )
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error finding user by email {email}: {str(e)}")
            raise

    async def find_by_id(self, user_id: str) -> Optional[User]:
        """
        Find user by ID (excluding deleted users).

        Args:
            user_id: User UUID

        Returns:
            User object if found, None otherwise
        """
        try:
            result = await self.session.execute(
                select(User).where(
                    (User.id == user_id) & (User.is_deleted == False)
                )
            )
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error finding user by ID {user_id}: {str(e)}")
            raise

    async def update_password(self, user_id: str, new_password_hash: str) -> User:
        """
        Update user password hash.

        Args:
            user_id: User UUID
            new_password_hash: New hashed password

        Returns:
            Updated User object
        """
        try:
            user = await self.find_by_id(user_id)
            if not user:
                logger.warning(f"Password update for non-existent user: {user_id}")
                return None

            user.password_hash = new_password_hash
            user.updated_at = datetime.utcnow()

            await self.session.flush()
            logger.info(f"Password updated for user {user_id}")
            return user

        except Exception as e:
            logger.error(f"Error updating password for user {user_id}: {str(e)}")
            await self.session.rollback()
            raise

    async def update_last_login(self, user_id: str) -> User:
        """
        Update user's last login timestamp (for audit trail).

        Args:
            user_id: User UUID

        Returns:
            Updated User object
        """
        try:
            user = await self.find_by_id(user_id)
            if not user:
                logger.warning(f"Last login update for non-existent user: {user_id}")
                return None

            user.last_login = datetime.utcnow()
            await self.session.flush()

            logger.info(f"Last login updated for user {user_id}")
            return user

        except Exception as e:
            logger.error(f"Error updating last login for user {user_id}: {str(e)}")
            await self.session.rollback()
            raise

    async def update_mfa(
        self,
        user_id: str,
        mfa_enabled: bool,
        mfa_secret_encrypted: Optional[str] = None,
    ) -> User:
        """
        Update MFA settings for user.

        Args:
            user_id: User UUID
            mfa_enabled: Whether MFA is enabled
            mfa_secret_encrypted: Encrypted TOTP secret (None to disable)

        Returns:
            Updated User object
        """
        try:
            user = await self.find_by_id(user_id)
            if not user:
                logger.warning(f"MFA update for non-existent user: {user_id}")
                return None

            user.mfa_enabled = mfa_enabled
            user.mfa_secret_encrypted = mfa_secret_encrypted
            user.updated_at = datetime.utcnow()

            await self.session.flush()

            status = "enabled" if mfa_enabled else "disabled"
            logger.info(f"MFA {status} for user {user_id}")
            return user

        except Exception as e:
            logger.error(f"Error updating MFA for user {user_id}: {str(e)}")
            await self.session.rollback()
            raise

    async def soft_delete(self, user_id: str) -> User:
        """
        Soft delete user (GDPR compliance).
        Marks user as deleted without removing data.

        Args:
            user_id: User UUID

        Returns:
            Updated User object
        """
        try:
            user = await self.find_by_id(user_id)
            if not user:
                logger.warning(f"Soft delete for non-existent user: {user_id}")
                return None

            user.is_deleted = True
            user.deleted_at = datetime.utcnow()
            user.updated_at = datetime.utcnow()

            await self.session.flush()

            logger.info(f"User soft-deleted: {user_id}")
            return user

        except Exception as e:
            logger.error(f"Error soft-deleting user {user_id}: {str(e)}")
            await self.session.rollback()
            raise

    async def update_role(self, user_id: str, new_role: UserRole) -> User:
        """
        Update user role (admin operation).

        Args:
            user_id: User UUID
            new_role: New UserRole

        Returns:
            Updated User object
        """
        try:
            user = await self.find_by_id(user_id)
            if not user:
                logger.warning(f"Role update for non-existent user: {user_id}")
                return None

            old_role = user.role
            user.role = new_role
            user.updated_at = datetime.utcnow()

            await self.session.flush()

            logger.info(f"User role updated: {user_id} ({old_role.value} -> {new_role.value})")
            return user

        except Exception as e:
            logger.error(f"Error updating role for user {user_id}: {str(e)}")
            await self.session.rollback()
            raise
