# apps/api/app/services/data_ingestion/ingestion_engine.py
"""
Ingestion engine - orchestrates the full pipeline:
Loader → Mapper → Database Write → HIPAA Audit Logging
"""

import logging
import json
from typing import List, Optional, Dict, Any
from datetime import datetime
import asyncio

from sqlalchemy.exc import IntegrityError

from .models import (
    RawHospitalData,
    NormalizedHospitalData,
    NormalizedProcedureData,
    NormalizedPriceNormalizerData,
    IngestReport,
    IngestError as IngestErrorModel,
    IngestSource,
    IngestMetrics,
)
from .errors import IngestError, DatabaseError, EngineError
from .loaders import HHSLoader, EHDSLoader, ABDMLoader, JsonLoader
from .mappers import HospitalMapper, ProcedureMapper, NormalizerMapper
from ...utils.llm_client import get_llm_client
from ...repositories import (
    HospitalRepository,
    ProcedureRepository,
    NormalizerRepository,
    AuditRepository,
)
from ...models import (
    GlobalHospital,
    ProcedurePrice,
    PriceNormalizer,
)
from ...db import get_session_factory

logger = logging.getLogger("evijnar.ingest.engine")


class DataIngestionEngine:
    """
    Orchestrates the entire data ingestion pipeline.
    Handles loading, mapping, validation, and database persistence.
    """

    def __init__(self, batch_size: int = 100, max_concurrent_llm: int = 5):
        """
        Initialize ingestion engine.

        Args:
            batch_size: Records per batch
            max_concurrent_llm: Max concurrent LLM calls
        """
        self.batch_size = batch_size
        self.max_concurrent_llm = max_concurrent_llm

        # Initialize mappers and loaders
        self.hospital_mapper = HospitalMapper()
        self.procedure_mapper = ProcedureMapper()
        self.normalizer_mapper = NormalizerMapper()

        # Track ingestion state
        self.report: Optional[IngestReport] = None
        self.llm_client = None

    async def initialize(self):
        """Initialize engine and dependencies"""
        await self.hospital_mapper.initialize()
        await self.procedure_mapper.initialize()
        await self.normalizer_mapper.initialize()
        self.llm_client = await get_llm_client()
        logger.info("DataIngestionEngine initialized")

    async def ingest_file(
        self,
        filepath: str,
        source: IngestSource,
        dry_run: bool = False,
    ) -> IngestReport:
        """
        Ingest data from a file.

        Args:
            filepath: Path to JSON file
            source: Data source (HHS, EHDS, ABDM)
            dry_run: If True, don't write to database

        Returns:
            IngestReport with results

        Raises:
            IngestError: If ingestion fails
        """
        try:
            logger.info(f"Starting ingestion from {filepath} (source: {source.value})")

            # Create report
            self.report = IngestReport(
                source=source,
                filename=filepath,
            )

            # Step 1: Load file
            logger.info("Step 1: Loading file...")
            loader = self._get_loader(source)
            raw_data = loader.load_file(filepath)
            self.report.total_records = len(raw_data)

            # Step 2: Parse records
            logger.info("Step 2: Parsing records...")
            raw_hospitals = loader.parse_records(raw_data)

            # Step 3: Map and ingest
            logger.info(f"Step 3: Processing {len(raw_hospitals)} hospitals...")
            await self._process_hospitals(raw_hospitals, dry_run)

            # Step 4: Finalize
            self.report.end_time = datetime.utcnow()
            self.report.processing_time_seconds = (
                self.report.end_time - self.report.start_time
            ).total_seconds()

            logger.info(
                f"Ingestion complete: {self.report.succeeded} succeeded, "
                f"{self.report.failed} failed, {self.report.skipped} skipped"
            )

            return self.report

        except Exception as e:
            logger.error(f"Ingestion failed: {str(e)}")
            if self.report:
                self.report.end_time = datetime.utcnow()
                self.report.errors.append(
                    IngestErrorModel(
                        source_id="ENGINE",
                        error_message=str(e),
                        error_type="ENGINE_ERROR",
                    )
                )
            raise EngineError(f"Ingestion failed: {str(e)}")

    async def _process_hospitals(self, raw_hospitals: List[RawHospitalData], dry_run: bool = False):
        """
        Process list of raw hospitals through mapping and database write.

        Args:
            raw_hospitals: List of raw hospital data
            dry_run: If True, don't persist to database
        """
        for raw_hospital in raw_hospitals:
            try:
                # Map hospital
                normalized_hospital = await self.hospital_mapper.map_hospital(raw_hospital)

                # Map procedures
                normalized_procedures = await self.procedure_mapper.map_procedures(
                    raw_hospital.procedures + [
                        dept_proc
                        for dept in raw_hospital.departments
                        for dept_proc in dept.procedures
                    ]
                )

                # Map normalizers (CPT codes)
                normalizers_to_create = []
                for proc in normalized_procedures:
                    if proc.cpt_code:
                        try:
                            normalizer = await self.normalizer_mapper.map_cpt_code(
                                proc.cpt_code,
                                f"{proc.clinical_category} - {proc.complexity_score}",
                            )
                            normalizers_to_create.append(normalizer)
                        except Exception as e:
                            logger.warning(f"Failed to map CPT {proc.cpt_code}: {str(e)}")
                            continue

                # Write to database (if not dry run)
                if not dry_run:
                    await self._write_to_database(normalized_hospital, normalized_procedures, normalizers_to_create)

                self.report.succeeded += 1
                self.report.hospitals_created += 1
                self.report.procedures_created += len(normalized_procedures)
                self.report.normalizers_created += len(normalizers_to_create)

                # Log success
                await self._log_ingest_success(raw_hospital.source_id)

            except Exception as e:
                logger.warning(f"Failed to process hospital {raw_hospital.source_id}: {str(e)}")
                self.report.failed += 1
                self.report.errors.append(
                    IngestErrorModel(
                        source_id=raw_hospital.source_id,
                        error_message=str(e),
                        error_type=type(e).__name__,
                        raw_data_snippet=raw_hospital.model_dump(exclude=["raw_json"]),
                    )
                )
                await self._log_ingest_failure(raw_hospital.source_id, str(e))

                continue

    async def _write_to_database(
        self,
        hospital: NormalizedHospitalData,
        procedures: List[NormalizedProcedureData],
        normalizers: List[NormalizedPriceNormalizerData],
    ):
        """
        Write normalized data to PostgreSQL database atomically.

        Handles idempotency for hospitals and normalizers, creates procedures,
        and logs all operations for HIPAA compliance.

        Args:
            hospital: Normalized hospital data
            procedures: Normalized procedures
            normalizers: Normalized price mappings

        Raises:
            DatabaseError: If database operation fails
        """
        # Get session factory and create a new session
        session_factory = get_session_factory()

        async with session_factory() as session:
            try:
                # Initialize repositories
                hospital_repo = HospitalRepository(session)
                procedure_repo = ProcedureRepository(session)
                normalizer_repo = NormalizerRepository(session)
                audit_repo = AuditRepository(session)

                # Step 1: Check for existing hospital (idempotency)
                existing_hospital = await hospital_repo.find_by_source_id(hospital.source_id)

                if existing_hospital:
                    logger.info(f"Hospital {hospital.name} already exists (source_id: {hospital.source_id}). Skipping...")
                    self.report.skipped += 1
                    await session.commit()
                    return

                # Step 2: Create or update hospital
                db_hospital = GlobalHospital(
                    name=hospital.name,
                    hospital_type=hospital.hospital_type,
                    country_code=hospital.country_code,
                    state_province=hospital.state_province,
                    city=hospital.city,
                    postal_code=hospital.postal_code,
                    phone_primary=hospital.phone_primary,
                    email=hospital.email,
                    website_url=hospital.website_url,
                    jci_accredited=hospital.jci_accredited,
                    jci_certificate_url=hospital.jci_certificate_url,
                    jci_expires_at=hospital.jci_expires_at,
                    nabh_accredited=hospital.nabh_accredited,
                    nabh_certificate_url=hospital.nabh_certificate_url,
                    nabh_expires_at=hospital.nabh_expires_at,
                    avg_quality_score=hospital.avg_quality_score,
                    complication_rate=hospital.complication_rate,
                    readmission_rate=hospital.readmission_rate,
                    patient_reviews_count=hospital.patient_reviews_count,
                    price_data_source=hospital.price_data_source.value,
                    price_data_verified_at=hospital.price_data_verified_at,
                    source_id=hospital.source_id,
                )
                created_hospital = await hospital_repo.create(db_hospital)
                logger.info(f"Created hospital: {created_hospital.id} - {created_hospital.name}")

                # Step 3: Create normalizers (medical code mappings)
                # These are deduplicated by CPT code at the repository level
                created_normalizers_map = {}  # Map CPT code -> normalizer_id

                for normalizer_data in normalizers:
                    try:
                        db_normalizer = PriceNormalizer(
                            cpt_code=normalizer_data.cpt_code,
                            cpt_description=normalizer_data.cpt_description,
                            icd10_code=normalizer_data.icd10_code,
                            icd10_description=normalizer_data.icd10_description,
                            uhi_code=normalizer_data.uhi_code,
                            ehds_identifier=normalizer_data.ehds_identifier,
                            clinical_category=normalizer_data.clinical_category,
                            complexity_score=normalizer_data.complexity_score,
                            us_median_cost_usd=normalizer_data.us_median_cost_usd,
                        )
                        created_normalizer = await normalizer_repo.create(db_normalizer)
                        created_normalizers_map[normalizer_data.cpt_code] = created_normalizer.id
                        logger.debug(f"Normalizer: CPT {normalizer_data.cpt_code} -> ID {created_normalizer.id}")
                    except Exception as e:
                        logger.warning(f"Failed to create normalizer for CPT {normalizer_data.cpt_code}: {str(e)}")
                        continue

                # Step 4: Create procedures, linking to normalizers and hospital
                for procedure_data in procedures:
                    try:
                        # Get normalizer_id if CPT code exists
                        normalizer_id = None
                        if procedure_data.cpt_code and procedure_data.cpt_code in created_normalizers_map:
                            normalizer_id = created_normalizers_map[procedure_data.cpt_code]

                        db_procedure = ProcedurePrice(
                            hospital_id=created_hospital.id,
                            normalizer_id=normalizer_id,
                            clinical_category=procedure_data.clinical_category,
                            complexity_score=procedure_data.complexity_score,
                            base_price=procedure_data.base_price,
                            facility_fee=procedure_data.facility_fee,
                            anesthesia_fee=procedure_data.anesthesia_fee,
                            surgeon_fee=procedure_data.surgeon_fee,
                            currency_code=procedure_data.currency_code,
                            success_rate=procedure_data.success_rate,
                            complication_rate=procedure_data.complication_rate,
                            data_source=procedure_data.data_source.value,
                            verified_at=procedure_data.verified_at,
                        )
                        created_procedure = await procedure_repo.create(db_procedure)
                        logger.debug(f"Procedure: {procedure_data.clinical_category} in hospital {created_hospital.id}")
                    except Exception as e:
                        logger.warning(f"Failed to create procedure for hospital {created_hospital.id}: {str(e)}")
                        continue

                # Step 5: Log success to HIPAA audit trail
                await audit_repo.log_ingest_success(
                    user_id=None,  # System operation
                    hospital_id=created_hospital.id,
                    source=hospital.price_data_source.value,
                )
                logger.info(f"Database write complete for hospital {created_hospital.name}")

                # Commit transaction
                await session.commit()

            except IntegrityError as e:
                logger.error(f"Integrity constraint violation: {str(e)}")
                await session.rollback()
                raise DatabaseError(f"Duplicate or constraint violation: {str(e)}")
            except Exception as e:
                logger.error(f"Error writing to database: {str(e)}")
                await session.rollback()
                raise DatabaseError(f"Database write failed: {str(e)}")

    async def _log_ingest_success(self, source_id: str):
        """
        Log successful ingestion to HIPAA audit trail.

        Persists to database via AuditRepository and logs to file.

        Args:
            source_id: Source hospital identifier
        """
        # Log to console/file
        audit_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "action": "INGEST_SUCCESS",
            "resource_type": "Hospital",
            "resource_id": source_id,
            "source": "DataIngestionEngine",
        }
        logger.info(f"HIPAA_AUDIT: {json.dumps(audit_entry)}")

        # Also persist to database
        try:
            session_factory = get_session_factory()
            async with session_factory() as session:
                audit_repo = AuditRepository(session)
                await audit_repo.log_ingest_success(
                    user_id=None,  # System operation
                    hospital_id=source_id,
                    source="DataIngestionEngine",
                )
                await session.commit()
        except Exception as e:
            logger.warning(f"Failed to persist audit log to database: {str(e)}")

    async def _log_ingest_failure(self, source_id: str, error: str):
        """
        Log failed ingestion to HIPAA audit trail.

        Persists to database via AuditRepository and logs to file.

        Args:
            source_id: Source hospital identifier
            error: Error message (truncated to 100 chars)
        """
        # Log to console/file
        audit_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "action": "INGEST_FAILURE",
            "resource_type": "Hospital",
            "resource_id": source_id,
            "source": "DataIngestionEngine",
            "error": error[:100],
        }
        logger.warning(f"HIPAA_AUDIT: {json.dumps(audit_entry)}")

        # Also persist to database
        try:
            session_factory = get_session_factory()
            async with session_factory() as session:
                audit_repo = AuditRepository(session)
                await audit_repo.log_ingest_failure(
                    user_id=None,  # System operation
                    hospital_id=source_id,
                    error_message=error[:500],  # Store more detail in DB than log
                )
                await session.commit()
        except Exception as e:
            logger.warning(f"Failed to persist audit log to database: {str(e)}")

    def _get_loader(self, source: IngestSource) -> JsonLoader:
        """Get appropriate loader for source"""
        if source == IngestSource.HHS_TRANSPARENCY:
            return HHSLoader()
        elif source == IngestSource.EHDS:
            return EHDSLoader()
        elif source == IngestSource.ABDM:
            return ABDMLoader()
        else:
            raise EngineError(f"Unknown source: {source}")

    def get_report(self) -> Optional[IngestReport]:
        """Get current ingestion report"""
        return self.report

    def get_llm_usage(self) -> Dict[str, Any]:
        """Get LLM usage statistics"""
        if self.llm_client:
            return self.llm_client.get_usage_stats()
        return {}
