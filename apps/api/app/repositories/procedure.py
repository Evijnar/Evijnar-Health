# apps/api/app/repositories/procedure.py
"""
Repository for procedure pricing database operations.
Handles CRUD for hospital-specific procedure pricing.
"""

from typing import Optional, List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import ProcedurePrice
import logging

logger = logging.getLogger("evijnar.repo.procedure")


class ProcedureRepository:
    """Data access layer for procedures"""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, procedure: ProcedurePrice) -> ProcedurePrice:
        """Create new procedure price record"""
        try:
            self.session.add(procedure)
            await self.session.flush()
            logger.info(
                f"Created procedure: {procedure.id} - "
                f"Hospital {procedure.hospital_id}, Normalizer {procedure.normalizer_id}"
            )
            return procedure
        except Exception as e:
            logger.error(f"Error creating procedure: {str(e)}")
            raise

    async def get_by_id(self, procedure_id: str) -> Optional[ProcedurePrice]:
        """Get procedure by ID"""
        try:
            result = await self.session.execute(
                select(ProcedurePrice).where(ProcedurePrice.id == procedure_id)
            )
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error getting procedure {procedure_id}: {str(e)}")
            raise

    async def find_by_hospital_and_normalizer(
        self, hospital_id: str, normalizer_id: str
    ) -> Optional[ProcedurePrice]:
        """Find procedure for specific hospital and normalizer combination"""
        try:
            result = await self.session.execute(
                select(ProcedurePrice).where(
                    (ProcedurePrice.hospital_id == hospital_id)
                    & (ProcedurePrice.normalizer_id == normalizer_id)
                )
            )
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error finding procedure: {str(e)}")
            raise

    async def list_by_hospital(self, hospital_id: str) -> List[ProcedurePrice]:
        """Get all procedures for a hospital"""
        try:
            result = await self.session.execute(
                select(ProcedurePrice).where(ProcedurePrice.hospital_id == hospital_id)
            )
            return result.scalars().all()
        except Exception as e:
            logger.error(f"Error listing procedures for hospital {hospital_id}: {str(e)}")
            raise
