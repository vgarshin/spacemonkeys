"""Upload result files to S3 preserving directory structure."""

import logging
import os
from typing import Dict, Optional

from .s3_client import upload_file_to_s3
from ..config.settings import S3_RESULT_BUCKET

logger = logging.getLogger(__name__)


def upload_result_files(
    results: Dict[str, Dict[str, str]],
    bucket: Optional[str] = None,
    cred_path: Optional[str] = None,
) -> int:
    """
    Upload OCR, detection, and grading results as separate text files.

    Args:
        results: Dict mapping PDF key to dict with keys:
            - 'ocr_text' (optional)
            - 'detection' (optional)
            - 'grading' (optional)
        bucket: Destination bucket (default S3_RESULT_BUCKET).
        cred_path: Path to credentials.

    Returns:
        Number of files uploaded successfully.
    """
    if bucket is None:
        bucket = S3_RESULT_BUCKET

    uploaded = 0
    for pdf_key, result_dict in results.items():
        # Determine base path in output bucket: same directory as PDF key but without .pdf extension
        # e.g., "group/participant/file.pdf" -> "group/participant/file/"
        dir_path = os.path.dirname(pdf_key)
        base_name = os.path.splitext(os.path.basename(pdf_key))[0]
        if dir_path:
            prefix = f"{dir_path}"  # use `/` for subdirectory save
        else:
            prefix = ""

        # Upload OCR text
        if "ocr_text" in result_dict:
            ocr_key = f"{prefix}/{base_name}_ocr_result.txt"
            success = _upload_text(result_dict["ocr_text"], ocr_key, bucket, cred_path)
            if success:
                uploaded += 1

        # Upload detection result
        if "detection" in result_dict:
            det_key = f"{prefix}/{base_name}_detection_result.txt"
            success = _upload_text(result_dict["detection"], det_key, bucket, cred_path)
            if success:
                uploaded += 1

        # Upload grading result
        if "grading" in result_dict:
            grad_key = f"{prefix}/{base_name}_grading_result.txt"
            success = _upload_text(result_dict["grading"], grad_key, bucket, cred_path)
            if success:
                uploaded += 1

    logger.info(f"Uploaded {uploaded} result files to bucket {bucket}")
    return uploaded


def _upload_text(
    text: str,
    s3_key: str,
    bucket: str,
    cred_path: Optional[str] = None,
) -> bool:
    """Upload text content to S3 as a file."""
    import tempfile
    import os

    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
        f.write(text)
        tmp_path = f.name
    try:
        success = upload_file_to_s3(
            local_path=tmp_path,
            s3_key=s3_key,
            bucket=bucket,
            cred_path=cred_path,
        )
        return success
    finally:
        os.unlink(tmp_path)


if __name__ == "__main__":
    # Test with dummy data
    logging.basicConfig(level=logging.INFO)
    dummy_results = {
        "group1/participant1/file.pdf": {
            "ocr_text": "This is OCR text.",
            "detection": "Detection result.",
            "grading": "Итого: 50 из 60.",
        }
    }
    count = upload_result_files(dummy_results)
    print(f"Uploaded {count} files")
