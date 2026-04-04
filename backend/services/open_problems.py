"""
Extracts and clusters open problems from analyzed papers.
"""
import json
import logging
import os
from datetime import date
from typing import Any

import anthropic
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from models.open_problem import OpenProblem, OpenProblemCluster
from prompts import OPEN_PROBLEMS_SYNTHESIS_PROMPT

logger = logging.getLogger(__name__)


async def save_open_problems(
    db: AsyncSession,
    paper_id: str,
    problems: list[dict[str, Any]],
    published_date: date,
):
    """Save extracted open problems to database."""
    for prob in problems:
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
    Weekly job: re-cluster all open problems using Claude Opus.
    Replaces the existing clusters table.
    """
    client = anthropic.AsyncAnthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    # Fetch recent open problems (last 90 days)
    from datetime import timedelta
    cutoff = date.today() - timedelta(days=90)

    result = await db.execute(
        select(OpenProblem, func.count(OpenProblem.id))
        .join(
            # join with papers to get published date
            __import__("models.paper", fromlist=["Paper"]).Paper,
            OpenProblem.paper_id == __import__("models.paper", fromlist=["Paper"]).Paper.id,
        )
        .group_by(OpenProblem.description)
        .limit(200)
    )

    # Simpler: just fetch all open problems
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
        message = await client.messages.create(
            model="claude-opus-4-5",
            max_tokens=3000,
            system=OPEN_PROBLEMS_SYNTHESIS_PROMPT,
            messages=[{"role": "user", "content": user_content}],
        )
        raw = message.content[0].text.strip()
        raw = raw.removeprefix("```json").removeprefix("```").removesuffix("```").strip()
        data = json.loads(raw)

        # Clear old clusters and save new ones
        from sqlalchemy import delete
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
