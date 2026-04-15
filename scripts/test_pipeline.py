#!/usr/bin/env python3
"""
Test the full pipeline with a single arXiv paper.
Uses Gemini 2.0 Flash for analysis. 

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
    import gemini_client
    from services.fetcher import _is_plasma_relevant

    print(f"\nTesting pipeline with arXiv:{arxiv_id}")
    print("-" * 60)

    # 1. Fetch paper metadata from arXiv
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

    print(f"Title: {title[:80]}")
    print(f"Authors: {', '.join([a.get('name', '') for a in authors_raw][:3])}")
    print(f"Plasma relevant: {_is_plasma_relevant(title, abstract)}")
    print()

    # 2. Analyze with Gemini
    print("Running Gemini analysis...")
    analysis = gemini_client.analyze_paper(title, abstract)

    if not analysis:
        print("✗ Analysis failed")
        return

    print(f"✓ Analysis complete\n")
    print(f"  Headline: {analysis.get('headline')}")
    print(f"  Summary: {analysis.get('summary', analysis.get('short_summary', ''))[:150]}...")
    print(f"  Key findings: {analysis.get('key_findings', [])[:3]}")
    print()

    # 3. Extract open problems
    print("Extracting open problems...")
    problems = gemini_client.extract_open_problems(title, abstract, analysis)
    print(f"✓ Found {len(problems)} open problems")
    for op in problems:
        print(f"  - {op}")
    print()

    # 4. Get embedding
    print("Getting embedding...")
    embedding = gemini_client.get_embedding(f"{title} {abstract}")
    print(f"✓ Embedding dimension: {len(embedding)}")
    print(f"  First 5 values: {embedding[:5]}")
    print()

    # 5. Full analysis JSON
    print("Full analysis JSON:")
    print(json.dumps(analysis, indent=2))
    print()

    print("=" * 60)
    print("PIPELINE TEST PASSED")
    print("=" * 60)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--arxiv-id", default=DEFAULT_ARXIV_ID)
    args = parser.parse_args()
    asyncio.run(main(args.arxiv_id))
