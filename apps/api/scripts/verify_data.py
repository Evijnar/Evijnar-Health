"""
Phase 3 Database Verification - Post-ingestion data validation queries.
Query database to confirm data persistence and integrity.
"""

import asyncio
from typing import List, Dict, Any
from sqlalchemy import text, func, select
from app.db import get_session_factory
from app.models import GlobalHospital, ProcedurePrice, PriceNormalizer, AuditLog


class DatabaseVerification:
    """Utility class for database verification queries."""

    def __init__(self, session_factory):
        self.session_factory = session_factory

    async def verify_hospital_count(self, expected_count: int = None) -> Dict[str, Any]:
        """Verify total hospital records in database."""
        async with self.session_factory() as session:
            result = await session.execute(
                select(func.count(GlobalHospital.id))
            )
            count = result.scalar()

            return {
                "total_hospitals": count,
                "expected": expected_count,
                "matches": count == expected_count if expected_count else None,
            }

    async def verify_hospitals_by_source(self) -> Dict[str, int]:
        """Verify hospitals grouped by price data source."""
        async with self.session_factory() as session:
            result = await session.execute(
                select(
                    GlobalHospital.price_data_source,
                    func.count(GlobalHospital.id).label("count"),
                ).group_by(GlobalHospital.price_data_source)
            )

            data = {}
            for row in result:
                data[row[0]] = row[1]
            return data

    async def verify_hospitals_by_country(self) -> Dict[str, int]:
        """Verify hospitals grouped by country."""
        async with self.session_factory() as session:
            result = await session.execute(
                select(
                    GlobalHospital.country_code,
                    func.count(GlobalHospital.id).label("count"),
                ).group_by(GlobalHospital.country_code)
            )

            data = {}
            for row in result:
                data[row[0]] = row[1]
            return data

    async def verify_accreditation_status(self) -> Dict[str, int]:
        """Verify accreditation status counts."""
        async with self.session_factory() as session:
            jci_count = await session.execute(
                select(func.count(GlobalHospital.id)).where(
                    GlobalHospital.jci_accredited is True
                )
            )
            nabh_count = await session.execute(
                select(func.count(GlobalHospital.id)).where(
                    GlobalHospital.nabh_accredited is True
                )
            )

            return {
                "jci_accredited": jci_count.scalar() or 0,
                "nabh_accredited": nabh_count.scalar() or 0,
            }

    async def verify_procedure_count(self, expected_count: int = None) -> Dict[str, Any]:
        """Verify total procedure records."""
        async with self.session_factory() as session:
            result = await session.execute(
                select(func.count(ProcedurePrice.id))
            )
            count = result.scalar()

            return {
                "total_procedures": count,
                "expected": expected_count,
                "matches": count == expected_count if expected_count else None,
            }

    async def verify_procedures_by_category(self) -> Dict[str, int]:
        """Verify procedures grouped by clinical category."""
        async with self.session_factory() as session:
            result = await session.execute(
                select(
                    ProcedurePrice.clinical_category,
                    func.count(ProcedurePrice.id).label("count"),
                ).group_by(ProcedurePrice.clinical_category)
            )

            data = {}
            for row in result:
                data[row[0]] = row[1]
            return data

    async def verify_normalizer_count(self, expected_count: int = None) -> Dict[str, Any]:
        """Verify price normalizer records."""
        async with self.session_factory() as session:
            result = await session.execute(
                select(func.count(PriceNormalizer.id))
            )
            count = result.scalar()

            return {
                "total_normalizers": count,
                "expected": expected_count,
                "matches": count == expected_count if expected_count else None,
            }

    async def verify_data_quality(self) -> Dict[str, Any]:
        """Verify data quality metrics."""
        async with self.session_factory() as session:
            # Hospitals with quality score
            with_quality = await session.execute(
                select(func.count(GlobalHospital.id)).where(
                    GlobalHospital.avg_quality_score.isnot(None)
                )
            )

            # Procedures with base price
            with_price = await session.execute(
                select(func.count(ProcedurePrice.id)).where(
                    ProcedurePrice.base_price.isnot(None)
                )
            )

            # Procedures with success rate
            with_success = await session.execute(
                select(func.count(ProcedurePrice.id)).where(
                    ProcedurePrice.success_rate.isnot(None)
                )
            )

            return {
                "hospitals_with_quality_score": with_quality.scalar() or 0,
                "procedures_with_price": with_price.scalar() or 0,
                "procedures_with_success_rate": with_success.scalar() or 0,
            }

    async def verify_no_duplicates(self) -> Dict[str, Any]:
        """Verify no duplicate hospitals by source_id."""
        async with self.session_factory() as session:
            # Find duplicate source_ids
            result = await session.execute(
                select(
                    GlobalHospital.source_id,
                    func.count(GlobalHospital.id).label("count"),
                )
                .group_by(GlobalHospital.source_id)
                .having(func.count(GlobalHospital.id) > 1)
            )

            duplicates = result.fetchall()

            return {
                "has_duplicates": len(duplicates) > 0,
                "duplicate_count": len(duplicates),
                "details": [
                    {"source_id": row[0], "instances": row[1]} for row in duplicates
                ],
            }

    async def verify_audit_logs(self) -> Dict[str, Any]:
        """Verify audit logging for compliance."""
        async with self.session_factory() as session:
            # Count ingestion events
            success_logs = await session.execute(
                select(func.count(AuditLog.id)).where(
                    AuditLog.action == "INGEST_SUCCESS"
                )
            )
            failure_logs = await session.execute(
                select(func.count(AuditLog.id)).where(
                    AuditLog.action == "INGEST_FAILURE"
                )
            )

            return {
                "ingestion_success_logs": success_logs.scalar() or 0,
                "ingestion_failure_logs": failure_logs.scalar() or 0,
            }

    async def verify_hospital_details(self, source_id: str) -> Dict[str, Any]:
        """Verify specific hospital details."""
        async with self.session_factory() as session:
            hospital = await session.execute(
                select(GlobalHospital).where(
                    GlobalHospital.source_id == source_id
                )
            )
            hospital = hospital.scalars().first()

            if not hospital:
                return {"found": False}

            return {
                "found": True,
                "id": hospital.id,
                "name": hospital.name,
                "city": hospital.city,
                "country_code": hospital.country_code,
                "jci_accredited": hospital.jci_accredited,
                "nabh_accredited": hospital.nabh_accredited,
                "quality_score": float(hospital.avg_quality_score) if hospital.avg_quality_score else None,
                "procedures_count": len(hospital.procedures) if hospital.procedures else 0,
            }

    async def generate_verification_report(self) -> Dict[str, Any]:
        """Generate comprehensive verification report."""
        return {
            "hospital_count": await self.verify_hospital_count(),
            "hospitals_by_source": await self.verify_hospitals_by_source(),
            "hospitals_by_country": await self.verify_hospitals_by_country(),
            "accreditation_status": await self.verify_accreditation_status(),
            "procedure_count": await self.verify_procedure_count(),
            "procedures_by_category": await self.verify_procedures_by_category(),
            "normalizer_count": await self.verify_normalizer_count(),
            "data_quality": await self.verify_data_quality(),
            "duplicate_check": await self.verify_no_duplicates(),
            "audit_logs": await self.verify_audit_logs(),
        }


