# Phase 3: Integration Testing & Database Verification

**Status**: Testing Framework Ready for End-to-End Ingestion Validation

## Overview

Phase 3 provides comprehensive testing and verification for Evijnar's data ingestion pipeline. It covers:

- ✅ **End-to-end ingestion** with real sample data (HHS, EHDS, ABDM sources)
- ✅ **Idempotency testing** - same data ingested multiple times
- ✅ **Transaction atomicity** - all-or-nothing database writes
- ✅ **Concurrent ingestion** - multiple sources processed in parallel
- ✅ **Data persistence verification** - queries confirm what's in the database

## Quick Start

### 1. Run All Phase 3 Tests

```bash
cd apps/api

# Run all tests with verbose output
python -m pytest tests/test_integration_phase1.py -v

# Run with coverage report
python -m pytest tests/test_integration_phase1.py --cov=app --cov-report=html

# Use the test runner script for comprehensive report
python scripts/run_phase1_tests.py --verbose --coverage --report
```

### 2. Run Specific Test Groups

```bash
# End-to-end ingestion tests
python -m pytest tests/test_integration_phase1.py::TestIntegrationEndToEnd -v

# Idempotency tests
python -m pytest tests/test_integration_phase1.py::TestIdempotency -v

# Transaction atomicity tests
python -m pytest tests/test_integration_phase1.py::TestTransactionAtomicity -v

# Concurrent ingestion tests
python -m pytest tests/test_integration_phase1.py::TestConcurrentIngestion -v
```

### 3. Verify Database After Ingestion

```bash
# Generate comprehensive verification report
python scripts/verify_data.py

# Example output:
# Hospital Count: 4 hospitals
# Hospitals by Source:
#   - HHS_TRANSPARENCY: 2
#   - EHDS: 1
#   - ABDM: 1
# Hospitals by Country:
#   - US: 2
#   - DE: 1
#   - IN: 1
```

## Test Suite Details

### End-to-End Integration Tests (`TestIntegrationEndToEnd`)

Tests complete ingestion pipeline from file load to database persistence.

**Tests**:
- `test_ingest_hhs_sample_data` - Ingest HHS Transparency data
- `test_ingest_ehds_sample_data` - Ingest EHDS (EU) data
- `test_ingest_abdm_sample_data` - Ingest ABDM (India) data
- `test_data_persists_to_database` - Verify data actually wrote to database
- `test_dry_run_does_not_persist` - Dry-run mode doesn't affect database

**Sample Data Included**:
- Mayo Clinic Rochester (HHS) - Teaching hospital with cardiology
- Cleveland Clinic (HHS) - Large multi-specialty hospital
- Charité Berlin (EHDS) - EU teaching hospital
- Apollo Hospitals Chennai (ABDM) - India private hospital

### Idempotency Tests (`TestIdempotency`)

Ensures same data ingested multiple times produces consistent results.

**Tests**:
- `test_duplicate_ingestion_skipped` - Second ingestion skips duplicate hospitals
- `test_multiple_sources_same_hospital` - Multiple sources handled correctly

**Guarantees**:
- Re-running ingestion doesn't create duplicate records
- Database remains consistent across multiple runs
- Source ID serves as unique identifier per source

### Transaction Atomicity Tests (`TestTransactionAtomicity`)

Verifies all-or-nothing database writes (ACID compliance).

**Tests**:
- `test_partial_failure_rollback` - Invalid records don't corrupt database

**Guarantees**:
- Only valid records are persisted
- Invalid records're logged but don't affect database state
- No orphaned records or partial data

### Concurrent Ingestion Tests (`TestConcurrentIngestion`)

Tests parallel processing from multiple sources without conflicts.

**Tests**:
- `test_concurrent_different_sources` - HHS, EHDS, ABDM simultaneously
- `test_concurrent_same_source` - Same source from multiple threads
- Verifies idempotency during concurrent operations

**Guarantees**:
- Concurrent ingestion completes without conflicts
- Data integrity maintained under parallel load
- No race conditions or transaction deadlocks

## Database Verification Queries

The `verify_data.py` script provides these verification functions:

### Hospital Verification

```python
# Total hospital count
await verifier.verify_hospital_count(expected_count=4)
# Returns: {"total_hospitals": 4, "expected": 4, "matches": True}

# Hospitals by source
await verifier.verify_hospitals_by_source()
# Returns: {"HHS_TRANSPARENCY": 2, "EHDS": 1, "ABDM": 1}

# Hospitals by country
await verifier.verify_hospitals_by_country()
# Returns: {"US": 2, "DE": 1, "IN": 1}

# Accreditation status
await verifier.verify_accreditation_status()
# Returns: {"jci_accredited": 3, "nabh_accredited": 1}
```

### Procedure Verification

```python
# Total procedure count
await verifier.verify_procedure_count()
# Returns: {"total_procedures": 5, ...}

# Procedures by clinical category
await verifier.verify_procedures_by_category()
# Returns: {"CARDIAC_SURGERY": 1, "ONCOLOGY": 1, "ORTHOPEDICS": 1, ...}
```

### Data Quality Metrics

```python
# Quality metrics
await verifier.verify_data_quality()
# Returns: {
#   "hospitals_with_quality_score": 4,
#   "procedures_with_price": 5,
#   "procedures_with_success_rate": 5
# }

# Duplicate check
await verifier.verify_no_duplicates()
# Returns: {"has_duplicates": False, "duplicate_count": 0, "details": []}
```

### Audit & Compliance

