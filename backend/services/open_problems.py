"""
Extracts and clusters open problems from analyzed papers.
"""
import asyncio
import json
import logging
from datetime import date
from typing import Any

from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from models.open_problem import OpenProblem, OpenProblemCluster
import gemini_client

logger = logging.getLogger(__name__)


async def save_open_problems(
    db: AsyncSession,
    paper_id: str,
    problems: list,
    published_date: date,
):
    """Save extracted open problems to database."""
    for prob in problems:
        if isinstance(prob, str):
            # gemini_client returns list[str]
            op = OpenProblem(
                paper_id=paper_id,
                description=prob,
                subfields=[],
                specificity="medium",
                evidence="",
            )
        else:
            # dict format
            op = OpenProblem(
                paper_id=paper_id,
                description=prob.get("problem", ""),
                subfields=prob.get("subfields", []),
                specificity=prob.get("specificity", "medium"),
                evidence=prob.get("evidence", ""),
            )
        db.add(op)
    await db.flush()


async def synthesize_clusters(db: AsyncSession):
    """
    Weekly job: re-cluster all open problems using Gemini.
    Replaces the existing clusters table.
    """
    # Fetch recent open problems
    result = await db.execute(select(OpenProblem).limit(300))
    problems = result.scalars().all()

    if not problems:
        logger.info("No open problems to synthesize")
        return

    # Group by description for frequency counting
    problem_list = [
        {
            "problem": p.description,
            "subfields": p.subfields,
            "occurrence": 1,
        }
        for p in problems
    ]

    user_content = f"Open problems from recent plasma physics papers:\n\n{json.dumps(problem_list, indent=2)}"

    try:
        from google.generativeai import GenerativeModel
        import time

        time.sleep(4.1)
        model = GenerativeModel("gemini-2.0-flash")

        prompt = f"""You are a plasma physics research strategist synthesizing the landscape of open problems.

You will receive a list of open problems extracted from recent papers. Each has a description, subfields, and occurrence count.

Your task:
1. GROUP similar problems into THEMES
2. For each theme write a synthesis

Return JSON:
{{
  "clusters": [
    {{
      "theme": "<short name, max 8 words>",
      "description": "<2-3 precise sentences about why this is hard and what solving it would unlock>",
      "subfields": ["<list>"],
      "urgency": "<high | medium | low>",
      "paper_count": <int>,
      "first_seen": "<YYYY-MM>",
      "last_seen": "<YYYY-MM>"
    }}
  ]
}}

Order clusters from most to least urgent. Return ONLY the JSON.

{user_content}"""

        resp = await asyncio.to_thread(model.generate_content, prompt)
        raw = resp.text.strip()
        raw = raw.removeprefix("```json").removeprefix("```").removesuffix("```").strip()
        data = json.loads(raw)

        # Clear old clusters and save new ones
        await db.execute(delete(OpenProblemCluster))

        for cluster in data.get("clusters", []):
            c = OpenProblemCluster(
                theme=cluster.get("theme", ""),
                description=cluster.get("description", ""),
                subfields=cluster.get("subfields", []),
                urgency=cluster.get("urgency", "medium"),
                frequency=cluster.get("paper_count", 1),
                first_appeared=_parse_ym(cluster.get("first_seen")),
                last_appeared=_parse_ym(cluster.get("last_seen")),
            )
            db.add(c)

        await db.flush()
        logger.info(f"Synthesized {len(data.get('clusters', []))} open problem clusters")

    except Exception as e:
        logger.error(f"Cluster synthesis failed: {e}")


def _parse_ym(ym_str: str | None) -> date | None:
    if not ym_str:
        return None
    try:
        parts = ym_str.split("-")
        return date(int(parts[0]), int(parts[1]) if len(parts) > 1 else 1, 1)
    except Exception:
        return None
