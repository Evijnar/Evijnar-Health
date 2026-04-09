# apps/api/app/repositories/hospital.py
"""
Repository for hospital database operations.
Handles CRUD operations for GlobalHospital entities.
"""

from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import GlobalHospital
import logging

logger = logging.getLogger("evijnar.repo.hospital")


class HospitalRepository:
    """Data access layer for hospitals"""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def find_by_source_id(self, source_id: str) -> Optional[GlobalHospital]:
        """Find hospital by source_id (for idempotency check)"""
        try:
            result = await self.session.execute(
                select(GlobalHospital).where(GlobalHospital.source_id == source_id)
            )
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error finding hospital by source_id {source_id}: {str(e)}")
            raise

    async def find_by_name_and_location(
        self, name: str, city: str, state_province: str, country_code: str
    ) -> Optional[GlobalHospital]:
        """Find hospital by name and location (alternative idempotency check)"""
        try:
            result = await self.session.execute(
                select(GlobalHospital).where(
                    (GlobalHospital.name == name)
                    & (GlobalHospital.city == city)
                    & (GlobalHospital.state_province == state_province)
                    & (GlobalHospital.country_code == country_code)
                )
            )
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error finding hospital by location: {str(e)}")
            raise

    async def create(self, hospital: GlobalHospital) -> GlobalHospital:
        """Create new hospital record"""
        try:
            self.session.add(hospital)
            await self.session.flush()
            logger.info(f"Created hospital: {hospital.id} - {hospital.name}")
            return hospital
        except Exception as e:
            logger.error(f"Error creating hospital: {str(e)}")
            raise

    async def update(self, hospital: GlobalHospital) -> GlobalHospital:
        """Update existing hospital record"""
        try:
            await self.session.merge(hospital)
            await self.session.flush()
            logger.info(f"Updated hospital: {hospital.id} - {hospital.name}")
            return hospital
        except Exception as e:
            logger.error(f"Error updating hospital: {str(e)}")
            raise

    async def get_by_id(self, hospital_id: str) -> Optional[GlobalHospital]:
        """Get hospital by ID"""
        try:
            result = await self.session.execute(
                select(GlobalHospital).where(GlobalHospital.id == hospital_id)
            )
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error getting hospital {hospital_id}: {str(e)}")
            raise
