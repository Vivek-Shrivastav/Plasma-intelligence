"""
Subfield endpoints: feed for last 6 months per subfield.
"""
from datetime import date, timedelta
from typing import Any

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, desc, and_, cast
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from models.paper import Paper
from services.lit_review import SUBFIELD_DISPLAY_NAMES

router = APIRouter()

SUBFIELD_SLUGS = list(SUBFIELD_DISPLAY_NAMES.keys())


@router.get("/")
async def list_subfields():
    """Return all available subfields with display names."""
    return [
        {"slug": slug, "name": name}
        for slug, name in SUBFIELD_DISPLAY_NAMES.items()
    ]


@router.get("/{slug}")
async def get_subfield_feed(
    slug: str,
    days: int = Query(default=180, ge=1, le=365),
    min_score: int = Query(default=1, ge=1, le=10),
    limit: int = Query(default=100, ge=1, le=300),
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
):
    """Return papers for a subfield, default last 6 months."""
    if slug not in SUBFIELD_DISPLAY_NAMES:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail=f"Unknown subfield: {slug}")

    cutoff = date.today() - timedelta(days=days)

    # Match subfield slug against stored subfields array
    result = await db.execute(
        select(Paper)
        .where(
            and_(
                Paper.published_date >= cutoff,
                Paper.analysis_failed == False,
                Paper.importance_score >= min_score,
                Paper.subfields.cast(JSONB).contains(
                    cast([slug.replace("-", " ")], JSONB)
                ),
            )
        )
        .order_by(desc(Paper.importance_score), desc(Paper.published_date))
        .limit(limit)
        .offset(offset)
    )
    papers = result.scalars().all()

    from api.papers import paper_to_dict
    return {
        "slug": slug,
        "name": SUBFIELD_DISPLAY_NAMES[slug],
        "papers": [paper_to_dict(p) for p in papers],
        "count": len(papers),
    }
