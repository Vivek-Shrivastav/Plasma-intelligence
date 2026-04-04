"""
Fetches new papers from arXiv API and NASA ADS API.
"""
import asyncio
import logging
import os
from datetime import date, timedelta
from typing import Any

import httpx
import xmltodict

logger = logging.getLogger(__name__)

ARXIV_CATEGORIES = [
    "physics.plasm-ph",
    "astro-ph.SR",
    "astro-ph.HE",
    "physics.space-ph",
    "nucl-th",
]

ADS_JOURNALS = [
    "The Astrophysical Journal",
    "The Astrophysical Journal Letters",
    "Journal of Geophysical Research Space Physics",
    "Geophysical Research Letters",
    "Monthly Notices of the Royal Astronomical Society",
    "Astronomy and Astrophysics",
    "Solar Physics",
    "Physics of Plasmas",
    "Journal of Plasma Physics",
    "Nuclear Fusion",
    "Physical Review Letters",
    "Physical Review E",
    "Plasma Physics and Controlled Fusion",
    "Advances in Space Research",
]

PLASMA_KEYWORDS = [
    "plasma", "tokamak", "stellarator", "fusion", "magnetic reconnection",
    "magnetohydrodynamic", "MHD", "kinetic", "instability", "turbulence",
    "solar wind", "magnetosphere", "accretion disk", "shock", "alfven",
    "two-stream", "drift wave", "confinement", "heating", "transport",
]


def _is_plasma_relevant(title: str, abstract: str) -> bool:
    """Quick keyword filter to avoid analyzing unrelated papers."""
    combined = (title + " " + abstract).lower()
    return any(kw.lower() in combined for kw in PLASMA_KEYWORDS)


async def fetch_arxiv(target_date: date | None = None) -> list[dict[str, Any]]:
    """Fetch papers from arXiv for a given date (defaults to yesterday)."""
    if target_date is None:
        target_date = date.today() - timedelta(days=1)
    date_str = target_date.strftime("%Y%m%d")

    papers: list[dict] = []

    async with httpx.AsyncClient(timeout=60) as client:
        for category in ARXIV_CATEGORIES:
            query = (
                f"cat:{category}+AND+submittedDate:[{date_str}0000+TO+{date_str}2359]"
            )
            url = (
                f"http://export.arxiv.org/api/query"
                f"?search_query={query}&start=0&max_results=100"
                f"&sortBy=submittedDate&sortOrder=descending"
            )
            try:
                r = await client.get(url)
                r.raise_for_status()
                data = xmltodict.parse(r.text)
                entries = data.get("feed", {}).get("entry", [])
                if isinstance(entries, dict):
                    entries = [entries]  # single result

                for entry in entries:
                    arxiv_id = entry.get("id", "").split("/abs/")[-1]
                    title = entry.get("title", "").replace("\n", " ").strip()
                    abstract = entry.get("summary", "").replace("\n", " ").strip()

                    if not _is_plasma_relevant(title, abstract):
                        continue

                    authors_raw = entry.get("author", [])
                    if isinstance(authors_raw, dict):
                        authors_raw = [authors_raw]
                    authors = [a.get("name", "") for a in authors_raw]

                    links = entry.get("link", [])
                    if isinstance(links, dict):
                        links = [links]
                    pdf_url = next(
                        (l["@href"] for l in links if l.get("@title") == "pdf"), None
                    )

                    papers.append({
                        "arxiv_id": arxiv_id,
                        "title": title,
                        "authors": authors,
                        "abstract": abstract,
                        "journal": "arXiv",
                        "published_date": target_date,
                        "pdf_url": pdf_url or f"https://arxiv.org/pdf/{arxiv_id}",
                        "paper_url": f"https://arxiv.org/abs/{arxiv_id}",
                        "source": "arxiv",
                    })

            except Exception as e:
                logger.error(f"arXiv fetch failed for {category}: {e}")

            await asyncio.sleep(0.5)  # be polite

    logger.info(f"arXiv: fetched {len(papers)} plasma-relevant papers for {date_str}")
    return papers


async def fetch_nasa_ads(target_date: date | None = None) -> list[dict[str, Any]]:
    """Fetch papers from NASA ADS for a given date."""
    token = os.environ.get("NASA_ADS_TOKEN")
    if not token:
        logger.warning("NASA_ADS_TOKEN not set — skipping NASA ADS fetch")
        return []

    if target_date is None:
        target_date = date.today() - timedelta(days=1)
    date_str = target_date.strftime("%Y-%m-%d")

    papers: list[dict] = []
    headers = {"Authorization": f"Bearer {token}"}

    async with httpx.AsyncClient(timeout=60) as client:
        for journal in ADS_JOURNALS:
            query = f'pub:"{journal}" pubdate:[{date_str} TO {date_str}]'
            params = {
                "q": query,
                "fl": "title,author,abstract,identifier,pubdate,doi,bibcode,pub",
                "rows": 50,
                "sort": "date desc",
            }
            try:
                r = await client.get(
                    "https://api.adsabs.harvard.edu/v1/search/query",
                    headers=headers,
                    params=params,
                )
                r.raise_for_status()
                docs = r.json().get("response", {}).get("docs", [])

                for doc in docs:
                    title = doc.get("title", [""])[0] if doc.get("title") else ""
                    abstract = doc.get("abstract", "")
                    if not abstract or not _is_plasma_relevant(title, abstract):
                        continue

                    doi = None
                    for ident in doc.get("identifier", []):
                        if ident.startswith("10."):
                            doi = ident
                            break

                    bibcode = doc.get("bibcode", "")
                    papers.append({
                        "arxiv_id": None,
                        "doi": doi,
                        "title": title,
                        "authors": doc.get("author", []),
                        "abstract": abstract,
                        "journal": doc.get("pub", journal),
                        "published_date": target_date,
                        "pdf_url": f"https://ui.adsabs.harvard.edu/link_gateway/{bibcode}/ESOURCE" if bibcode else None,
                        "paper_url": f"https://ui.adsabs.harvard.edu/abs/{bibcode}" if bibcode else None,
                        "source": "ads",
                    })

            except Exception as e:
                logger.error(f"NASA ADS fetch failed for {journal}: {e}")

            await asyncio.sleep(0.3)

    logger.info(f"NASA ADS: fetched {len(papers)} papers for {date_str}")
    return papers


async def fetch_all(target_date: date | None = None) -> list[dict[str, Any]]:
    """Fetch from all sources and deduplicate."""
    arxiv_papers, ads_papers = await asyncio.gather(
        fetch_arxiv(target_date),
        fetch_nasa_ads(target_date),
    )

    # Deduplicate by title similarity (simple exact-title dedup)
    seen_titles: set[str] = set()
    all_papers: list[dict] = []

    for paper in arxiv_papers + ads_papers:
        title_key = paper["title"].lower().strip()[:80]
        if title_key not in seen_titles:
            seen_titles.add(title_key)
            all_papers.append(paper)

    logger.info(f"Total unique papers to process: {len(all_papers)}")
    return all_papers
