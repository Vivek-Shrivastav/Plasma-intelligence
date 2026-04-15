"""
APScheduler jobs: daily paper fetch at 02:00 UTC, weekly synthesis on Sundays.
"""
import asyncio
import logging
from datetime import date, timedelta

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy import select

from database import AsyncSessionLocal
from models.paper import Paper
from services import (
    fetch_all,
    analyze_paper,
    download_pdf,
    extract_figures_from_pdf,
    describe_figure,
    upload_figure,
    extract_open_problems,
    append_to_review,
    save_open_problems,
    cleanup_pdf,
    synthesize_clusters,
)

logger = logging.getLogger(__name__)
scheduler = AsyncIOScheduler(timezone="UTC")


async def process_single_paper(paper: dict, db) -> bool:
    """Full pipeline for one paper. Returns True on success."""
    title_short = paper["title"][:70]

    # 1. Check for duplicates
    existing = await db.execute(
        select(Paper).where(Paper.arxiv_id == paper.get("arxiv_id"))
        if paper.get("arxiv_id")
        else select(Paper).where(Paper.title == paper["title"])
    )
    if existing.scalar_one_or_none():
        logger.debug(f"Skipping duplicate: {title_short}")
        return False

    # 2. Analyze with Gemini
    logger.info(f"Analyzing: {title_short}")
    analysis = await analyze_paper(paper)
    if not analysis:
        logger.warning(f"Analysis failed: {title_short}")
        db_paper = Paper(
            arxiv_id=paper.get("arxiv_id"),
            doi=paper.get("doi"),
            title=paper["title"],
            authors=paper["authors"],
            abstract=paper["abstract"],
            journal=paper.get("journal"),
            published_date=paper["published_date"],
            pdf_url=paper.get("pdf_url"),
            paper_url=paper.get("paper_url"),
            analysis_failed=True,
            figures=[],
        )
        db.add(db_paper)
        await db.flush()
        return False

    # 3. Extract and upload figures (best-effort)
    figures = []
    if paper.get("pdf_url") and paper.get("arxiv_id"):
        try:
            pdf_path = await download_pdf(paper["pdf_url"], paper["arxiv_id"])
            if pdf_path:
                raw_figures = extract_figures_from_pdf(pdf_path)
                context = f"{paper['title']}. {analysis.get('short_summary', '')}"
                for i, fig in enumerate(raw_figures):
                    description = await describe_figure(fig["data"], context)
                    uploaded = await upload_figure(
                        fig["data"],
                        paper.get("arxiv_id", "unknown"),
                        i,
                        description,
                    )
                    if uploaded:
                        figures.append(uploaded)
                cleanup_pdf(pdf_path)
        except Exception as e:
            logger.error(f"Figure pipeline failed for {title_short}: {e}")

    # 4. Save paper to database
    db_paper = Paper(
        arxiv_id=paper.get("arxiv_id"),
        doi=paper.get("doi"),
        title=paper["title"],
        authors=paper["authors"],
        abstract=paper["abstract"],
        journal=paper.get("journal"),
        published_date=paper["published_date"],
        pdf_url=paper.get("pdf_url"),
        paper_url=paper.get("paper_url"),
        analysis=analysis,
        field=analysis.get("field"),
        subfields=analysis.get("subfield", []),
        importance_score=analysis.get("importance_score"),
        technical_depth=analysis.get("technical_depth"),
        headline=analysis.get("headline"),
        short_summary=analysis.get("short_summary"),
        keywords=analysis.get("keywords", []),
        concepts_detected=analysis.get("concepts_detected", []),
        figures=figures,
        analysis_failed=False,
    )
    db.add(db_paper)
    await db.flush()

    # 5. Update literature reviews
    await append_to_review(db, paper, analysis)

    # 6. Extract open problems
    problems = await extract_open_problems(paper, analysis)
    if problems:
        await save_open_problems(db, str(db_paper.id), problems, paper["published_date"])

    return True


@scheduler.scheduled_job("cron", hour=2, minute=0, id="daily_fetch")
async def daily_fetch_job():
    """Fetch and process yesterday's papers from all sources."""
    target_date = date.today() - timedelta(days=1)
    logger.info(f"[Daily Job] Starting fetch for {target_date}")

    papers = await fetch_all(target_date)
    processed = 0

    async with AsyncSessionLocal() as db:
        for paper in papers:
            try:
                success = await process_single_paper(paper, db)
                if success:
                    processed += 1
                await asyncio.sleep(1)  # gentle rate limiting
            except Exception as e:
                logger.error(f"Paper processing error: {e}")
                await db.rollback()
                continue

        await db.commit()

    logger.info(f"[Daily Job] Done. Processed {processed}/{len(papers)} papers.")


@scheduler.scheduled_job("cron", day_of_week="sun", hour=3, minute=0, id="weekly_synthesis")
async def weekly_synthesis_job():
    """Re-cluster open problems and update subfield summaries."""
    logger.info("[Weekly Job] Starting open problems synthesis")
    async with AsyncSessionLocal() as db:
        await synthesize_clusters(db)
        await db.commit()
    logger.info("[Weekly Job] Done.")


def start_scheduler():
    if not scheduler.running:
        scheduler.start()
        logger.info("Scheduler started. Daily fetch at 02:00 UTC.")


def shutdown_scheduler():
    if scheduler.running:
        scheduler.shutdown(wait=False)
