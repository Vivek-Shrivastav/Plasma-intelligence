"""
Sends papers to Claude API for structured plasma physics analysis.
"""
import json
import logging
import os
from typing import Any

import anthropic
from tenacity import retry, stop_after_attempt, wait_exponential

from prompts import (
    PAPER_ANALYSIS_PROMPT,
    FIGURE_DESCRIPTION_PROMPT,
    OPEN_PROBLEMS_PROMPT,
)

logger = logging.getLogger(__name__)

_client: anthropic.AsyncAnthropic | None = None


def get_client() -> anthropic.AsyncAnthropic:
    global _client
    if _client is None:
        _client = anthropic.AsyncAnthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    return _client


@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=2, min=4, max=30))
async def analyze_paper(paper: dict[str, Any]) -> dict[str, Any] | None:
    """
    Send a paper to Claude Sonnet for full plasma physics analysis.
    Returns structured JSON or None on persistent failure.
    """
    client = get_client()

    parts = [
        f"Title: {paper['title']}",
        f"Authors: {', '.join(paper['authors'][:8])}",
        f"Journal: {paper.get('journal', 'arXiv')}",
        f"Published: {paper.get('published_date', '')}",
        f"\nAbstract:\n{paper['abstract']}",
    ]
    if paper.get("full_text"):
        parts.append(f"\nKey excerpts from full text:\n{paper['full_text'][:5000]}")
    if paper.get("figure_descriptions"):
        parts.append(f"\nFigure descriptions:\n{paper['figure_descriptions']}")

    try:
        message = await client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=3000,
            system=PAPER_ANALYSIS_PROMPT,
            messages=[{"role": "user", "content": "\n\n".join(parts)}],
        )
        raw = message.content[0].text.strip()
        # Strip any accidental markdown fences
        raw = raw.removeprefix("```json").removeprefix("```").removesuffix("```").strip()
        return json.loads(raw)

    except json.JSONDecodeError as e:
        logger.error(f"JSON parse error for '{paper['title'][:60]}': {e}")
        return None
    except anthropic.APIError as e:
        logger.error(f"Anthropic API error: {e}")
        raise  # let tenacity retry


@retry(stop=stop_after_attempt(2), wait=wait_exponential(multiplier=2, min=2, max=10))
async def describe_figure(image_bytes: bytes, paper_context: str) -> str:
    """Send a figure image to Claude Vision for description."""
    import base64

    client = get_client()

    try:
        message = await client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=300,
            system=FIGURE_DESCRIPTION_PROMPT,
            messages=[{
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": "image/png",
                            "data": base64.standard_b64encode(image_bytes).decode(),
                        },
                    },
                    {"type": "text", "text": f"Paper context: {paper_context[:500]}"},
                ],
            }],
        )
        return message.content[0].text.strip()
    except Exception as e:
        logger.error(f"Figure description failed: {e}")
        return "Figure description unavailable."


@retry(stop=stop_after_attempt(2), wait=wait_exponential(multiplier=2, min=2, max=10))
async def extract_open_problems(analysis: dict[str, Any]) -> list[dict]:
    """Extract structured open problems from a paper analysis."""
    client = get_client()

    try:
        message = await client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=800,
            system=OPEN_PROBLEMS_PROMPT,
            messages=[{
                "role": "user",
                "content": json.dumps(analysis, indent=2)
            }],
        )
        raw = message.content[0].text.strip()
        raw = raw.removeprefix("```json").removeprefix("```").removesuffix("```").strip()
        result = json.loads(raw)
        return result if isinstance(result, list) else []
    except Exception as e:
        logger.error(f"Open problems extraction failed: {e}")
        return []
