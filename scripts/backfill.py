#!/usr/bin/env python3
"""
Backfill script: fetch and process papers from the past N months.
Uses Gemini 2.0 Flash (free tier) for analysis.
Run once after initial deployment.

Usage:
    cd backend
    python ../scripts/backfill.py --months 3
    python ../scripts/backfill.py --months 1 --start-date 2025-03-01
"""
import asyncio
import argparse
import sys
from pathlib import Path
from datetime import date, timedelta

sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from dotenv import load_dotenv
load_dotenv(Path(__file__).parent.parent / ".env")

from database import create_tables, AsyncSessionLocal
from services.fetcher import fetch_all
from scheduler import process_single_paper


async def main(months: int, start_date_str: str | None = None):
    await create_tables()

    if start_date_str:
        start = date.fromisoformat(start_date_str)
    else:
        start = date.today() - timedelta(days=months * 30)

    end = date.today() - timedelta(days=1)
    total_days = (end - start).days

    print(f"\nBackfilling {total_days} days ({start} → {end})...\n")

    total_processed = 0
    current = start

    while current <= end:
        print(f"  Fetching {current}...", end=" ", flush=True)
        try:
            papers = await fetch_all(current)
            print(f"{len(papers)} papers found")

            async with AsyncSessionLocal() as db:
                day_count = 0
                for j, paper in enumerate(papers):
                    try:
                        ok = await process_single_paper(paper, db)
                        if ok:
                            day_count += 1
                        if (j + 1) % 5 == 0:
                            print(f"    Progress: {j+1}/{len(papers)} papers processed")
                        await asyncio.sleep(4.5) # Gentle pace (13 RPM)
                    except Exception as e:
                        print(f"    ! Error processing paper: {e}")
                        continue
                await db.commit()
                total_processed += day_count
                print(f"    → processed {day_count}/{len(papers)}")

        except Exception as e:
            print(f"    ✗ Error: {e}")

        current += timedelta(days=1)
        await asyncio.sleep(2)

    print(f"\nBackfill complete. Total papers processed: {total_processed}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--months", type=int, default=3)
    parser.add_argument("--start-date", help="YYYY-MM-DD")
    args = parser.parse_args()
    asyncio.run(main(args.months, args.start_date))
