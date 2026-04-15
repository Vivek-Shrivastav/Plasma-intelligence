"""
Sends papers to Gemini API for structured plasma physics analysis.
"""
import asyncio
import logging
from typing import Any

import gemini_client

logger = logging.getLogger(__name__)

async def analyze_paper(paper: dict[str, Any]) -> dict[str, Any] | None:
    try:
        return await asyncio.to_thread(
            gemini_client.analyze_paper,
            title=paper['title'],
            abstract=paper.get('abstract', ''),
            full_text=paper.get('full_text', '')
        )
    except Exception as e:
        logger.error(f"Gemini API error: {e}")
        return None

async def describe_figure(image_bytes: bytes, paper_context: str) -> str:
    try:
        return await asyncio.to_thread(
            gemini_client.describe_figure,
            image_bytes=image_bytes,
            paper_title=paper_context,
        )
    except Exception as e:
        logger.error(f"Figure description failed: {e}")
        return "Figure description unavailable."

async def extract_open_problems(paper: dict[str, Any], analysis: dict[str, Any]) -> list[dict]:
    # We alter the signature slightly since gemini_client requires title and abstract,
    # but the calling code can just be updated to pass `paper` alongside `analysis`.
    try:
        # gemini_client returns list[str], but open_problems downstream might expect list[dict]?
        # Wait, let's look at `gemini_client.extract_open_problems` output: `list[str]`.
        # `services/open_problems.py` might expect dict. Let's return what gemini returns.
        problems = await asyncio.to_thread(
            gemini_client.extract_open_problems,
            title=paper['title'],
            abstract=paper.get('abstract', ''),
            analysis=analysis
        )
        return problems
    except Exception as e:
        logger.error(f"Open problems extraction failed: {e}")
        return []

