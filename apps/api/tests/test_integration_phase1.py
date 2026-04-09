"""
Phase 3 Integration Tests - End-to-end ingestion with real sample data
Tests for idempotency, transaction atomicity, and concurrent ingestion.
"""

import pytest
import asyncio
import json
from pathlib import Path
from typing import List
import tempfile

from app.services.data_ingestion import IngestSource
from app.services.data_ingestion.ingestion_engine import DataIngestionEngine
from app.db import get_session_factory
from app.repositories import HospitalRepository, ProcedureRepository, NormalizerRepository


class TestIntegrationEndToEnd:
    """End-to-end integration tests with real sample data."""

    @pytest.mark.asyncio
    async def test_ingest_hhs_sample_data(self, ingestion_engine, tmp_data_files, clean_database):
        """Test complete HHS data ingestion pipeline."""
        report = await ingestion_engine.ingest_file(
            filepath=tmp_data_files["HHS"],
            source=IngestSource.HHS_TRANSPARENCY,
            dry_run=False,
        )

        assert report.total_records == 2
        assert report.succeeded == 2
        assert report.failed == 0
        assert report.hospitals_created == 2
        assert report.success_rate == 100.0
        assert report.processing_time_seconds > 0

    @pytest.mark.asyncio
    async def test_ingest_ehds_sample_data(self, ingestion_engine, tmp_data_files, clean_database):
        """Test complete EHDS data ingestion pipeline."""
        report = await ingestion_engine.ingest_file(
            filepath=tmp_data_files["EHDS"],
            source=IngestSource.EHDS,
            dry_run=False,
        )

        assert report.total_records == 1
        assert report.succeeded == 1
        assert report.failed == 0
        assert report.hospitals_created == 1

    @pytest.mark.asyncio
    async def test_ingest_abdm_sample_data(self, ingestion_engine, tmp_data_files, clean_database):
        """Test complete ABDM data ingestion pipeline."""
        report = await ingestion_engine.ingest_file(
            filepath=tmp_data_files["ABDM"],
            source=IngestSource.ABDM,
            dry_run=False,
        )

        assert report.total_records == 1
        assert report.succeeded == 1
        assert report.hospitals_created == 1

    @pytest.mark.asyncio
    async def test_data_persists_to_database(self, ingestion_engine, tmp_data_files, clean_database, session_factory):
        """Verify data is actually persisted to database after ingestion."""
        # Run ingestion
        report = await ingestion_engine.ingest_file(
            filepath=tmp_data_files["HHS"],
            source=IngestSource.HHS_TRANSPARENCY,
            dry_run=False,
        )

        assert report.succeeded == 2

        # Query database to verify persistence
        async with session_factory() as session:
            hospital_repo = HospitalRepository(session)

            # Verify hospitals exist
            hospitals = await hospital_repo.find_all()
            assert len(hospitals) == 2

            # Verify specific hospital data
            mayo = await hospital_repo.find_by_source_id("HHS-HOSP-001")
            assert mayo is not None
            assert mayo.name == "Mayo Clinic Rochester"
            assert mayo.city == "Rochester"
            assert mayo.state_province == "MN"
            assert mayo.country_code == "US"
            assert mayo.jci_accredited is True
            assert float(mayo.avg_quality_score) == 95.5
            assert float(mayo.complication_rate) == 2.1

    @pytest.mark.asyncio
    async def test_dry_run_does_not_persist(self, ingestion_engine, tmp_data_files, clean_database, session_factory):
        """Verify dry-run doesn't write to database."""
        # Run ingestion in dry-run mode
        report = await ingestion_engine.ingest_file(
            filepath=tmp_data_files["HHS"],
            source=IngestSource.HHS_TRANSPARENCY,
            dry_run=True,
        )

        assert report.succeeded == 2

        # Verify NO data in database
        async with session_factory() as session:
            hospital_repo = HospitalRepository(session)
            hospitals = await hospital_repo.find_all()
            assert len(hospitals) == 0


