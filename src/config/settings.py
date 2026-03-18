"""Project settings and configuration."""

import json
from pathlib import Path

# Project root
PROJECT_ROOT = Path(__file__).parent.parent.parent

# Paths
DATA_DIR = PROJECT_ROOT / "data"
LOGS_DIR = PROJECT_ROOT / "logs"
CACHE_DIR = PROJECT_ROOT / "cache"
RAWOCR_DIR = CACHE_DIR / "raw_ocr"
IMGS_CACHE_DIR = CACHE_DIR / "images"

# Ensure directories exist
for d in [DATA_DIR, LOGS_DIR, CACHE_DIR, RAWOCR_DIR, IMGS_CACHE_DIR]:
    d.mkdir(parents=True, exist_ok=True)

# Credentials
CREDENTIALS_PATH = DATA_DIR / "credentials.json"

# S3 buckets
S3_CHECK_BUCKET = "cosmo-gsom-check-data"
S3_RESULT_BUCKET = "cosmo-gsom-result-data"
CSV_KEY = "Grades-lab_spr_2026-Загрузить решение кейса--12791.csv"

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
LOCAL_UPLOAD_PATH = Path(
    "/home/vgarshin/yadisk/EDU/SpaceLab/" "lab_spr_2026-Загрузить решение кейса-12791"
)

# Logging
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
