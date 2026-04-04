"""
Literature review endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from models.lit_review import LiteratureReview
from services.lit_review import SUBFIELD_DISPLAY_NAMES

router = APIRouter()


@router.get("/")
async def list_reviews(db: AsyncSession = Depends(get_db)):
    """List all available literature reviews with metadata."""
    result = await db.execute(select(LiteratureReview))
    reviews = result.scalars().all()
    return [
        {
            "subfield": r.subfield,
            "name": SUBFIELD_DISPLAY_NAMES.get(r.subfield, r.subfield),
            "paper_count": r.paper_count,
            "last_updated": r.last_updated_at.isoformat() if r.last_updated_at else None,
            "is_seeded": r.is_seeded,
            "earliest_year": r.earliest_year,
        }
        for r in reviews
    ]


@router.get("/{subfield}")
async def get_review(subfield: str, db: AsyncSession = Depends(get_db)):
    """Return full literature review markdown for a subfield."""
    result = await db.execute(
        select(LiteratureReview).where(LiteratureReview.subfield == subfield)
    )
    review = result.scalar_one_or_none()
    if not review:
        raise HTTPException(
            status_code=404,
            detail=f"No literature review found for '{subfield}'. Run the seed script first.",
        )
    return {
        "subfield": review.subfield,
        "name": SUBFIELD_DISPLAY_NAMES.get(review.subfield, review.subfield),
        "content_markdown": review.content_markdown,
        "paper_count": review.paper_count,
        "last_updated": review.last_updated_at.isoformat() if review.last_updated_at else None,
        "is_seeded": review.is_seeded,
    }
