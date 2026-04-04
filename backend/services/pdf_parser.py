"""
Downloads PDFs from arXiv and extracts figures using PyMuPDF.
"""
import logging
import os
import io
from pathlib import Path
from typing import Any

import httpx

logger = logging.getLogger(__name__)

TMP_DIR = Path("tmp")
TMP_DIR.mkdir(exist_ok=True)

MIN_FIGURE_WIDTH = 200
MIN_FIGURE_HEIGHT = 150
MIN_FIGURE_AREA = 40_000


async def download_pdf(pdf_url: str, arxiv_id: str) -> Path | None:
    """Download a PDF to the tmp directory. Returns path or None."""
    dest = TMP_DIR / f"{arxiv_id.replace('/', '_')}.pdf"
    if dest.exists():
        return dest
    try:
        async with httpx.AsyncClient(timeout=60, follow_redirects=True) as client:
            r = await client.get(pdf_url, headers={"User-Agent": "PlasmaIntelligence/1.0"})
            r.raise_for_status()
            dest.write_bytes(r.content)
        return dest
    except Exception as e:
        logger.warning(f"PDF download failed for {arxiv_id}: {e}")
        return None


def extract_figures_from_pdf(pdf_path: Path) -> list[dict[str, Any]]:
    """
    Extract figures from a PDF using PyMuPDF.
    Returns list of dicts with 'data' (PNG bytes), 'page', 'index'.
    """
    try:
        import fitz  # PyMuPDF
    except ImportError:
        logger.warning("PyMuPDF not installed — skipping figure extraction")
        return []

    figures = []
    try:
        doc = fitz.open(str(pdf_path))
        for page_num in range(len(doc)):
            page = doc[page_num]
            for img_index, img in enumerate(page.get_images(full=True)):
                xref = img[0]
                try:
                    base_image = doc.extract_image(xref)
                    w, h = base_image["width"], base_image["height"]

                    # Filter out tiny images (icons, logos, etc.)
                    if w < MIN_FIGURE_WIDTH or h < MIN_FIGURE_HEIGHT:
                        continue
                    if w * h < MIN_FIGURE_AREA:
                        continue
                    # Filter extreme aspect ratios (likely decorative bars)
                    aspect = max(w, h) / min(w, h)
                    if aspect > 8:
                        continue

                    # Convert to PNG bytes
                    from PIL import Image
                    img_data = base_image["image"]
                    img_ext = base_image["ext"]

                    if img_ext.lower() in ("png", "jpeg", "jpg"):
                        pil_img = Image.open(io.BytesIO(img_data))
                        png_buf = io.BytesIO()
                        pil_img.save(png_buf, format="PNG")
                        png_bytes = png_buf.getvalue()
                    else:
                        continue  # skip vector/other formats

                    figures.append({
                        "data": png_bytes,
                        "page": page_num + 1,
                        "index": img_index,
                        "width": w,
                        "height": h,
                    })

                except Exception:
                    continue

        doc.close()
    except Exception as e:
        logger.error(f"PDF parse error for {pdf_path}: {e}")

    # Limit to first 8 figures
    return figures[:8]


def cleanup_pdf(pdf_path: Path):
    """Remove a downloaded PDF from tmp."""
    try:
        pdf_path.unlink(missing_ok=True)
    except Exception:
        pass
