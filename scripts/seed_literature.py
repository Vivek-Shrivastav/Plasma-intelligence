#!/usr/bin/env python3
"""
One-time script: generate historical literature reviews for all subfields.
Uses Gemini 2.0 Flash (free tier) — run once, ~20-25 minutes total.

Usage:
    cd backend
    python ../scripts/seed_literature.py
    python ../scripts/seed_literature.py --subfield magnetic-reconnection  # single subfield
"""
import asyncio
import argparse
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from dotenv import load_dotenv
load_dotenv(Path(__file__).parent.parent / ".env")

from database import create_tables, AsyncSessionLocal
from services.lit_review import seed_review, SUBFIELD_DISPLAY_NAMES


async def main(target_subfield: str | None = None):
    await create_tables()

    subfields = (
        [target_subfield]
        if target_subfield
        else list(SUBFIELD_DISPLAY_NAMES.keys())
    )

    print(f"\nSeeding {len(subfields)} literature review(s)...\n")

    async with AsyncSessionLocal() as db:
        for i, subfield in enumerate(subfields, 1):
            display = SUBFIELD_DISPLAY_NAMES.get(subfield, subfield)
            print(f"Seeding subfield {i} of {len(subfields)}: {display}...")
            try:
                content = await seed_review(db, subfield)
                await db.commit()
                print(f"  ✓ {len(content)} characters written\n")
                time.sleep(5)  # respect rate limits between subfields
            except Exception as e:
                print(f"  ✗ Failed: {e}\n")
                await db.rollback()

    print("Done! All literature reviews seeded.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--subfield", help="Seed only one specific subfield slug")
    args = parser.parse_args()
    asyncio.run(main(args.subfield))
