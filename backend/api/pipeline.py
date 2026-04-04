"""
Manual pipeline trigger endpoints (protected by a simple token).
Use these to run the daily job manually or to process a specific paper.
"""
import os
from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from scheduler import process_single_paper
from services.fetcher import fetch_all
from services.lit_review import seed_review, SUBFIELD_DISPLAY_NAMES

router = APIRouter()


def verify_token(x_admin_token: str | None = Header(default=None)):
    expected = os.environ.get("ADMIN_TOKEN", "plasma-admin-secret")
    if x_admin_token != expected:
        raise HTTPException(status_code=401, detail="Invalid admin token.")
    return True


@router.post("/run-daily")
async def run_daily_job(
    target_date: str | None = None,
    _auth=Depends(verify_token),
    db: AsyncSession = Depends(get_db),
):
    """Manually trigger the daily fetch job for a given date (YYYY-MM-DD)."""
    if target_date:
        td = date.fromisoformat(target_date)
    else:
        from datetime import timedelta
        td = date.today() - timedelta(days=1)

    papers = await fetch_all(td)
    processed = 0
    import asyncio
    for paper in papers:
        try:
            ok = await process_single_paper(paper, db)
            if ok:
                processed += 1
            await asyncio.sleep(0.8)
        except Exception as e:
            continue

    await db.commit()
    return {"message": f"Processed {processed}/{len(papers)} papers for {td}"}


@router.post("/seed-literature/{subfield}")
async def trigger_seed(
    subfield: str,
    _auth=Depends(verify_token),
    db: AsyncSession = Depends(get_db),
):
    """Generate or regenerate the historical literature review for a subfield."""
    if subfield not in SUBFIELD_DISPLAY_NAMES:
        raise HTTPException(status_code=404, detail=f"Unknown subfield: {subfield}")

    content = await seed_review(db, subfield)
    await db.commit()
    return {"subfield": subfield, "chars_generated": len(content)}


@router.post("/analyze-paper")
async def analyze_single(
    arxiv_id: str,
    _auth=Depends(verify_token),
    db: AsyncSession = Depends(get_db),
):
    """Fetch and analyze a single arXiv paper by ID."""
    from datetime import timedelta
    import httpx, xmltodict

    url = f"http://export.arxiv.org/api/query?id_list={arxiv_id}"
    async with httpx.AsyncClient(timeout=30) as client:
        r = await client.get(url)
    data = xmltodict.parse(r.text)
    entry = data.get("feed", {}).get("entry", {})
    if not entry:
        raise HTTPException(status_code=404, detail=f"arXiv ID not found: {arxiv_id}")

    from services.fetcher import _is_plasma_relevant
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

    ok = await process_single_paper(paper, db)
    await db.commit()
    return {"arxiv_id": arxiv_id, "processed": ok}
