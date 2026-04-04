"""
Manages the living literature reviews per subfield.
Append-only: historical backbone written once, daily patches appended.
"""
import json
import logging
import os
from datetime import date
from typing import Any

import anthropic
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from tenacity import retry, stop_after_attempt, wait_exponential

from models.lit_review import LiteratureReview
from prompts import LIT_PATCH_PROMPT, LIT_SEED_PROMPT_TEMPLATE

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


@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=2, min=4, max=20))
async def generate_patch(
    subfield: str,
    paper: dict[str, Any],
    analysis: dict[str, Any],
    existing_tail: str,
) -> str:
    """Generate a patch paragraph to append to a literature review."""
    client = anthropic.AsyncAnthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    year = str(paper.get("published_date", ""))[:4]
    first_author = paper.get("authors", ["Unknown"])[0].split(",")[0]
    citation = f"({first_author}{year})"

    user_content = f"""SUBFIELD: {subfield}

CURRENT REVIEW (last section, for continuity):
{existing_tail[-2500:] if existing_tail else "(No content yet — this is the first entry)"}

NEW PAPER:
Title: {paper['title']}
Authors: {', '.join(paper.get('authors', [])[:5])} {year}
Citation key: {citation}
Field: {analysis.get('field', '')}
Short summary: {analysis.get('short_summary', '')}
Key contributions: {json.dumps(analysis.get('key_contributions', []))}
Methods: {json.dumps(analysis.get('methods_used', []))}
Open problems: {json.dumps(analysis.get('open_problems', []))}
Positioning: {analysis.get('literature_context', {}).get('positioning', '')}"""

    message = await client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=500,
        system=LIT_PATCH_PROMPT,
        messages=[{"role": "user", "content": user_content}],
    )
    return message.content[0].text.strip()


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


async def seed_review(db: AsyncSession, subfield: str) -> str:
    """
    Generate the full historical literature review for a subfield.
    Run once per subfield via scripts/seed_literature.py.
    """
    client = anthropic.AsyncAnthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    display = SUBFIELD_DISPLAY_NAMES.get(subfield, subfield)

    prompt = LIT_SEED_PROMPT_TEMPLATE.format(
        subfield=display,
        subfield_title=display,
        today=date.today().isoformat(),
    )

    message = await client.messages.create(
        model="claude-opus-4-5",
        max_tokens=4000,
        messages=[{"role": "user", "content": prompt}],
    )
    content = message.content[0].text.strip()

    review = await get_or_create_review(db, subfield)
    review.content_markdown = content
    review.is_seeded = True
    review.paper_count = 0

    return content
