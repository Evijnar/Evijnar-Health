# apps/api/app/repositories/audit.py
"""
Repository for audit log database operations.
Handles HIPAA audit trail logging.
"""

from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import AuditLog
from datetime import datetime
import logging

logger = logging.getLogger("evijnar.repo.audit")


class AuditRepository:
    """Data access layer for audit logs"""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def log_action(
        self,
        user_id: Optional[str],
        action: str,
        resource_type: str,
        resource_id: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> AuditLog:
        """Create audit log entry for an action"""
        try:
            # Note: user_id can be None for system operations like ingestion
            audit_entry = AuditLog(
                user_id=user_id or "system",
                action=action,
                resource_type=resource_type,
                resource_id=resource_id,
                ip_address=ip_address,
                user_agent=user_agent,
                created_at=datetime.utcnow(),
            )
            self.session.add(audit_entry)
            await self.session.flush()
            logger.debug(f"Logged audit action: {action} on {resource_type} {resource_id}")
            return audit_entry
        except Exception as e:
            logger.error(f"Error logging audit action: {str(e)}")
            raise

    async def log_ingest_success(
        self,
        user_id: Optional[str],
        hospital_id: str,
        source: str,
    ) -> AuditLog:
        """Log successful ingestion"""
        return await self.log_action(
            user_id=user_id,
            action="INGEST_SUCCESS",
            resource_type="Hospital",
            resource_id=hospital_id,
        )

    async def log_ingest_failure(
        self,
        user_id: Optional[str],
        hospital_id: str,
        error_message: str,
    ) -> AuditLog:
        """Log failed ingestion"""
        return await self.log_action(
            user_id=user_id,
            action="INGEST_FAILURE",
            resource_type="Hospital",
            resource_id=hospital_id,
        )
