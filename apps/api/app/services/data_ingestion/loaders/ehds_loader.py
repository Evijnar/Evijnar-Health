# apps/api/app/services/data_ingestion/loaders/ehds_loader.py
"""
EHDS (European Health Data Space) 2026 Loader.
Parses European hospital data from EHDS format.
"""

import logging
from typing import List, Dict, Any

from ..models import RawHospitalData, RawProcedureData, RawDepartmentData, IngestSource
from .json_loader import JsonLoader

logger = logging.getLogger("evijnar.ingest.ehds_loader")


class EHDSLoader(JsonLoader):
    """
    Loader for EHDS (European Health Data Space) format.
    Expected structure with healthcare_service array.
    """

    def __init__(self):
        super().__init__(IngestSource.EHDS)

    def parse_records(self, raw_data: List[Dict[str, Any]]) -> List[RawHospitalData]:
        """
        Parse EHDS-format JSON.
        Expected structure:
        {
            "organisation_id": "...",
            "name": "...",
            "location": {"address": "...", "country": "..."},
            "healthcare_services": [
                {
                    "service_name": "...",
                    "icd10_code": "...",
                    "pricing": {...}
                }
            ]
        }
        """
        records = []

        for idx, record in enumerate(raw_data):
            try:
                location = record.get('location', {})

                # Parse departments and procedures from healthcare_services
                departments = []
                procedures = []

                for service in record.get('healthcare_services', []):
                    # Create procedure from service
                    proc = RawProcedureData(
                        description=service.get('service_name') or service.get('description') or "Unknown Service",
                        code=service.get('icd10_code'),
                        price=service.get('pricing', {}).get('base_price'),
                        currency=service.get('pricing', {}).get('currency', 'EUR'),
                        success_rate=service.get('outcome_data', {}).get('success_rate'),
                        complication_rate=service.get('outcome_data', {}).get('complication_rate'),
                    )
                    procedures.append(proc)

                    # Create department if specialization info present
                    if service.get('specialization'):
                        dept = RawDepartmentData(
                            name=service.get('specialization'),
                            code=service.get('specialization_code'),
                            procedures=[proc],
                        )
                        departments.append(dept)

                hospital = RawHospitalData(
                    source_id=record.get('organisation_id') or record.get('id') or f"EHDS-{idx}",
                    source=IngestSource.EHDS,
                    name=record.get('name') or record.get('organisation_name') or "",
                    description=record.get('description'),
                    city=location.get('city') or "",
                    state_or_province=location.get('region') or location.get('state', ''),
                    postal_code=location.get('postal_code'),
                    country_code=location.get('country_code', 'EU'),
                    phone=record.get('contact', {}).get('phone'),
                    email=record.get('contact', {}).get('email'),
                    website=record.get('contact', {}).get('website'),
                    hospital_type_raw=record.get('organisation_type'),
                    departments=departments,
                    procedures=procedures,
                    raw_json=record,
                )
                records.append(hospital)

                logger.debug(f"Parsed EHDS record: {hospital.name} with {len(procedures)} services")

            except Exception as e:
                logger.warning(f"Failed to parse EHDS record {idx}: {str(e)}")
                continue

        logger.info(f"Parsed {len(records)} EHDS healthcare organisations")
        return records
