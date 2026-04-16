"""
Gemini API client — drop-in replacement for the Anthropic client.
All AI calls in the project must go through this module.

Free tier limits (Gemini 2.0 Flash):
  - 15 requests per minute
  - 1,000,000 tokens per minute  
  - 1,500 requests per day

Rate limit strategy:
  - Hard sleep of 4 seconds between every call (15 RPM safe)
  - Exponential backoff via tenacity on 429 errors
  - Batch processing with 60s sleep between batches of 10
"""

import os, time, logging
from tenacity import retry, wait_exponential, stop_after_attempt, retry_if_exception_type
import google.generativeai as genai
from google.api_core.exceptions import ResourceExhausted

logger = logging.getLogger(__name__)

genai.configure(api_key=os.environ["GEMINI_API_KEY"])

FLASH_MODEL   = "gemini-2.0-flash"
EMBED_MODEL   = "models/text-embedding-004"
INTER_CALL_SLEEP = 4.1   # seconds between calls to stay under 15 RPM

# ── Retry decorator for rate limit errors ──────────────────────────
gemini_retry = retry(
    retry=retry_if_exception_type(ResourceExhausted),
    wait=wait_exponential(multiplier=2, min=60, max=600), # wait up to 10 mins
    stop=stop_after_attempt(10), # try 10 times
    before_sleep=lambda rs: logger.warning(
        f"Rate limited (ResourceExhausted). Waiting {rs.next_action.sleep:.0f}s...")
)

@gemini_retry
def analyze_paper(title: str, abstract: str, full_text: str = "") -> dict:
    """
    Analyzes a plasma physics paper. Returns structured dict with:
    headline, summary, key_findings, methodology, significance, 
    open_questions, subfield_tags
    """
    time.sleep(INTER_CALL_SLEEP)
    model = genai.GenerativeModel(FLASH_MODEL)
    prompt = f"""You are an expert plasma physics researcher. 
Analyze this paper and return a JSON object with these exact keys:
{{
  "headline": "one punchy newspaper headline (max 12 words)",
  "short_summary": "2-3 sentence plain-language summary for a physics audience",
  "field": "The general field (e.g., Plasma Physics, Astrophysics, Fusion Energy)",
  "subfield": ["specific subfield 1", "specific subfield 2"],
  "importance_score": 1-100 (integer score of how groundbreaking this is),
  "technical_depth": "one word: low, medium, or high",
  "keywords": ["key concept 1", "key concept 2", "key concept 3"],
  "concepts_detected": ["List 3-5 specific physics concepts mentioned"],
  "methodology": "one sentence describing the method used",
  "significance": "one sentence on why this matters to the field"
}}

Only return valid JSON. No markdown, no backticks, no extra text.

Title: {title}
Abstract: {abstract}
{f"Full text excerpt: {full_text[:3000]}" if full_text else ""}
"""
    resp = model.generate_content(prompt)
    import json
    try:
        return json.loads(resp.text.strip())
    except json.JSONDecodeError:
        # Attempt to extract JSON if model added surrounding text
        import re
        match = re.search(r'\{.*\}', resp.text, re.DOTALL)
        if match:
            return json.loads(match.group())
        raise ValueError(f"Could not parse Gemini response as JSON: {resp.text[:200]}")

@gemini_retry
def describe_figure(image_bytes: bytes, paper_title: str) -> str:
    """Describes a figure extracted from a plasma physics paper."""
    time.sleep(INTER_CALL_SLEEP)
    import PIL.Image, io
    model = genai.GenerativeModel(FLASH_MODEL)
    image = PIL.Image.open(io.BytesIO(image_bytes))
    resp = model.generate_content([
        image,
        f"This figure is from a plasma physics paper titled: '{paper_title}'. "
        f"Describe what this figure shows in 2-3 sentences. "
        f"Focus on the physics being demonstrated. Be specific."
    ])
    return resp.text.strip()

