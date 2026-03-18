"""Tests for module1_upload."""

import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path

from src.module1_upload.uploader import upload_all_files, LOCAL_PATH


@patch("src.module1_upload.uploader.upload_directory_to_s3")
def test_upload_all_files(mock_upload):
    """Test upload_all_files calls upload_directory_to_s3 with correct args."""
    mock_upload.return_value = 5
    result = upload_all_files()
    assert result == 5
    mock_upload.assert_called_once_with(
        local_dir=str(LOCAL_PATH),
        s3_prefix="",
        bucket="cosmo-gsom-check-data",
        cred_path=None,
    )


@patch("src.module1_upload.uploader.upload_directory_to_s3")
def test_upload_all_files_custom(mock_upload):
    """Test with custom parameters."""
    custom_path = Path("/tmp/test")
    mock_upload.return_value = 3
    result = upload_all_files(local_path=custom_path, bucket="test-bucket")
    assert result == 3
    mock_upload.assert_called_once_with(
        local_dir=str(custom_path),
        s3_prefix="",
        bucket="test-bucket",
        cred_path=None,
    )


def test_local_path_exists():
    """Ensure LOCAL_PATH is defined."""
    assert LOCAL_PATH is not None
    # Not checking actual existence because it may not exist on test environment