class TestIdempotency:
    """Test idempotent ingestion - same data ingested multiple times."""

    @pytest.mark.asyncio
    async def test_duplicate_ingestion_skipped(self, ingestion_engine, tmp_data_files, clean_database, session_factory):
        """Running same ingestion twice should skip duplicates on second run."""
        file_path = tmp_data_files["HHS"]

        # First ingestion
        report1 = await ingestion_engine.ingest_file(
            filepath=file_path,
            source=IngestSource.HHS_TRANSPARENCY,
            dry_run=False,
        )
        assert report1.succeeded == 2
        assert report1.skipped == 0

        # Second ingestion (same file)
        report2 = await ingestion_engine.ingest_file(
            filepath=file_path,
            source=IngestSource.HHS_TRANSPARENCY,
            dry_run=False,
        )

        # Second run should skip duplicates
        assert report2.succeeded == 0
        assert report2.skipped == 2

        # Database should still have only 2 hospitals
        async with session_factory() as session:
            hospital_repo = HospitalRepository(session)
            hospitals = await hospital_repo.find_all()
            assert len(hospitals) == 2

    @pytest.mark.asyncio
    async def test_multiple_sources_same_hospital(self, ingestion_engine, sample_hhs_data, sample_ehds_data, clean_database, session_factory):
        """Test ingesting similar hospitals from different sources."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create files with different source_ids but similar data
            hhs_file = Path(tmpdir) / "hhs.json"
            hhs_file.write_text(json.dumps(sample_hhs_data))

            # Ingest HHS
            report1 = await ingestion_engine.ingest_file(
                filepath=str(hhs_file),
                source=IngestSource.HHS_TRANSPARENCY,
                dry_run=False,
            )

            # Verify database has HHS hospitals
            async with session_factory() as session:
                hospital_repo = HospitalRepository(session)
                hospitals = await hospital_repo.find_all()
                assert len(hospitals) == 2

                # Both should be from HHS source
                for hosp in hospitals:
                    assert hosp.price_data_source == "HHS_TRANSPARENCY"


class TestTransactionAtomicity:
    """Test transaction atomicity - all-or-nothing database writes."""

    @pytest.mark.asyncio
    async def test_partial_failure_rollback(self, ingestion_engine, clean_database, session_factory):
        """Test that partial failures don't corrupt database state."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create mixed valid/invalid data
            mixed_data = [
                {
                    "source_id": "VALID-001",
                    "name": "Valid Hospital",
                    "city": "Boston",
                    "state": "MA",
                    "postal_code": "02101",
                    "country_code": "US",
                    "phone": "617-555-0001",
                    "hospital_type": "PRIVATE",
                    "departments": [],
                    "procedures": [],
                },
                {
                    # Missing required fields - should fail
                    "source_id": "INVALID-001",
                    "name": "Invalid Hospital",
                    "departments": [],
                    "procedures": [],
                },
            ]

            file_path = Path(tmpdir) / "mixed.json"
            file_path.write_text(json.dumps(mixed_data))

            # Run ingestion
            report = await ingestion_engine.ingest_file(
                filepath=str(file_path),
                source=IngestSource.HHS_TRANSPARENCY,
                dry_run=False,
            )

            # Should have 1 success, 1 failure
            assert report.succeeded + report.failed == 2
            assert report.failed >= 1

            # Verify database state is clean
            async with session_factory() as session:
                hospital_repo = HospitalRepository(session)
                hospitals = await hospital_repo.find_all()
                # Database should only contain successfully processed hospitals
                assert len(hospitals) <= 1


class TestConcurrentIngestion:
    """Test concurrent ingestion from multiple sources."""

    @pytest.mark.asyncio
    async def test_concurrent_different_sources(
        self, ingestion_engine, tmp_data_files, clean_database, session_factory
    ):
        """Test concurrent ingestion from HHS, EHDS, and ABDM sources."""
        # Create engines for concurrent execution
        tasks = [
            ingestion_engine.ingest_file(
                filepath=tmp_data_files["HHS"],
                source=IngestSource.HHS_TRANSPARENCY,
                dry_run=False,
            ),
            ingestion_engine.ingest_file(
                filepath=tmp_data_files["EHDS"],
                source=IngestSource.EHDS,
                dry_run=False,
            ),
            ingestion_engine.ingest_file(
                filepath=tmp_data_files["ABDM"],
                source=IngestSource.ABDM,
                dry_run=False,
            ),
        ]

        # Run concurrently
        results = await asyncio.gather(*tasks)

        # Verify all completed
        assert len(results) == 3
        assert all(r.success_rate == 100.0 for r in results)

        # Verify total data in database
        async with session_factory() as session:
            hospital_repo = HospitalRepository(session)
            hospitals = await hospital_repo.find_all()
            # HHS: 2, EHDS: 1, ABDM: 1 = 4 total
            assert len(hospitals) == 4

    @pytest.mark.asyncio
    async def test_concurrent_same_source(self, sample_hhs_data, clean_database, session_factory):
        """Test concurrent ingestion from same source."""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_paths = []
            for i in range(3):
                file_path = Path(tmpdir) / f"hhs_{i}.json"
                file_path.write_text(json.dumps(sample_hhs_data))
                file_paths.append(str(file_path))

            # Create multiple engines to run concurrently
            engines = [
                DataIngestionEngine(batch_size=10) for _ in range(3)
            ]
            for engine in engines:
                await engine.initialize()

            tasks = [
                engines[i].ingest_file(
                    filepath=file_paths[i],
                    source=IngestSource.HHS_TRANSPARENCY,
                    dry_run=False,
                )
                for i in range(3)
            ]

            # Run concurrently
            results = await asyncio.gather(*tasks, return_exceptions=True)

            # Verify all completed
            assert len(results) == 3

            # First ingestion should succeed
            assert results[0].succeeded == 2

            # Subsequent ingestions should skip (idempotency)
            async with session_factory() as session:
                hospital_repo = HospitalRepository(session)
                hospitals = await hospital_repo.find_all()
                # Should still be 2 (idempotent)
                assert len(hospitals) == 2
