"""S3 client for Yandex Object Storage."""

import os
import json
import logging
from pathlib import Path
from typing import Optional

import boto3
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)


def load_credentials(cred_path: Optional[str] = None) -> dict:
    """Load credentials from JSON file."""
    if cred_path is None:
        cred_path = Path(__file__).parent.parent.parent / "data" / "credentials.json"
    with open(cred_path, "r") as f:
        return json.load(f)


def get_s3_client(cred_path: Optional[str] = None):
    """Create and return an S3 client configured for Yandex Cloud."""
    creds = load_credentials(cred_path)
    s3_config = creds["s3"]
    session = boto3.session.Session()
    return session.client(
        service_name="s3",
        endpoint_url=s3_config["endpoint"],
        aws_access_key_id=s3_config["access_key_id"],
        aws_secret_access_key=s3_config["secret_access_key"],
    )


def upload_file_to_s3(
    local_path: str,
    s3_key: str,
    bucket: Optional[str] = None,
    cred_path: Optional[str] = None,
) -> bool:
    """
    Upload a file to Yandex Object Storage preserving directory structure.

    Args:
        local_path: Path to local file.
        s3_key: Key (path) in S3 bucket.
        bucket: Bucket name, defaults to credentials bucket.
        cred_path: Path to credentials JSON.

    Returns:
        True if successful, False otherwise.
    """
    try:
        client = get_s3_client(cred_path)
        if bucket is None:
            bucket = load_credentials(cred_path)["s3"]["bucket"]
        client.upload_file(local_path, bucket, s3_key)
        logger.info(f"Uploaded {local_path} to s3://{bucket}/{s3_key}")
        return True
    except ClientError as e:
        logger.error(f"Failed to upload {local_path}: {e}")
        return False


def download_file_from_s3(
    s3_key: str,
    local_path: str,
    bucket: Optional[str] = None,
    cred_path: Optional[str] = None,
) -> bool:
    """
    Download a file from S3 to local path.

    Args:
        s3_key: Key (path) in S3 bucket.
        local_path: Local file path to save to.
        bucket: Bucket name, defaults to credentials bucket.
        cred_path: Path to credentials JSON.

    Returns:
        True if successful, False otherwise.
    """
    try:
        client = get_s3_client(cred_path)
        if bucket is None:
            bucket = load_credentials(cred_path)["s3"]["bucket"]
        client.download_file(bucket, s3_key, local_path)
        logger.info(f"Downloaded s3://{bucket}/{s3_key} to {local_path}")
        return True
    except ClientError as e:
        logger.error(f"Failed to download {s3_key}: {e}")
        return False


def upload_directory_to_s3(
    local_dir: str,
    s3_prefix: str = "",
    bucket: Optional[str] = None,
    cred_path: Optional[str] = None,
) -> int:
    """
    Upload entire directory recursively to S3.

    Args:
        local_dir: Local directory path.
        s3_prefix: Prefix to prepend to S3 keys.
        bucket: Bucket name.
        cred_path: Path to credentials.

    Returns:
        Number of files uploaded successfully.
    """
    uploaded = 0
    for root, _, files in os.walk(local_dir):
        for file in files:
            local_path = os.path.join(root, file)
            rel_path = os.path.relpath(local_path, local_dir)
            s3_key = os.path.join(s3_prefix, rel_path).replace("\\", "/")
            if upload_file_to_s3(local_path, s3_key, bucket, cred_path):
                uploaded += 1
    logger.info(f"Uploaded {uploaded} files from {local_dir}")
    return uploaded