async def main():
    """Run database verification."""
    session_factory = get_session_factory()
    verifier = DatabaseVerification(session_factory)

    print("\n" + "=" * 70)
    print("DATABASE VERIFICATION REPORT")
    print("=" * 70 + "\n")

    report = await verifier.generate_verification_report()

    print(f"Hospital Count: {report['hospital_count']['total_hospitals']} hospitals")
    print(f"\nHospitals by Source:")
    for source, count in report['hospitals_by_source'].items():
        print(f"  - {source}: {count}")

    print(f"\nHospitals by Country:")
    for country, count in report['hospitals_by_country'].items():
        print(f"  - {country}: {count}")

    print(f"\nAccreditation Status:")
    print(f"  - JCI Accredited: {report['accreditation_status']['jci_accredited']}")
    print(f"  - NABH Accredited: {report['accreditation_status']['nabh_accredited']}")

    print(f"\nProcedure Count: {report['procedure_count']['total_procedures']} procedures")
    print(f"\nProcedures by Category:")
    for category, count in report['procedures_by_category'].items():
        print(f"  - {category}: {count}")

    print(f"\nPrice Normalizers: {report['normalizer_count']['total_normalizers']}")

    print(f"\nData Quality:")
    print(f"  - Hospitals with Quality Score: {report['data_quality']['hospitals_with_quality_score']}")
    print(f"  - Procedures with Price: {report['data_quality']['procedures_with_price']}")
    print(f"  - Procedures with Success Rate: {report['data_quality']['procedures_with_success_rate']}")

    print(f"\nDuplicate Check:")
    dup = report['duplicate_check']
    print(f"  - Has Duplicates: {dup['has_duplicates']}")
    print(f"  - Duplicate Count: {dup['duplicate_count']}")

    print(f"\nAudit Logs:")
    print(f"  - Ingestion Success: {report['audit_logs']['ingestion_success_logs']}")
    print(f"  - Ingestion Failures: {report['audit_logs']['ingestion_failure_logs']}")

    print("\n" + "=" * 70)


if __name__ == "__main__":
    asyncio.run(main())
