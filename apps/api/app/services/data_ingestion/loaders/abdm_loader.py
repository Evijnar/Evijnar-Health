# apps/api/app/services/data_ingestion/loaders/abdm_loader.py
"""
ABDM (Ayushman Bharat Digital Mission) / UHI 2026 Loader.
Parses Indian healthcare facility data from ABDM format.
"""

import logging
from typing import List, Dict, Any

from ..models import RawHospitalData, RawProcedureData, RawDepartmentData, IngestSource
from .json_loader import JsonLoader

logger = logging.getLogger("evijnar.ingest.abdm_loader")


class ABDMLoader(JsonLoader):
    """
    Loader for ABDM/UHI (Unified Health Interface) format.
    Parses Indian healthcare facility pricing data.
    Expected structure with facility and services arrays.
    """

    def __init__(self):
        super().__init__(IngestSource.ABDM)

    def parse_records(self, raw_data: List[Dict[str, Any]]) -> List[RawHospitalData]:
        """
        Parse ABDM/UHI-format JSON.
        Expected structure:
        {
            "facility_id": "...",
            "facility_name": "...",
            "facility_type": "...",
            "state": "...",
            "district": "...",
            "nabh_accredited": true/false,
            "services": [
                {
                    "uhi_code": "...",
                    "service_name": "...",
                    "pricing": {...},
                    "outcomes": {...}
                }
            ]
        }
        """
        records = []

        for idx, record in enumerate(raw_data):
            try:
                # Parse services into procedures and departments
                departments = {}
                procedures = []

                for service in record.get('services', []):
                    pricing = service.get('pricing', {})
                    outcomes = service.get('outcomes', {})

                    proc = RawProcedureData(
                        description=service.get('service_name') or service.get('description') or "Unknown Service",
                        code=service.get('uhi_code'),  # ABDM uses UHI codes
                        price=pricing.get('total_cost') or pricing.get('price'),
                        currency=pricing.get('currency', 'INR'),
                        success_rate=outcomes.get('success_rate'),
                        complication_rate=outcomes.get('complication_rate'),
                    )
                    procedures.append(proc)

                    # Group by department/specialization
                    dept_name = service.get('department') or service.get('specialization') or 'General'
                    if dept_name not in departments:
                        departments[dept_name] = RawDepartmentData(
                            name=dept_name,
                            code=service.get('department_code'),
                            procedures=[]
                        )
                    departments[dept_name].procedures.append(proc)

                # Extract tier classification for rural routing
                state_code = record.get('state_code', 'XX')
                district = record.get('district', '')
                rural_tier = self._classify_tier(state_code, district)

                hospital = RawHospitalData(
                    source_id=record.get('facility_id') or record.get('id') or f"ABDM-{idx}",
                    source=IngestSource.ABDM,
                    name=record.get('facility_name') or record.get('name') or "",
                    description=record.get('description'),
                    city=record.get('city') or record.get('district') or "",
                    state_or_province=record.get('state') or state_code,
                    postal_code=record.get('postal_code'),
                    country_code='IN',  # India
                    phone=record.get('phone'),
                    email=record.get('email'),
                    website=record.get('website'),
                    hospital_type_raw=record.get('facility_type'),
                    nabh_accredited=record.get('nabh_accredited', False),
                    departments=list(departments.values()),
                    procedures=procedures,
                    raw_json=record,
                )
                records.append(hospital)

                logger.debug(f"Parsed ABDM record: {hospital.name} (Tier: {rural_tier}) with {len(procedures)} services")

            except Exception as e:
                logger.warning(f"Failed to parse ABDM record {idx}: {str(e)}")
                continue

        logger.info(f"Parsed {len(records)} ABDM healthcare facilities")
        return records

    def _classify_tier(self, state_code: str, district: str) -> str:
        """
        Classify facility into rural tier based on location.
        Must be synchronized with Patient.rural_tier enum.
        """
        # Tier 3 (rural) states: Madhya Pradesh, Odisha, Rajasthan, Chhattisgarh, etc.
        tier_3_states = ['MP', 'OD', 'RJ', 'CG', 'JH', 'BH', 'UP-RURAL']

        if state_code in tier_3_states:
            # Assume rural unless large city district
            large_cities = ['Bhopal', 'Indore', 'Jabalpur', 'Raipur', 'Ranchi']
            if district not in large_cities:
                return 'TIER_3'

        # Default to Tier 2 (semi-urban)
        return 'TIER_2'
