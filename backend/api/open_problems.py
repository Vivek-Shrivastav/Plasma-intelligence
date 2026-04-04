"""
Open problems endpoints.
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from models.open_problem import OpenProblem, OpenProblemCluster
from models.paper import Paper

router = APIRouter()


@router.get("/clusters")
async def get_clusters(
    urgency: str | None = None,
    subfield: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    """Return synthesized open problem clusters."""
    query = select(OpenProblemCluster).order_by(
        desc(OpenProblemCluster.frequency),
        desc(OpenProblemCluster.last_appeared),
    )
    result = await db.execute(query)
    clusters = result.scalars().all()

    out = []
    for c in clusters:
        if urgency and c.urgency != urgency:
            continue
        if subfield and subfield not in (c.subfields or []):
            continue
        out.append({
            "id": str(c.id),
            "theme": c.theme,
            "description": c.description,
            "subfields": c.subfields or [],
            "urgency": c.urgency,
            "frequency": c.frequency,
            "first_appeared": c.first_appeared.isoformat() if c.first_appeared else None,
            "last_appeared": c.last_appeared.isoformat() if c.last_appeared else None,
            "synthesized_at": c.synthesized_at.isoformat() if c.synthesized_at else None,
        })
    return {"clusters": out, "count": len(out)}


@router.get("/raw")
async def get_raw_problems(
    subfield: str | None = None,
    limit: int = Query(default=100, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
):
    """Return raw extracted open problems with paper info."""
    result = await db.execute(
        select(OpenProblem, Paper.title, Paper.published_date, Paper.arxiv_id)
        .join(Paper, OpenProblem.paper_id == Paper.id)
        .order_by(desc(Paper.published_date))
        .limit(limit)
    )
    rows = result.all()

    out = []
    for prob, title, pub_date, arxiv_id in rows:
        if subfield and subfield not in (prob.subfields or []):
            continue
        out.append({
            "id": str(prob.id),
            "description": prob.description,
            "subfields": prob.subfields or [],
            "specificity": prob.specificity,
            "evidence": prob.evidence,
            "paper_title": title,
            "paper_date": pub_date.isoformat() if pub_date else None,
            "arxiv_id": arxiv_id,
        })
    return {"problems": out, "count": len(out)}
