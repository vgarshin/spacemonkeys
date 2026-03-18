"""Module 2: Process PDFs from object storage with OCR."""

import logging
import tempfile
import os
from pathlib import Path
from typing import Optional

from ..config.settings import S3_CHECK_BUCKET, RAWOCR_DIR, IMGS_CACHE_DIR
from ..utils.s3_client import get_s3_client, load_credentials
from ..utils.ocr_client import process_pdf

logger = logging.getLogger(__name__)


def download_pdf_from_s3(
    s3_key: str,
    local_path: str,
    bucket: Optional[str] = None,
    cred_path: Optional[str] = None,
) -> bool:
    """Download a PDF file from S3 to local path."""
    try:
        client = get_s3_client(cred_path)
        if bucket is None:
            bucket = load_credentials(cred_path)["s3"]["bucket"]
        client.download_file(bucket, s3_key, local_path)
        logger.info(f"Downloaded s3://{bucket}/{s3_key} to {local_path}")
        return True
    except Exception as e:
        logger.error(f"Failed to download {s3_key}: {e}")
        return False


def list_pdf_keys(
    bucket: Optional[str] = None,
    cred_path: Optional[str] = None,
):
    """List all PDF keys in the bucket."""
    client = get_s3_client(cred_path)
    if bucket is None:
        bucket = load_credentials(cred_path)["s3"]["bucket"]
    paginator = client.get_paginator("list_objects_v2")
    pdf_keys = []
    for page in paginator.paginate(Bucket=bucket):
        for obj in page.get("Contents", []):
            key = obj["Key"]
            if key.lower().endswith(".pdf"):
                pdf_keys.append(key)
    return pdf_keys


def process_all_pdfs(
    bucket: Optional[str] = None,
    cred_path: Optional[str] = None,
    output_dir: Optional[str] = None,
) -> dict:
    """
    Download each PDF from S3, run OCR, and store text.

    Args:
        bucket: S3 bucket name.
        cred_path: Path to credentials.
        output_dir: Directory to store OCR results.

    Returns:
        Dict mapping PDF key to extracted text.
    """
    if bucket is None:
        bucket = S3_CHECK_BUCKET
    if output_dir is None:
        output_dir = str(RAWOCR_DIR)

    Path(output_dir).mkdir(parents=True, exist_ok=True)
    Path(IMGS_CACHE_DIR).mkdir(parents=True, exist_ok=True)

    pdf_keys = list_pdf_keys(bucket, cred_path)
    logger.info(f"Found {len(pdf_keys)} PDFs in bucket {bucket}")

    results = {}
    for key in pdf_keys:
        logger.info(f"Processing {key}...")
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
            tmp_path = tmp.name
        try:
            if not download_pdf_from_s3(key, tmp_path, bucket, cred_path):
                continue
            # Run OCR
            text = process_pdf(
                pdf_path=tmp_path,
                output_dir=os.path.join(output_dir, Path(key).stem),
                cred_path=cred_path,
            )
            results[key] = text
            # Save text to file
            text_path = Path(output_dir) / f"{Path(key).stem}.txt"
            text_path.write_text(text, encoding="utf-8")
            logger.info(f"Saved OCR text to {text_path}")
        except Exception as e:
            logger.error(f"Error processing {key}: {e}")
        finally:
            os.unlink(tmp_path)
            # Clean image cache
            for f in Path(IMGS_CACHE_DIR).glob("*.jpg"):
                f.unlink()

    return results


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    process_all_pdfs()
