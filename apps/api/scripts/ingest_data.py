#!/usr/bin/env python3
# apps/api/scripts/ingest_data.py
"""
CLI script for testing and running data ingestion locally.
Usage: python ingest_data.py --source HHS_TRANSPARENCY --file path/to/file.json
"""

import asyncio
import argparse
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.data_ingestion import IngestSource
from app.services.data_ingestion.ingestion_engine import DataIngestionEngine


async def main():
    parser = argparse.ArgumentParser(description="Evijnar Data Ingestion CLI")
    parser.add_argument(
        "--source",
        type=str,
        required=True,
        choices=["HHS_TRANSPARENCY", "EHDS", "ABDM"],
        help="Data source",
    )
    parser.add_argument(
        "--file",
        type=str,
        required=True,
        help="Path to JSON file to ingest",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Dry run - don't write to database",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=100,
        help="Batch size for processing",
    )

    args = parser.parse_args()

    # Validate file exists
    filepath = Path(args.file)
    if not filepath.exists():
        print(f"❌ File not found: {args.file}")
        sys.exit(1)

    print(f"🚀 Starting Evijnar Data Ingestion")
    print(f"   Source: {args.source}")
    print(f"   File: {args.file}")
    print(f"   Dry Run: {args.dry_run}")
    print()

    try:
        # Initialize engine
        engine = DataIngestionEngine(batch_size=args.batch_size)
        await engine.initialize()
        print("✅ Engine initialized")

        # Run ingestion
        source = IngestSource[args.source]
        report = await engine.ingest_file(str(filepath), source, dry_run=args.dry_run)

        # Print results
        print()
        print("=" * 60)
        print("INGESTION REPORT")
        print("=" * 60)
        print(f"Job ID:              {report.job_id}")
        print(f"Total Records:       {report.total_records}")
        print(f"✅ Succeeded:        {report.succeeded}")
        print(f"❌ Failed:           {report.failed}")
        print(f"⏭️  Skipped:          {report.skipped}")
        print(f"Success Rate:        {report.success_rate:.1f}%")
        print()
        print(f"Hospitals Created:   {report.hospitals_created}")
        print(f"Procedures Created:  {report.procedures_created}")
        print(f"Normalizers Created: {report.normalizers_created}")
        print()
        print(f"Processing Time:     {report.processing_time_seconds:.2f}s")

        # Print LLM stats
        llm_stats = engine.get_llm_usage()
        print()
        print("LLM Usage Statistics:")
        print(f"  Total Calls:       {llm_stats.get('total_calls', 0)}")
        print(f"  Total Tokens:      {llm_stats.get('total_tokens', 0)}")
        print(f"  Cached Responses:  {llm_stats.get('total_cached', 0)}")
        print(f"  Estimated Cost:    ${llm_stats.get('estimated_cost_usd', 0):.2f}")

        # Print errors if any
        if report.errors:
            print()
            print(f"Errors ({len(report.errors)} total):")
            for error in report.errors[:5]:  # Show first 5
                print(f"  - {error.source_id}: {error.error_message}")
            if len(report.errors) > 5:
                print(f"  ... and {len(report.errors) - 5} more")

        print()
        print("=" * 60)

        # Exit with appropriate code
        sys.exit(0 if report.is_complete and report.success_rate > 80 else 1)

    except Exception as e:
        print(f"❌ Ingestion failed: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
