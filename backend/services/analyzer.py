"""
Sends papers to Groq API for structured plasma physics analysis.
"""
import json
import logging
import os
from typing import Any

from groq import AsyncGroq
from tenacity import retry, stop_after_attempt, wait_exponential

from prompts import (
    PAPER_ANALYSIS_PROMPT,
    OPEN_PROBLEMS_PROMPT,
)

logger = logging.getLogger(__name__)
_client: AsyncGroq | None = None
MODEL = "llama-3.3-70b-versatile"

def get_client() -> AsyncGroq:
    global _client
    if _client is None:
        _client = AsyncGroq(api_key=os.environ["GROQ_API_KEY"])
    return _client

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=2, min=4, max=30))
async def analyze_paper(paper: dict[str, Any]) -> dict[str, Any] | None:
    client = get_client()
    parts = [
        f"Title: {paper['title']}",
        f"Authors: {', '.join(paper['authors'][:8])}",
        f"Journal: {paper.get('journal', 'arXiv')}",
        f"Published: {paper.get('published_date', '')}",
        f"\nAbstract:\n{paper['abstract']}",
    ]
    if paper.get("full_text"):
        parts.append(f"\nKey excerpts:\n{paper['full_text'][:5000]}")
    try:
        response = await client.chat.completions.create(
            model=MODEL,
            max_tokens=3000,
            messages=[
                {"role": "system", "content": PAPER_ANALYSIS_PROMPT},
                {"role": "user", "content": "\n\n".join(parts)},
            ],
        )
        raw = response.choices[0].message.content.strip()
        raw = raw.removeprefix("```json").removeprefix("```").removesuffix("```").strip()
        return json.loads(raw)
    except json.JSONDecodeError as e:
        logger.error(f"JSON parse error: {e}")
        return None
    except Exception as e:
        logger.error(f"Groq API error: {e}")
        raise

async def describe_figure(image_bytes: bytes, paper_context: str) -> str:
    return "Figure description unavailable."

@retry(stop=stop_after_attempt(2), wait=wait_exponential(multiplier=2, min=2, max=10))
async def extract_open_problems(analysis: dict[str, Any]) -> list[dict]:
    client = get_client()
    try:
        response = await client.chat.completions.create(
            model=MODEL,
            max_tokens=800,
            messages=[
                {"role": "system", "content": OPEN_PROBLEMS_PROMPT},
                {"role": "user", "content": json.dumps(analysis, indent=2)},
            ],
        )
        raw = response.choices[0].message.content.strip()
        raw = raw.removeprefix("```json").removeprefix("```").removesuffix("```").strip()
        result = json.loads(raw)
        return result if isinstance(result, list) else []
    except Exception as e:
        logger.error(f"Open problems extraction failed: {e}")
        return []
