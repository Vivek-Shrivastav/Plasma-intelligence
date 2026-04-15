"""
Saves extracted figures to local filesystem.
"""
import logging
import os
from typing import Any
from pathlib import Path

logger = logging.getLogger(__name__)

async def upload_figure(
    image_bytes: bytes,
    paper_arxiv_id: str,
    figure_index: int,
    description: str = "",
) -> dict[str, Any] | None:
    """
    Save figure PNG to local storage.
    Returns dict with url and description.
    """
    safe_id = paper_arxiv_id.replace("/", "_")
    base_dir = Path(f"static/figures/{safe_id}")
    base_dir.mkdir(parents=True, exist_ok=True)

    filename = f"{figure_index}.png"
    dest = base_dir / filename

    try:
        dest.write_bytes(image_bytes)
        
        # Use NEXT_PUBLIC_API_URL from environment for the full URL
        api_url = os.environ.get("NEXT_PUBLIC_API_URL", "http://localhost:8000")
        public_url = f"{api_url}/static/figures/{safe_id}/{figure_index}.png"
        
        return {
            "url": public_url,
            "description": description,
            "index": figure_index,
        }
    except Exception as e:
        logger.error(f"Figure save failed: {e}")
        return None
