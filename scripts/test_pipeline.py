#!/usr/bin/env python3
"""
Test the full pipeline with a single arXiv paper.

Usage:
    cd backend
    python ../scripts/test_pipeline.py
    python ../scripts/test_pipeline.py --arxiv-id 2401.12345
"""
import asyncio
import argparse
import sys
import json
from pathlib import Path
from datetime import date

sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from dotenv import load_dotenv
load_dotenv(Path(__file__).parent.parent / ".env")

# Well-known plasma physics arXiv paper for testing
DEFAULT_ARXIV_ID = "2310.07788"  # example plasma paper

async def main(arxiv_id: str):
    from database import create_tables, AsyncSessionLocal
    from services.analyzer import analyze_paper
    from services.fetcher import _is_plasma_relevant

    await create_tables()

    print(f"\nTesting pipeline with arXiv:{arxiv_id}")
    print("-" * 60)

    # Fetch paper metadata
    import httpx, xmltodict
    url = f"http://export.arxiv.org/api/query?id_list={arxiv_id}"
    async with httpx.AsyncClient(timeout=30) as client:
        r = await client.get(url)
    data = xmltodict.parse(r.text)
    entry = data.get("feed", {}).get("entry", {})

    if not entry:
        print(f"✗ arXiv ID not found: {arxiv_id}")
        return

    title = entry.get("title", "").replace("\n", " ").strip()
    abstract = entry.get("summary", "").replace("\n", " ").strip()
    authors_raw = entry.get("author", [])
    if isinstance(authors_raw, dict):
        authors_raw = [authors_raw]

    paper = {
        "arxiv_id": arxiv_id,
        "title": title,
        "authors": [a.get("name", "") for a in authors_raw],
        "abstract": abstract,
        "journal": "arXiv",
        "published_date": date.today(),
        "pdf_url": f"https://arxiv.org/pdf/{arxiv_id}",
        "paper_url": f"https://arxiv.org/abs/{arxiv_id}",
    }

    print(f"Title: {title[:80]}")
    print(f"Authors: {', '.join(paper['authors'][:3])}")
    print(f"Plasma relevant: {_is_plasma_relevant(title, abstract)}")
    print()

    # Run analysis
    print("Running Claude analysis...")
    analysis = await analyze_paper(paper)

    if not analysis:
        print("✗ Analysis failed")
        return

    print(f"✓ Analysis complete\n")
    print(f"  Headline: {analysis.get('headline')}")
    print(f"  Field: {analysis.get('field')}")
    print(f"  Subfields: {analysis.get('subfield')}")
    print(f"  Importance: {analysis.get('importance_score')}/10")
    print(f"  Depth: {analysis.get('technical_depth')}")
    print(f"  Concepts: {analysis.get('concepts_detected')}")
    print()
    print(f"  Short summary:\n  {analysis.get('short_summary')}")
    print()
    print(f"  Open problems:")
    for op in analysis.get("open_problems", []):
        print(f"    - {op}")
    print()

    # Save to DB
    print("Saving to database...")
    async with AsyncSessionLocal() as db:
        from scheduler import process_single_paper
        ok = await process_single_paper(paper, db)
        await db.commit()
        if ok:
            print("✓ Paper saved successfully")
        else:
            print("✗ Paper not saved (may already exist)")

    print("\nFull analysis JSON:")
    print(json.dumps(analysis, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--arxiv-id", default=DEFAULT_ARXIV_ID)
    args = parser.parse_args()
    asyncio.run(main(args.arxiv_id))
