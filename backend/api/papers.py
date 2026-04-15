"""
Paper endpoints: daily digest, paper detail, search.
"""
from datetime import date, timedelta
from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, desc, and_, cast
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from models.paper import Paper

router = APIRouter()


def paper_to_dict(p: Paper) -> dict[str, Any]:
    return {
        "id": str(p.id),
        "arxiv_id": p.arxiv_id,
        "doi": p.doi,
        "title": p.title,
        "authors": p.authors,
        "journal": p.journal,
        "published_date": p.published_date.isoformat() if p.published_date else None,
        "field": p.field,
        "subfields": p.subfields or [],
        "importance_score": p.importance_score,
        "technical_depth": p.technical_depth,
        "headline": p.headline,
        "short_summary": p.short_summary,
        "keywords": p.keywords or [],
        "concepts_detected": p.concepts_detected or [],
        "figures": p.figures or [],
        "pdf_url": p.pdf_url,
        "paper_url": p.paper_url,
        "analysis": p.analysis,
    }


@router.get("/today")
async def get_today(db: AsyncSession = Depends(get_db)):
    """Return yesterday's papers sorted by importance (the 'today' newspaper)."""
    yesterday = date.today() - timedelta(days=1)
    result = await db.execute(
        select(Paper)
        .where(
            and_(
                Paper.published_date == yesterday,
                Paper.analysis_failed == False,
            )
        )
        .order_by(desc(Paper.importance_score))
    )
    papers = result.scalars().all()
    return {"date": date.today().isoformat(), "papers": [paper_to_dict(p) for p in papers]}


@router.get("/date/{date_str}")
async def get_by_date(date_str: str, db: AsyncSession = Depends(get_db)):
    """Return all papers for a specific date (YYYY-MM-DD)."""
    try:
        target = date.fromisoformat(date_str)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD.")
    result = await db.execute(
        select(Paper)
        .where(
            and_(
                Paper.published_date == target,
                Paper.analysis_failed == False,
            )
        )
        .order_by(desc(Paper.importance_score))
    )
    papers = result.scalars().all()
    return {"date": date_str, "papers": [paper_to_dict(p) for p in papers]}


@router.get("/{paper_id}")
async def get_paper(paper_id: UUID, db: AsyncSession = Depends(get_db)):
    """Return full detail for a single paper."""
    result = await db.execute(select(Paper).where(Paper.id == paper_id))
    paper = result.scalar_one_or_none()
    if not paper:
        raise HTTPException(status_code=404, detail="Paper not found.")
    return paper_to_dict(paper)


@router.get("/")
async def list_papers(
    field: str | None = None,
    subfield: str | None = None,
    min_score: int = Query(default=1, ge=1, le=10),
    days: int = Query(default=30, ge=1, le=365),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
):
    """List papers with optional filters."""
    cutoff = date.today() - timedelta(days=days)
    conditions = [
        Paper.published_date >= cutoff,
        Paper.analysis_failed == False,
        Paper.importance_score >= min_score,
    ]
    if field:
        conditions.append(Paper.field == field)
    if subfield:
        conditions.append(
            Paper.subfields.cast(JSONB).contains(cast([subfield], JSONB))
        )

    result = await db.execute(
        select(Paper)
        .where(and_(*conditions))
        .order_by(desc(Paper.importance_score), desc(Paper.published_date))
        .limit(limit)
        .offset(offset)
    )
    papers = result.scalars().all()
    return {"papers": [paper_to_dict(p) for p in papers], "count": len(papers)}
