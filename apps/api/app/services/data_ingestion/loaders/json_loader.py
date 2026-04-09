# apps/api/app/services/data_ingestion/loaders/json_loader.py
"""Generic JSON file loader"""

import json
from pathlib import Path
from typing import List, Dict, Any
import logging

from ..models import RawHospitalData, IngestSource
from ..errors import InvalidJsonError, FormatError

logger = logging.getLogger("evijnar.ingest.loader")


class JsonLoader:
    """Base class for loading JSON data files"""

    def __init__(self, source: IngestSource):
        self.source = source

    def load_file(self, filepath: str) -> List[Dict[str, Any]]:
        """
        Load and parse JSON file.

        Args:
            filepath: Path to JSON file

        Returns:
            List of records from JSON

        Raises:
            InvalidJsonError: If JSON is malformed
            FileNotFoundError: If file doesn't exist
        """
        try:
            path = Path(filepath)
            if not path.exists():
                raise FileNotFoundError(f"File not found: {filepath}")

            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Handle both JSON array and object with data key
            if isinstance(data, list):
                records = data
            elif isinstance(data, dict):
                # Look for common data keys
                for key in ['data', 'hospitals', 'records', 'results', 'entries']:
                    if key in data:
                        records = data[key]
                        if not isinstance(records, list):
                            raise FormatError(f"Expected list at key '{key}', got {type(records)}")
                        break
                else:
                    raise FormatError("JSON object must contain 'data' or similar key with array")
            else:
                raise FormatError(f"Expected JSON array or object, got {type(data)}")

            logger.info(f"Loaded {len(records)} records from {filepath}")
            return records

        except json.JSONDecodeError as e:
            raise InvalidJsonError(
                f"Malformed JSON in {filepath}: {str(e)}",
                details={"line": e.lineno, "column": e.colno}
            )
        except Exception as e:
            if isinstance(e, (InvalidJsonError, FormatError, FileNotFoundError)):
                raise
            raise InvalidJsonError(
                f"Error loading JSON: {str(e)}",
                details={"filepath": filepath}
            )

    def parse_records(self, raw_data: List[Dict[str, Any]]) -> List[RawHospitalData]:
        """
        Parse raw JSON records into RawHospitalData models.
        To be overridden by subclasses for format-specific parsing.

        Args:
            raw_data: List of raw records from JSON

        Returns:
            List of RawHospitalData instances
        """
        raise NotImplementedError("Subclasses must implement parse_records()")


class GenericJsonLoader(JsonLoader):
    """
    Generic loader for already-normalized JSON.
    Assumes JSON is already in near-standard format.
    """

    def parse_records(self, raw_data: List[Dict[str, Any]]) -> List[RawHospitalData]:
        """
        Parse generic JSON records.
        Attempts to map fields flexibly.
        """
        records = []

        for idx, record in enumerate(raw_data):
            try:
                hospital = RawHospitalData(
                    source_id=record.get('id') or record.get('source_id') or f"GEN-{idx}",
                    source=self.source,
                    name=record.get('name') or record.get('hospital_name') or "",
                    city=record.get('city') or "",
                    state_or_province=record.get('state') or record.get('state_province') or "",
                    country_code=record.get('country_code', 'US'),
                    phone=record.get('phone'),
                    email=record.get('email'),
                    website=record.get('website'),
                    postal_code=record.get('postal_code'),
                    hospital_type_raw=record.get('hospital_type'),
                    jci_accredited=record.get('jci_accredited'),
                    nabh_accredited=record.get('nabh_accredited'),
                    raw_json=record,
                )
                records.append(hospital)
            except Exception as e:
                logger.warning(f"Failed to parse record {idx}: {str(e)}")
                continue

        return records