```python
# HIPAA audit logs
await verifier.verify_audit_logs()
# Returns: {"ingestion_success_logs": 4, "ingestion_failure_logs": 0}

# Specific hospital details
await verifier.verify_hospital_details("HHS-HOSP-001")
# Returns detailed hospital information with procedures
```

### Complete Verification Report

```python
# Generate complete report
report = await verifier.generate_verification_report()
# Returns comprehensive dict with all verification results
```

## Sample Data Specifications

### HHS Transparency Data

```json
[
  {
    "source_id": "HHS-HOSP-001",
    "name": "Mayo Clinic Rochester",
    "city": "Rochester",
    "state": "MN",
    "country_code": "US",
    "hospital_type": "TEACHING",
    "jci_accredited": true,
    "avg_quality_score": 95.5,
    "complication_rate": 2.1,
    "readmission_rate": 1.8,
    "departments": [
      {
        "name": "Cardiology",
        "procedures": [
          {
            "name": "Heart Bypass Surgery",
            "cpt_code": "33533",
            "base_price": 75000,
            "currency_code": "USD",
            "success_rate": 97.5,
            "clinical_category": "CARDIAC_SURGERY",
            "complexity_score": 9.5
          }
        ]
      }
    ]
  }
]
```

### EHDS Data

```json
[
  {
    "source_id": "EHDS-HOSP-001",
    "name": "Charité Berlin",
    "country_code": "DE",
    "hospital_type": "TEACHING",
    "price_data_source": "EHDS",
    "departments": [
      {
        "name": "Oncology",
        "procedures": [
          {
            "name": "Cervical Cancer Treatment",
            "base_price": 45000,
            "currency_code": "EUR",
            "clinical_category": "ONCOLOGY"
          }
        ]
      }
    ]
  }
]
```

### ABDM Data

```json
[
  {
    "source_id": "ABDM-HOSP-001",
    "name": "Apollo Hospitals Chennai",
    "country_code": "IN",
    "hospital_type": "PRIVATE",
    "nabh_accredited": true,
    "price_data_source": "ABDM",
    "departments": [
      {
        "name": "Orthopedics",
        "procedures": [
          {
            "name": "Total Knee Replacement",
            "base_price": 350000,
            "currency_code": "INR",
            "clinical_category": "ORTHOPEDICS"
          }
        ]
      }
    ]
  }
]
```

## Test Fixtures & Utilities

### Available Fixtures (conftest.py)

```python
# Ingestion engine
@pytest.fixture
async def ingestion_engine:
    # Initialized DataIngestionEngine ready for testing

# Session factory
@pytest.fixture
async def session_factory:
    # Database session factory

# Sample data (auto-generated)
@pytest.fixture
def sample_hhs_data:  # 2 hospitals, 3 procedures
def sample_ehds_data:  # 1 hospital, 1 procedure
def sample_abdm_data:  # 1 hospital, 1 procedure

# Temporary JSON files
@pytest.fixture
def tmp_data_files:
    # Dict with paths to HHS, EHDS, ABDM JSON files

# Database cleanup
@pytest.fixture
async def clean_database:
    # Truncates tables before/after test
```

## Running in CI/CD

### Example GitHub Actions Workflow

```yaml
name: Phase 3 Tests

on: [push, pull_request]

jobs:
  integration-tests:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:16
        env:
          POSTGRES_PASSWORD: postgres
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

    steps:
      - uses: actions/checkout@v3
      
      - name: Run Phase 3 Tests
        working-directory: ./apps/api
        run: |
          python -m pip install -e .
          python -m pytest tests/test_integration_phase1.py -v --cov=app
      
      - name: Verify Data
        working-directory: ./apps/api
        run: python scripts/verify_data.py
      
      - name: Upload Coverage
        uses: codecov/codecov-action@v3
```

## Troubleshooting

### "Database connection failed"

```bash
# Ensure PostgreSQL is running
docker-compose up -d postgres

# Check environment variables
cat apps/api/.env
```

### "Test timeouts"

```bash
# Run with extended timeout
python -m pytest tests/test_integration_phase1.py --timeout=300

# Run single test class at a time
python -m pytest tests/test_integration_phase1.py::TestIntegrationEndToEnd -v
```

### "Duplicate ingestion not skipped"

```bash
# Verify source_id uniqueness in sample data
python scripts/verify_data.py

# Check for manual database records
psql -U postgres -d evijnar -c "SELECT source_id, COUNT(*) FROM global_hospitals GROUP BY source_id HAVING COUNT(*) > 1;"
```

## Next Steps

After Phase 3 completion:

1. **Production Load Testing** - Phase 4 with real dataset volumes
2. **Performance Optimization** - Tune batch sizes and concurrency
3. **Monitoring Setup** - Track ingestion metrics in production
4. **Data Migration** - Load historical hospital data
5. **Load Balancing** - Distribute ingestion across multiple workers

## Files Included

```
tests/
├── __init__.py                      # Test module
├── conftest.py                      # Fixtures & test data
└── test_integration_phase1.py       # All test cases

scripts/
├── ingest_data.py                   # CLI ingestion tool
├── verify_data.py                   # Database verification
└── run_phase1_tests.py              # Comprehensive test runner

docs/
└── phase1_TESTING.md               # This file
```

## Summary

Phase 3 provides a robust testing framework ensuring:

- ✅ End-to-end ingestion works correctly across all data sources
- ✅ Data idempotency prevents duplicates
- ✅ Transaction atomicity ensures data consistency
- ✅ Concurrent processing handles parallel workloads
- ✅ Complete audit trail for compliance
- ✅ Verified data persistence to database

The framework is production-ready for validating ingestion pipelines before going live.
