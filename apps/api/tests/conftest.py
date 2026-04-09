"""
Pytest configuration and fixtures for integration tests.
Handles database setup/teardown and test data generation.
"""

import asyncio
import pytest
from pathlib import Path
import json
import tempfile
from typing import AsyncGenerator

# Add parent directory to path for imports
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.data_ingestion.ingestion_engine import DataIngestionEngine
from app.services.data_ingestion import IngestSource
from app.db import get_session_factory, SessionLocal


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def session_factory():
    """Provide database session factory."""
    factory = get_session_factory()
    yield factory


@pytest.fixture
async def ingestion_engine():
    """Initialize and provide DataIngestionEngine."""
    engine = DataIngestionEngine(batch_size=10)
    await engine.initialize()
    yield engine


@pytest.fixture
def sample_hhs_data():
    """Generate sample HHS Transparency data."""
    return [
        {
            "source_id": "HHS-HOSP-001",
            "name": "Mayo Clinic Rochester",
            "address": "200 1st St SW",
            "city": "Rochester",
            "state": "MN",
            "postal_code": "55905",
            "country_code": "US",
            "phone": "507-284-2511",
            "email": "contact@mayo.edu",
            "website": "https://www.mayo.edu",
            "hospital_type": "TEACHING",
            "jci_accredited": True,
            "jci_certificate_url": "https://exemplarjci.org/mayo",
            "jci_expires_at": "2026-12-31T23:59:59Z",
            "nabh_accredited": False,
            "avg_quality_score": 95.5,
            "complication_rate": 2.1,
            "readmission_rate": 1.8,
            "patient_reviews_count": 5200,
            "price_data_source": "HHS_TRANSPARENCY",
            "price_data_verified_at": "2024-01-15T10:00:00Z",
            "departments": [
                {
                    "name": "Cardiology",
                    "procedures": [
                        {
                            "name": "Heart Bypass Surgery",
                            "cpt_code": "33533",
                            "base_price": 75000,
                            "facility_fee": 15000,
                            "anesthesia_fee": 3000,
                            "surgeon_fee": 18000,
                            "currency_code": "USD",
                            "success_rate": 97.5,
                            "complication_rate": 1.2,
                            "clinical_category": "CARDIAC_SURGERY",
                            "complexity_score": 9.5,
                        }
                    ],
                }
            ],
            "procedures": [
                {
                    "name": "General Consultation",
                    "cpt_code": "99215",
                    "base_price": 250,
                    "facility_fee": 50,
                    "anesthesia_fee": 0,
                    "surgeon_fee": 150,
                    "currency_code": "USD",
                    "success_rate": 100.0,
                    "complication_rate": 0.0,
                    "clinical_category": "CONSULTATION",
                    "complexity_score": 1.0,
                }
            ],
        },
        {
            "source_id": "HHS-HOSP-002",
            "name": "Cleveland Clinic",
            "address": "9500 Euclid Ave",
            "city": "Cleveland",
            "state": "OH",
            "postal_code": "44195",
            "country_code": "US",
            "phone": "216-444-2000",
            "email": "contact@clevelandclinic.org",
            "website": "https://www.clevelandclinic.org",
            "hospital_type": "TEACHING",
            "jci_accredited": True,
            "jci_certificate_url": "https://exemplarjci.org/ccf",
            "jci_expires_at": "2026-06-30T23:59:59Z",
            "nabh_accredited": False,
            "avg_quality_score": 93.8,
            "complication_rate": 2.5,
            "readmission_rate": 2.1,
            "patient_reviews_count": 4800,
            "price_data_source": "HHS_TRANSPARENCY",
            "price_data_verified_at": "2024-01-15T10:00:00Z",
            "departments": [],
            "procedures": [],
        },
    ]