@gemini_retry  
def extract_open_problems(title: str, abstract: str, analysis: dict) -> list[str]:
    """Extracts open research questions from a paper."""
    time.sleep(INTER_CALL_SLEEP)
    model = genai.GenerativeModel(FLASH_MODEL)
    prompt = f"""Extract open research questions and unsolved problems 
mentioned or implied in this plasma physics paper.
Return a JSON array of strings only. No markdown, no extra text.
Maximum 5 questions.

Title: {title}
Abstract: {abstract}
Key findings: {analysis.get('key_findings', [])}
"""
    resp = model.generate_content(prompt)
    import json, re
    try:
        text = resp.text.strip()
        match = re.search(r'\[.*\]', text, re.DOTALL)
        return json.loads(match.group() if match else text)
    except Exception:
        return []

@gemini_retry
def generate_literature_review_patch(subfield: str, new_papers: list[dict], existing_review: str) -> str:
    """
    Appends new findings to an existing literature review.
    Returns only the new paragraph(s) to append — not the full review.
    """
    time.sleep(INTER_CALL_SLEEP)
    model = genai.GenerativeModel(FLASH_MODEL)
    papers_text = "\n".join([
        f"- {p['title']}: {p.get('summary','')}" 
        for p in new_papers[:10]
    ])
    prompt = f"""You are writing a living literature review for the 
plasma physics subfield: {subfield}.

Here are new papers published recently:
{papers_text}

The existing review ends with:
...{existing_review[-500:] if existing_review else "(new review)"}

Write 1-2 new paragraphs continuing the review to incorporate 
these new papers. Write in academic style. 
Do not repeat what is already in the review. 
Do not include headings or titles — just the paragraphs.
"""
    resp = model.generate_content(prompt)
    return resp.text.strip()

@gemini_retry
def seed_literature_review(subfield: str, founding_papers: list[dict]) -> str:
    """
    Generates the full historical backbone of a literature review.
    Called once per subfield during initial seeding.
    Uses multiple calls to stay within token limits.
    """
    time.sleep(INTER_CALL_SLEEP)
    model = genai.GenerativeModel(FLASH_MODEL)
    papers_text = "\n".join([
        f"- ({p.get('year','?')}) {p['title']}: {p.get('abstract','')[:200]}"
        for p in founding_papers[:20]
    ])
    prompt = f"""Write a comprehensive literature review introduction for 
the plasma physics subfield: {subfield}.

Cover the historical development and key milestones using these papers:
{papers_text}

Write 3-4 substantial paragraphs in academic style.
Start from the earliest foundational work and progress chronologically.
Explain how the field evolved and what the major breakthroughs were.
"""
    resp = model.generate_content(prompt)
    return resp.text.strip()

def get_embedding(text: str) -> list[float]:
    """Gets text embedding for semantic search. No rate limit sleep 
    needed as embedding calls use a separate quota."""
    result = genai.embed_content(
        model=EMBED_MODEL,
        content=text[:2000],  # truncate to stay within token limits
        task_type="retrieval_document"
    )
    return result['embedding']

def analyze_papers_batch(papers: list[dict]) -> list[dict]:
    """
    Processes a batch of papers with proper rate limiting.
    Splits into sub-batches of 10 with 60s sleep between batches.
    Returns list of papers with analysis added.
    """
    results = []
    batch_size = 5 # Reduced from 10 to be even safer
    for i in range(0, len(papers), batch_size):
        batch = papers[i:i+batch_size]
        logger.info(f"Processing batch {i//batch_size + 1} of "
                   f"{(len(papers)+batch_size-1)//batch_size} "
                   f"({len(batch)} papers)")
        for paper in batch:
            try:
                analysis = analyze_paper(
                    paper['title'], 
                    paper.get('abstract',''),
                    paper.get('full_text','')
                )
                paper['analysis'] = analysis
                paper['headline'] = analysis.get('headline','')
                paper['summary'] = analysis.get('summary','')
                results.append(paper)
            except Exception as e:
                logger.error(f"Failed to analyze {paper['title']}: {e}")
                paper['analysis'] = {}
                results.append(paper)
        if i + batch_size < len(papers):
            logger.info("Batch complete. Sleeping 60s for rate limit...")
            time.sleep(60)
    return results
