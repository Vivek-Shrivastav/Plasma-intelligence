"""
Manages the living literature reviews per subfield.
Append-only: historical backbone written once, daily patches appended.
"""
import asyncio
import logging
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.lit_review import LiteratureReview
import gemini_client

logger = logging.getLogger(__name__)

SUBFIELD_DISPLAY_NAMES = {
    "magnetic-reconnection": "Magnetic Reconnection",
    "plasma-turbulence": "Plasma Turbulence",
    "two-stream-instability": "Two-Stream Instability",
    "tokamak": "Tokamak Physics",
    "stellarator": "Stellarator Physics",
    "solar-wind": "Solar Wind Plasma",
    "magnetosphere": "Magnetospheric Physics",
    "mhd-waves": "MHD Waves",
    "kinetic-effects": "Kinetic Effects in Plasmas",
    "plasma-heating": "Plasma Heating",
    "confinement": "Plasma Confinement",
    "transport": "Plasma Transport",
    "shocks": "Collisionless Shocks",
    "accretion-disks": "Accretion Disk Plasma",
    "pic-simulations": "PIC Simulations",
    "drift-waves": "Drift Waves",
    "plasma-instability": "Plasma Instabilities",
    "diagnostics": "Plasma Diagnostics",
}

async def get_or_create_review(db: AsyncSession, subfield: str) -> LiteratureReview:
    result = await db.execute(
        select(LiteratureReview).where(LiteratureReview.subfield == subfield)
    )
    review = result.scalar_one_or_none()
    if review is None:
        review = LiteratureReview(
            subfield=subfield,
            content_markdown="",
            paper_count=0,
            is_seeded=False,
        )
        db.add(review)
        await db.flush()
    return review

async def generate_patch(
    subfield: str,
    paper: dict[str, Any],
    analysis: dict[str, Any],
    existing_tail: str,
) -> str:
    """Generate a patch paragraph to append to a literature review."""
    year = str(paper.get("published_date", ""))[:4]
    paper_summary = analysis.get("short_summary", analysis.get("summary", ""))
    
    # gemini_client expects new_papers: list[dict]
    new_paper_dict = {
        "title": paper["title"],
        "summary": paper_summary
    }

    try:
        return await asyncio.to_thread(
            gemini_client.generate_literature_review_patch,
            subfield=subfield,
            new_papers=[new_paper_dict],
            existing_review=existing_tail
        )
    except Exception as e:
        logger.error(f"Gemini API lit review patch failed: {e}")
        return ""

async def append_to_review(
    db: AsyncSession,
    paper: dict[str, Any],
    analysis: dict[str, Any],
):
    """Append new paper to all relevant subfield literature reviews."""
    subfields: list[str] = analysis.get("subfield", [])
    if not subfields:
        return

    for subfield_raw in subfields:
        subfield = subfield_raw.lower().replace(" ", "-").replace("_", "-")
        if subfield not in SUBFIELD_DISPLAY_NAMES:
            continue

        try:
            review = await get_or_create_review(db, subfield)

            # If not seeded yet, add a placeholder header
            if not review.content_markdown:
                display = SUBFIELD_DISPLAY_NAMES.get(subfield, subfield)
                review.content_markdown = (
                    f"## Literature Review: {display}\n\n"
                    f"*This review is being built automatically. "
                    f"Run `scripts/seed_literature.py` to generate the full historical foundation.*\n\n"
                    f"### Recent Developments\n\n"
                )

            patch = await generate_patch(
                subfield=subfield,
                paper=paper,
                analysis=analysis,
                existing_tail=review.content_markdown,
            )

            review.content_markdown += f"\n\n{patch}"
            review.paper_count = (review.paper_count or 0) + 1

            logger.info(f"Appended to lit review: {subfield}")

        except Exception as e:
            logger.error(f"Failed to append to {subfield} lit review: {e}")

async def seed_review(db: AsyncSession, subfield: str, founding_papers: list[dict] = None) -> str:
    """
    Generate the full historical literature review for a subfield.
    """
    if founding_papers is None:
        founding_papers = []

    display = SUBFIELD_DISPLAY_NAMES.get(subfield, subfield)

    try:
        content = await asyncio.to_thread(
            gemini_client.seed_literature_review,
            subfield=display,
            founding_papers=founding_papers
        )
    except Exception as e:
        logger.error(f"Gemini API seed lit review failed: {e}")
        content = ""

    review = await get_or_create_review(db, subfield)
    review.content_markdown = content
    review.is_seeded = True
    review.paper_count = 0

    return content
