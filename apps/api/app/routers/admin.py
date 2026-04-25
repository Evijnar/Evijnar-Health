# apps/api/app/routers/admin.py
"""
Administrative endpoints for data ingestion and management.
Requires ADMIN role authorization.
"""

import logging
from fastapi import APIRouter, HTTPException, UploadFile, File, Depends
from pydantic import BaseModel
from typing import Optional
import tempfile
import os

from app.services.data_ingestion import (
    IngestReport,
    IngestSource,
    EngineError,
)
from app.services.data_ingestion.ingestion_engine import DataIngestionEngine

logger = logging.getLogger("evijnar.admin")

router = APIRouter()

# Global engine instance
_engine: Optional[DataIngestionEngine] = None


async def get_engine() -> DataIngestionEngine:
    """Get or create ingestion engine"""
    global _engine
    if _engine is None:
        _engine = DataIngestionEngine()
        await _engine.initialize()
    return _engine


class IngestRequest(BaseModel):
    """Request to start ingestion job"""
    source: str  # "HHS_TRANSPARENCY", "EHDS", "ABDM"
    dry_run: bool = False


class IngestJobResponse(BaseModel):
    """Response with job status"""
    job_id: str
    status: str  # "PENDING", "PROCESSING", "COMPLETED", "FAILED"
    message: str


# In-memory job tracking (for demo; in production use Redis/database)
_jobs: dict = {}


@router.post("/api/v1/admin/ingest/upload")
async def upload_and_ingest(
    file: UploadFile = File(...),
    source: str = "HHS_TRANSPARENCY",
    dry_run: bool = False,
    engine: DataIngestionEngine = Depends(get_engine),
) -> dict:
    """
    Upload a JSON file and start ingestion job.

    Args:
        file: JSON file to ingest
        source: Data source (HHS_TRANSPARENCY, EHDS, ABDM)
        dry_run: If true, don't persist to database
        engine: Ingestion engine

    Returns:
        Job information with results
    """
    try:
        # Validate source
        try:
            ingest_source = IngestSource[source]
        except KeyError:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid source. Must be one of: {', '.join([s.name for s in IngestSource])}"
            )

        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=".json") as temp_file:
            contents = await file.read()
            temp_file.write(contents)
            temp_path = temp_file.name

        try:
            # Run ingestion
            logger.info(f"Starting ingestion from uploaded file: {file.filename}")
            report = await engine.ingest_file(temp_path, ingest_source, dry_run)

            # Get LLM usage stats
            llm_usage = engine.get_llm_usage()

            return {
                "job_id": report.job_id,
                "status": "COMPLETED" if report.is_complete else "INCOMPLETE",
                "summary": {
                    "total_records": report.total_records,
                    "succeeded": report.succeeded,
                    "failed": report.failed,
                    "skipped": report.skipped,
                    "success_rate": f"{report.success_rate:.1f}%",
                    "hospitals_created": report.hospitals_created,
                    "procedures_created": report.procedures_created,
                    "normalizers_created": report.normalizers_created,
                    "processing_time_seconds": report.processing_time_seconds,
                },
                "llm_usage": {
                    "total_calls": llm_usage.get("total_calls", 0),
                    "total_tokens": llm_usage.get("total_tokens", 0),
                    "cached_responses": llm_usage.get("total_cached", 0),
                    "estimated_cost_usd": f"${llm_usage.get('estimated_cost_usd', 0):.2f}",
                },
                "errors": [
                    {
                        "source_id": e.source_id,
                        "error": e.error_message,
                        "type": e.error_type,
                    }
                    for e in report.errors[:10]  # First 10 errors
                ],
                "warnings": report.warnings[:5],
            }

        finally:
            # Clean up temp file
            if os.path.exists(temp_path):
                os.remove(temp_path)

    except EngineError as e:
        logger.error(f"Ingestion engine error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Ingestion error: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error in ingestion: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/api/v1/admin/ingest/status/{job_id}")
async def get_ingest_status(job_id: str) -> dict:
    """
    Get status of an ingestion job.

    Args:
        job_id: Job ID

    Returns:
        Job status and progress
    """
    # TODO: Implement job tracking with Redis
    raise HTTPException(status_code=501, detail="Job tracking not yet implemented")


@router.get("/api/v1/admin/ingest/health")
async def ingest_health(engine: DataIngestionEngine = Depends(get_engine)) -> dict:
    """Health check for ingestion service"""
    return {
        "status": "healthy",
        "llm_client_initialized": engine.llm_client is not None,
        "llm_usage": engine.get_llm_usage(),
    }


@router.post("/api/v1/admin/ingest/test-mappings")
async def test_mappings(engine: DataIngestionEngine = Depends(get_engine)) -> dict:
    """
    Test AI mapping with sample data.
    Useful for validating Evijnar Health AI integration.
    """
    from app.services.data_ingestion.models import RawHospitalData, RawProcedureData

    try:
        # Test hospital mapping
        test_hospital = RawHospitalData(
            source_id="TEST-001",
            source=IngestSource.HHS_TRANSPARENCY,
            name="Test Medical Center",
            city="Boston",
            state_or_province="Massachusetts",
            country_code="US",
        )

        mapped_hospital = await engine.hospital_mapper.map_hospital(test_hospital)

        # Test procedure mapping
        test_procedure = RawProcedureData(
            description="Total knee replacement with prosthesis",
            code="27447",
            price=45000,
        )

        mapped_procedure = await engine.procedure_mapper.map_procedure(test_procedure)

        # Test normalizer mapping
        normalizer = await engine.normalizer_mapper.map_cpt_code(
            "27447",
            "Total knee replacement with prosthesis",
        )

        return {
            "status": "success",
            "hospital_mapping": {
                "input": test_hospital.name,
                "output": mapped_hospital.name,
                "type": mapped_hospital.hospital_type,
            },
            "procedure_mapping": {
                "input": test_procedure.description,
                "output": mapped_procedure.icd10_code,
                "category": mapped_procedure.clinical_category,
                "complexity": mapped_procedure.complexity_score,
            },
            "normalizer_mapping": {
                "cpt": normalizer.cpt_code,
                "icd10": normalizer.icd10_code,
                "uhi": normalizer.uhi_code,
                "cost_usd": normalizer.us_median_cost_usd,
            },
        }

    except Exception as e:
        logger.error(f"Mapping test failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Mapping test failed: {str(e)}")


@router.get("/api/v1/admin/ingest/sources")
async def list_ingest_sources() -> dict:
    """List available ingestion sources"""
    return {
        "available_sources": [
            {
                "name": source.value,
                "description": {
                    "HHS_TRANSPARENCY": "USA Hospital Price Transparency Data",
                    "EHDS": "European Health Data Space",
                    "ABDM": "Ayushman Bharat Digital Mission (India)",
                }.get(source.name, "Unknown"),
            }
            for source in IngestSource
        ]
    }
