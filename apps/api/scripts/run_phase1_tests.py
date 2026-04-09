#!/usr/bin/env python3
"""
Phase 3 Test Runner - Orchestrates all integration tests and generates report.
Usage: python run_phase1_tests.py [--verbose] [--coverage] [--report]
"""

import subprocess
import sys
import json
import time
from pathlib import Path
from datetime import datetime


class phase1TestRunner:
    """Orchestrates Phase 3 testing workflow."""

    def __init__(self, verbose=False, coverage=False, report=False):
        self.verbose = verbose
        self.coverage = coverage
        self.report = report
        self.results = {
            "timestamp": datetime.utcnow().isoformat(),
            "tests": {},
            "summary": {},
        }

    def run_tests(self) -> bool:
        """Run all Phase 3 integration tests."""
        print("\n" + "=" * 70)
        print("PHASE 3: INTEGRATION TESTING - END-TO-END INGESTION")
        print("=" * 70 + "\n")

        test_groups = [
            ("End-to-End Ingestion", "TestIntegrationEndToEnd"),
            ("Idempotency", "TestIdempotency"),
            ("Transaction Atomicity", "TestTransactionAtomicity"),
            ("Concurrent Ingestion", "TestConcurrentIngestion"),
        ]

        all_passed = True
        total_start = time.time()

        for group_name, class_name in test_groups:
            print(f"\n📋 Running {group_name}...")
            print(f"   Class: {class_name}\n")

            start_time = time.time()

            # Build pytest command
            cmd = [
                "python",
                "-m",
                "pytest",
                f"tests/test_integration_phase1.py::{class_name}",
                "-v",
                "--tb=short",
                "--no-header",
            ]

            if self.coverage:
                cmd.extend(["--cov=app", "--cov-report=html"])

            if self.verbose:
                cmd.append("-vv")

            # Run tests
            result = subprocess.run(cmd, cwd=Path(__file__).parent.parent)
            elapsed = time.time() - start_time

            passed = result.returncode == 0
            all_passed = all_passed and passed

            status = "✅ PASSED" if passed else "❌ FAILED"
            print(f"\n   {status} ({elapsed:.2f}s)")

            self.results["tests"][group_name] = {
                "passed": passed,
                "elapsed_seconds": elapsed,
            }

        total_elapsed = time.time() - total_start

        print("\n" + "=" * 70)
        print("TEST SUMMARY")
        print("=" * 70 + "\n")

        for group_name, result in self.results["tests"].items():
            status = "✅" if result["passed"] else "❌"
            print(f"{status} {group_name:<30} {result['elapsed_seconds']:.2f}s")

        print(f"\nTotal Time: {total_elapsed:.2f}s")

        self.results["summary"] = {
            "all_passed": all_passed,
            "total_time_seconds": total_elapsed,
            "test_count": len(test_groups),
        }

        return all_passed

    async def verify_data(self) -> Dict:
        """Run database verification after tests."""
        print("\n" + "=" * 70)
        print("PHASE 3: DATABASE VERIFICATION")
        print("=" * 70 + "\n")

        # Import here to avoid issues during test execution
        sys.path.insert(0, str(Path(__file__).parent))
        from scripts.verify_data import DatabaseVerification
        from app.db import get_session_factory

        session_factory = get_session_factory()
        verifier = DatabaseVerification(session_factory)

        print("🔍 Running database verification queries...\n")

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

        print(f"\nProcedure Count: {report['procedure_count']['total_procedures']}")

        print(f"\nData Quality:")
        print(f"  - Hospitals with Quality Score: {report['data_quality']['hospitals_with_quality_score']}")
        print(f"  - Procedures with Price: {report['data_quality']['procedures_with_price']}")
        print(f"  - Procedures with Success Rate: {report['data_quality']['procedures_with_success_rate']}")

        dup = report['duplicate_check']
        if dup['has_duplicates']:
            print(f"\n⚠️  WARNING: Duplicate hospitals found: {dup['duplicate_count']}")
        else:
            print(f"\n✅ No duplicates found")

        self.results["verification"] = report

        return report

    def generate_report(self):
        """Generate JSON report of all results."""
        if not self.report:
            return

        report_path = Path(__file__).parent.parent / "phase1_test_report.json"
        report_path.write_text(json.dumps(self.results, indent=2))

        print(f"\n📄 Report saved to: {report_path}")

    def print_final_summary(self, all_passed: bool):
        """Print final summary and guidance."""
        print("\n" + "=" * 70)
        print("PHASE 3 TESTING COMPLETE")
        print("=" * 70 + "\n")

        if all_passed:
            print("✅ ALL TESTS PASSED\n")
            print("Next Steps:")
            print("  1. Review coverage report (if --coverage was used)")
            print("  2. Verify production data loading process")
            print("  3. Set up monitoring for ingestion pipeline")
            print("  4. Document any data quality issues")
        else:
            print("❌ SOME TESTS FAILED\n")
            print("Recommended Actions:")
            print("  1. Review failed test output above")
            print("  2. Check database state for inconsistencies")
            print("  3. Review ingestion logs for errors")
            print("  4. Fix issues and re-run tests")

        print("\n" + "=" * 70 + "\n")


async def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Phase 3 Integration Testing")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose test output")
    parser.add_argument("--coverage", "-c", action="store_true", help="Generate coverage report")
    parser.add_argument("--report", "-r", action="store_true", help="Generate JSON report")

    args = parser.parse_args()

    runner = phase1TestRunner(
        verbose=args.verbose,
        coverage=args.coverage,
        report=args.report,
    )

    # Run tests
    all_passed = runner.run_tests()

    # Run verification
    try:
        await runner.verify_data()
    except Exception as e:
        print(f"\n⚠️  Database verification failed: {str(e)}")
        print("   This may indicate database connectivity issues")

    # Generate report
    runner.generate_report()

    # Print summary
    runner.print_final_summary(all_passed)

    # Exit with appropriate code
    sys.exit(0 if all_passed else 1)


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
