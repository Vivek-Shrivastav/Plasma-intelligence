"""
Fetches new papers from arXiv API and Semantic Scholar API.
"""
import asyncio
import logging

from datetime import date, timedelta
from typing import Any

import httpx
import xmltodict
from tenacity import retry, wait_exponential, stop_after_attempt, retry_if_exception_type

logger = logging.getLogger(__name__)

ARXIV_CATEGORIES = [
    "physics.plasm-ph",
    "astro-ph.SR",
    "astro-ph.HE",
    "physics.space-ph",
    "nucl-th",
]



PLASMA_KEYWORDS = [
    "plasma", "tokamak", "stellarator", "fusion", "magnetic reconnection",
    "magnetohydrodynamic", "MHD", "kinetic", "instability", "turbulence",
    "solar wind", "magnetosphere", "accretion disk", "shock", "alfven",
    "two-stream", "drift wave", "confinement", "heating", "transport",
    "coronal", "corona", "ionosphere", "space weather", "astrophysical",
    "ITER", "tokamaks", "magnetized", "sheath", "glow discharge",
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
                f"https://export.arxiv.org/api/query"
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


@retry(
    retry=retry_if_exception_type(httpx.HTTPStatusError),
    wait=wait_exponential(multiplier=2, min=60, max=600),
    stop=stop_after_attempt(3), # Reduced to 3 attempts to avoid long hangs
    before_sleep=lambda rs: logger.warning(f"Semantic Scholar rate limited (429). Waiting {rs.next_action.sleep:.0f}s...")
)
async def _fetch_ss_batch(client: httpx.AsyncClient, url: str, params: dict) -> dict:
    try:
        r = await client.get(url, params=params)
        r.raise_for_status()
        return r.json()
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 429:
            raise # Let retry handle it
        logger.error(f"SS Batch failed: {e}")
        return {"data": []}
    except Exception as e:
        logger.error(f"SS Batch failed: {e}")
        return {"data": []}


async def fetch_semantic_scholar(target_date: date | None = None) -> list[dict[str, Any]]:
    """Fetch papers from Semantic Scholar for plasma physics."""
    from tenacity import retry, wait_exponential, stop_after_attempt, retry_if_exception_type
    if target_date is None:
        target_date = date.today() - timedelta(days=1)
    
    papers: list[dict] = []
    
    async with httpx.AsyncClient(timeout=60) as client:
        url = "https://api.semanticscholar.org/graph/v1/paper/search"
        params = {
            "query": "plasma physics tokamak",
            "fields": "paperId,title,abstract,year,authors,publicationDate,externalIds,openAccessPdf",
            "limit": 100,
            "offset": 0
        }
        try:
            # Using the retrying helper
            from tenacity import RetryError
            try:
                data = await _fetch_ss_batch(client, url, params)
            except RetryError:
                logger.error("Semantic Scholar failed after multiple retries. Skipping.")
                data = {"data": []}
            
            docs = data.get("data", [])

            for doc in docs:
                title = doc.get("title", "")
                abstract = doc.get("abstract", "")
                if not abstract or not _is_plasma_relevant(title, abstract):
                    continue

                pub_date_str = doc.get("publicationDate")
                if pub_date_str:
                    try:
                        pub_date = date.fromisoformat(pub_date_str)
                        if pub_date < target_date - timedelta(days=7):
                            continue # Skip very old papers
                    except Exception:
                        pass

                authors = [a.get("name", "") for a in doc.get("authors", [])]
                paperId = doc.get("paperId", "")
                
                pdf_url = None
                open_access = doc.get("openAccessPdf")
                if open_access and isinstance(open_access, dict):
                    pdf_url = open_access.get("url")
                
                doi = doc.get("externalIds", {}).get("DOI")

                papers.append({
                    "arxiv_id": None,
                    "doi": doi,
                    "title": title,
                    "authors": authors,
                    "abstract": abstract,
                    "journal": "Semantic Scholar",
                    "published_date": target_date,
                    "pdf_url": pdf_url,
                    "paper_url": f"https://www.semanticscholar.org/paper/{paperId}" if paperId else None,
                    "source": "semanticscholar",
                })

        except Exception as e:
            logger.error(f"Semantic Scholar fetch failed: {e}")

        await asyncio.sleep(0.3)

    logger.info(f"Semantic Scholar: fetched {len(papers)} papers")
    return papers


async def fetch_all(target_date: date | None = None) -> list[dict[str, Any]]:
    """Fetch from all sources and deduplicate."""
    arxiv_papers, ss_papers = await asyncio.gather(
        fetch_arxiv(target_date),
        fetch_semantic_scholar(target_date),
    )

    # Deduplicate by title similarity (simple exact-title dedup)
    seen_titles: set[str] = set()
    all_papers: list[dict] = []

    for paper in arxiv_papers + ss_papers:
        title_key = paper["title"].lower().strip()[:80]
        if title_key not in seen_titles:
            seen_titles.add(title_key)
            all_papers.append(paper)

    logger.info(f"Total unique papers to process: {len(all_papers)}")
    return all_papers
