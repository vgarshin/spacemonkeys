"""Module 1: Upload files from local path to Yandex Object Storage."""

import logging
from pathlib import Path
from typing import Optional

from ..config.settings import LOCAL_UPLOAD_PATH, S3_CHECK_BUCKET
from ..utils.s3_client import upload_directory_to_s3

logger = logging.getLogger(__name__)


def upload_all_files(
    local_path: Optional[Path] = None,
    bucket: Optional[str] = None,
    cred_path: Optional[str] = None,
) -> int:
    """
    Upload all files from local directory to S3 bucket preserving structure.

    Args:
        local_path: Local directory path (defaults to LOCAL_UPLOAD_PATH).
        bucket: S3 bucket name (defaults to S3_CHECK_BUCKET).
        cred_path: Path to credentials JSON.

    Returns:
        Number of files uploaded.
    """
    if local_path is None:
        local_path = LOCAL_UPLOAD_PATH
    if bucket is None:
        bucket = S3_CHECK_BUCKET

    if not local_path.exists():
        logger.error(f"Local path {local_path} does not exist.")
        return 0

    logger.info(f"Starting upload from {local_path} to bucket {bucket}")
    uploaded = upload_directory_to_s3(
        local_dir=str(local_path),
        s3_prefix="",
        bucket=bucket,
        cred_path=cred_path,
    )
    logger.info(f"Upload completed. {uploaded} files uploaded.")
    return uploaded


if __name__ == "__main__":
    import sys

    logging.basicConfig(level=logging.INFO)
    uploaded = upload_all_files()
    sys.exit(0 if uploaded > 0 else 1)