@pytest.fixture
def sample_ehds_data():
    """Generate sample EHDS (EU Health Data) data."""
    return [
        {
            "source_id": "EHDS-HOSP-001",
            "name": "Charité - Universitätsmedizin Berlin",
            "address": "Charitéplatz 1",
            "city": "Berlin",
            "state": "Berlin",
            "postal_code": "10117",
            "country_code": "DE",
            "phone": "+49 30 450",
            "email": "contact@charite.de",
            "website": "https://www.charite.de",
            "hospital_type": "TEACHING",
            "jci_accredited": False,
            "nabh_accredited": False,
            "avg_quality_score": 92.0,
            "complication_rate": 2.8,
            "readmission_rate": 2.3,
            "patient_reviews_count": 3200,
            "price_data_source": "EHDS",
            "price_data_verified_at": "2024-01-15T10:00:00Z",
            "departments": [
                {
                    "name": "Oncology",
                    "procedures": [
                        {
                            "name": "Cervical Cancer Treatment",
                            "cpt_code": None,
                            "base_price": 45000,
                            "facility_fee": 8000,
                            "anesthesia_fee": 2000,
                            "surgeon_fee": 12000,
                            "currency_code": "EUR",
                            "success_rate": 88.5,
                            "complication_rate": 3.2,
                            "clinical_category": "ONCOLOGY",
                            "complexity_score": 8.5,
                        }
                    ],
                }
            ],
            "procedures": [],
        },
    ]


@pytest.fixture
def sample_abdm_data():
    """Generate sample ABDM (India Health Data) data."""
    return [
        {
            "source_id": "ABDM-HOSP-001",
            "name": "Apollo Hospitals, Chennai",
            "address": "21 Greams Road",
            "city": "Chennai",
            "state": "Tamil Nadu",
            "postal_code": "600006",
            "country_code": "IN",
            "phone": "+91 44 2829 3333",
            "email": "contact@apollohospitals.com",
            "website": "https://www.apollohospitals.com",
            "hospital_type": "PRIVATE",
            "jci_accredited": True,
            "jci_certificate_url": "https://exemplarjci.org/apollo",
            "jci_expires_at": "2025-12-31T23:59:59Z",
            "nabh_accredited": True,
            "nabh_certificate_url": "https://www.nabh.co/apollo",
            "nabh_expires_at": "2025-08-31T23:59:59Z",
            "avg_quality_score": 91.5,
            "complication_rate": 3.1,
            "readmission_rate": 2.8,
            "patient_reviews_count": 2800,
            "price_data_source": "ABDM",
            "price_data_verified_at": "2024-01-15T10:00:00Z",
            "departments": [
                {
                    "name": "Orthopedics",
                    "procedures": [
                        {
                            "name": "Total Knee Replacement",
                            "cpt_code": "27447",
                            "base_price": 350000,  # INR
                            "facility_fee": 50000,
                            "anesthesia_fee": 15000,
                            "surgeon_fee": 80000,
                            "currency_code": "INR",
                            "success_rate": 95.2,
                            "complication_rate": 2.0,
                            "clinical_category": "ORTHOPEDICS",
                            "complexity_score": 8.0,
                        }
                    ],
                }
            ],
            "procedures": [],
        },
    ]


@pytest.fixture
def tmp_data_files(sample_hhs_data, sample_ehds_data, sample_abdm_data):
    """Create temporary JSON files with sample data."""
    files = {}

    with tempfile.TemporaryDirectory() as tmpdir:
        # HHS data
        hhs_file = Path(tmpdir) / "hhs_sample.json"
        hhs_file.write_text(json.dumps(sample_hhs_data))
        files["HHS"] = str(hhs_file)

        # EHDS data
        ehds_file = Path(tmpdir) / "ehds_sample.json"
        ehds_file.write_text(json.dumps(sample_ehds_data))
        files["EHDS"] = str(ehds_file)

        # ABDM data
        abdm_file = Path(tmpdir) / "abdm_sample.json"
        abdm_file.write_text(json.dumps(sample_abdm_data))
        files["ABDM"] = str(abdm_file)

        yield files


@pytest.fixture
async def clean_database(session_factory):
    """Clean database before and after tests."""
    # Before test
    async with session_factory() as session:
        # Truncate tables (for PostgreSQL)
        await session.execute("TRUNCATE TABLE public.global_hospitals CASCADE")
        await session.commit()

    yield

    # After test
    async with session_factory() as session:
        await session.execute("TRUNCATE TABLE public.global_hospitals CASCADE")
        await session.commit()
