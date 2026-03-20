"""Project settings and configuration."""

import json
import logging
import tempfile
from pathlib import Path

# Project root
PROJECT_ROOT = Path(__file__).parent.parent.parent

# Paths
DATA_DIR = PROJECT_ROOT / "data"
LOGS_DIR = PROJECT_ROOT / "logs"
CACHE_DIR = PROJECT_ROOT / "cache"
RAWOCR_DIR = CACHE_DIR / "raw_ocr"
IMGS_CACHE_DIR = CACHE_DIR / "images"

# Ensure directories exist with fallback on permission error


def ensure_dir(path: Path) -> bool:
    """Try to create directory, return True if successful."""
    try:
        path.mkdir(parents=True, exist_ok=True)
        return True
    except PermissionError:
        logging.warning(f"Permission denied for directory {path}, " "using fallback.")
        return False
    except OSError as e:
        logging.warning(f"Failed to create directory {path}: {e}")
        return False


# Try to create cache directories
if not ensure_dir(CACHE_DIR):
    # Fallback to temporary directory
    CACHE_DIR = Path(tempfile.gettempdir()) / "pdf_ai_cache"
    RAWOCR_DIR = CACHE_DIR / "raw_ocr"
    IMGS_CACHE_DIR = CACHE_DIR / "images"
    logging.info(f"Using fallback cache directory: {CACHE_DIR}")

for d in [DATA_DIR, LOGS_DIR, CACHE_DIR, RAWOCR_DIR, IMGS_CACHE_DIR]:
    try:
        d.mkdir(parents=True, exist_ok=True)
    except PermissionError:
        # If still failing, ignore and hope for the best
        pass

# Credentials
CREDENTIALS_PATH = DATA_DIR / "credentials.json"

# S3 buckets
S3_CHECK_BUCKET = "cosmo-gsom-check-data"
S3_RESULT_BUCKET = "cosmo-gsom-result-data"

# Yandex Cloud
with open(CREDENTIALS_PATH, "r", encoding="utf-8") as f:
    creds = json.load(f)
    FOLDER_ID = creds["yandex"]["folder_id"]
OCR_MODEL = "page"
OCR_API_URL = "https://ocr.api.cloud.yandex.net/ocr/v1/recognizeText"
LLM_API_URL = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"

# Processing
PDF_DPI = 200
OCR_SLEEP = 1.1
LLM_SLEEP = 1

# Upload
LOCAL_UPLOAD_PATH = Path("/home/jovyan/app/upload")


def discover_csv_key(upload_path: Path = LOCAL_UPLOAD_PATH) -> str:
    """
    Discover CSV file in the S3 bucket (cosmo-gsom-check-data).
    Returns the first .csv key found, or the default CSV_KEY if none.
    The upload_path parameter is kept for backward compatibility but ignored.
    """
    from src.utils.s3_client import list_csv_keys

    csv_keys = list_csv_keys(bucket=S3_CHECK_BUCKET)
    if not csv_keys:
        raise RuntimeError(
            f"No CSV files found in bucket {S3_CHECK_BUCKET}. "
            "Please upload a CSV file to the bucket."
        )
    return csv_keys[0]


# Logging
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
