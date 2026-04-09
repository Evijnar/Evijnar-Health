# apps/api/app/services/data_ingestion/loaders/hhs_loader.py
"""
HHS Price Transparency 2026 JSON Loader.
Parses US Hospital Price Transparency data from CMS/HHS format.
Format: https://www.cms.gov/CMSGov/media/document/price-transparency-requirements.json
"""

import logging
from typing import List, Dict, Any
from datetime import datetime

from ..models import RawHospitalData, RawProcedureData, IngestSource
from .json_loader import JsonLoader

logger = logging.getLogger("evijnar.ingest.hhs_loader")


class HHSLoader(JsonLoader):
    """
    Loader for HHS Price Transparency 2026 JSON format.
    Expects structure with pricing_information array.
    """

    def __init__(self):
        super().__init__(IngestSource.HHS_TRANSPARENCY)

    def parse_records(self, raw_data: List[Dict[str, Any]]) -> List[RawHospitalData]:
        """
        Parse HHS-format JSON.
        Expected structure:
        {
            "hospital": {
                "name": "...",
                "facility_ccn": "...",
                "npi": "...",
                "address": {...},
                "contact": {...}
            },
            "pricing_information": [
                {
                    "drug_name": "...",
                    "drug_code": "...",
                    "pricing": [...]
                }
            ]
        }
        """
        records = []

        for idx, record in enumerate(raw_data):
            try:
                hospital_info = record.get('hospital', {})
                address = hospital_info.get('address', {})

                # Extract procedures from pricing_information
                procedures = []
                for pricing_item in record.get('pricing_information', []):
                    proc = RawProcedureData(
                        description=pricing_item.get('description') or pricing_item.get('drug_name') or "Unknown Procedure",
                        code=pricing_item.get('code') or pricing_item.get('drug_code'),
                        price=pricing_item.get('price') or pricing_item.get('standard_charge'),
                        currency="USD",
                        success_rate=None,
                        complication_rate=None,
                    )
                    procedures.append(proc)

                hospital = RawHospitalData(
                    source_id=hospital_info.get('facility_ccn') or hospital_info.get('npi') or f"HHS-{idx}",
                    source=IngestSource.HHS_TRANSPARENCY,
                    name=hospital_info.get('name') or "",
                    description=hospital_info.get('description'),
                    city=address.get('city') or "",
                    state_or_province=address.get('state', 'US'),
                    postal_code=address.get('zip_code'),
                    country_code='US',
                    phone=hospital_info.get('phone'),
                    email=hospital_info.get('email'),
                    website=hospital_info.get('website'),
                    hospital_type_raw=hospital_info.get('type'),
                    procedures=procedures,
                    raw_json=record,
                )
                records.append(hospital)

                logger.debug(f"Parsed HHS record: {hospital.name} with {len(procedures)} procedures")

            except Exception as e:
                logger.warning(f"Failed to parse HHS record {idx}: {str(e)}")
                continue

        logger.info(f"Parsed {len(records)} HHS hospitals")
        return records
