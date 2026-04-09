# apps/api/app/repositories/normalizer.py
"""
Repository for price normalizer database operations.
Handles CRUD for medical code mappings (CPT → ICD-10 → UHI).
"""

from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from app.models import PriceNormalizer
import logging

logger = logging.getLogger("evijnar.repo.normalizer")


class NormalizerRepository:
    """Data access layer for price normalizers"""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def find_by_cpt_code(self, cpt_code: str) -> Optional[PriceNormalizer]:
        """Find normalizer by CPT code"""
        try:
            result = await self.session.execute(
                select(PriceNormalizer).where(PriceNormalizer.cpt_code == cpt_code)
            )
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error finding normalizer by CPT code {cpt_code}: {str(e)}")
            raise

    async def find_by_icd10_code(self, icd10_code: str) -> Optional[PriceNormalizer]:
        """Find normalizer by ICD-10 code"""
        try:
            result = await self.session.execute(
                select(PriceNormalizer).where(PriceNormalizer.icd10_code == icd10_code)
            )
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error finding normalizer by ICD-10 code {icd10_code}: {str(e)}")
            raise

    async def create(self, normalizer: PriceNormalizer) -> PriceNormalizer:
        """Create new normalizer (returns existing if duplicate CPT code)"""
        try:
            # Check if already exists
            existing = await self.find_by_cpt_code(normalizer.cpt_code)
            if existing:
                logger.info(f"Normalizer for CPT {normalizer.cpt_code} already exists")
                return existing

            self.session.add(normalizer)
            await self.session.flush()
            logger.info(f"Created normalizer: {normalizer.id} - CPT {normalizer.cpt_code}")
            return normalizer

        except IntegrityError as e:
            # Handle duplicate key error
            logger.warning(f"Duplicate normalizer CPT code: {normalizer.cpt_code}")
            await self.session.rollback()
            # Retry fetch
            return await self.find_by_cpt_code(normalizer.cpt_code)
        except Exception as e:
            logger.error(f"Error creating normalizer: {str(e)}")
            raise

    async def get_by_id(self, normalizer_id: str) -> Optional[PriceNormalizer]:
        """Get normalizer by ID"""
        try:
            result = await self.session.execute(
                select(PriceNormalizer).where(PriceNormalizer.id == normalizer_id)
            )
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error getting normalizer {normalizer_id}: {str(e)}")
            raise
