"""
Uploads extracted figures to Cloudflare R2 (S3-compatible) or any S3 bucket.
"""
import io
import logging
import os
import uuid
from typing import Any

logger = logging.getLogger(__name__)


def _get_s3_client():
    import boto3
    return boto3.client(
        "s3",
        endpoint_url=f"https://{os.environ['R2_ACCOUNT_ID']}.r2.cloudflarestorage.com",
        aws_access_key_id=os.environ["R2_ACCESS_KEY_ID"],
        aws_secret_access_key=os.environ["R2_SECRET_ACCESS_KEY"],
        region_name="auto",
    )


async def upload_figure(
    image_bytes: bytes,
    paper_arxiv_id: str,
    figure_index: int,
    description: str = "",
) -> dict[str, Any] | None:
    """
    Upload a figure PNG to object storage.
    Returns dict with url and description, or None if storage not configured.
    """
    if not os.environ.get("R2_ACCOUNT_ID"):
        # Storage not configured — save locally for dev
        return _save_figure_local(image_bytes, paper_arxiv_id, figure_index, description)

    bucket = os.environ["R2_BUCKET_NAME"]
    public_url_base = os.environ.get("R2_PUBLIC_URL", "")

    safe_id = paper_arxiv_id.replace("/", "_")
    key = f"figures/{safe_id}/fig_{figure_index:02d}.png"

    try:
        s3 = _get_s3_client()
        s3.put_object(
            Bucket=bucket,
            Key=key,
            Body=image_bytes,
            ContentType="image/png",
            CacheControl="public, max-age=31536000",
        )
        public_url = f"{public_url_base.rstrip('/')}/{key}"
        return {"url": public_url, "description": description, "index": figure_index}
    except Exception as e:
        logger.error(f"Figure upload failed: {e}")
        return None


def _save_figure_local(
    image_bytes: bytes,
    paper_arxiv_id: str,
    figure_index: int,
    description: str,
) -> dict[str, Any]:
    """Development fallback: save figure to local static directory."""
    from pathlib import Path
    static_dir = Path("static/figures")
    static_dir.mkdir(parents=True, exist_ok=True)

    safe_id = paper_arxiv_id.replace("/", "_")
    filename = f"{safe_id}_fig_{figure_index:02d}.png"
    dest = static_dir / filename

    dest.write_bytes(image_bytes)
    return {
        "url": f"/static/figures/{filename}",
        "description": description,
        "index": figure_index,
    }
