"""Yandex OCR client."""

import base64
import json
import logging
import time
from pathlib import Path
from typing import Optional

import requests

from .s3_client import load_credentials
from ..config.settings import OCR_MODEL, OCR_API_URL, OCR_SLEEP

logger = logging.getLogger(__name__)


def encode_file(image_path: str) -> str:
    """Encode image file to base64."""
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


def ocr_json(data: dict, output_path: str):
    """Save raw OCR JSON to file."""
    with open(output_path, "w") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def recognize_text(
    image_path: str,
    cred_path: Optional[str] = None,
    folder_id: Optional[str] = None,
    ocr_api_key: Optional[str] = None,
) -> str:
    """
    Send image to Yandex OCR and return extracted text.

    Args:
        image_path: Path to image file.
        cred_path: Path to credentials JSON.
        folder_id: Yandex Cloud folder ID.
        ocr_api_key: API key for OCR.

    Returns:
        Extracted text.
    """
    if cred_path is None:
        creds = load_credentials()
        folder_id = creds["yandex"]["folder_id"]
        ocr_api_key = creds["yandex"]["ocr_api_key"]
    else:
        creds = load_credentials(cred_path)
        if folder_id is None:
            folder_id = creds["yandex"]["folder_id"]
        if ocr_api_key is None:
            ocr_api_key = creds["yandex"]["ocr_api_key"]

    content = encode_file(image_path)
    data = {
        "mimeType": "JPEG",
        "languageCodes": ["*"],
        "model": OCR_MODEL,
        "content": content,
    }
    url = OCR_API_URL
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Api-Key {ocr_api_key}",
        "x-folder-id": folder_id,
        "x-data-logging-enabled": "true",
    }

    while True:
        try:
            r = requests.post(url=url, headers=headers, data=json.dumps(data))
            if r.status_code == 200:
                return r.json()["result"]["textAnnotation"]["fullText"]
            else:
                logger.error(f"OCR error: {r.status_code} -> {r.text}")
                time.sleep(OCR_SLEEP)
        except Exception as e:
            logger.error(f"Request failed: {e}")
            time.sleep(OCR_SLEEP)


def process_pdf(
    pdf_path: str,
    output_dir: str,
    cred_path: Optional[str] = None,
    dpi: int = 200,
) -> str:
    """
    Convert PDF to images, run OCR, and combine text.

    Args:
        pdf_path: Path to PDF file.
        output_dir: Directory to store raw OCR JSONs.
        cred_path: Path to credentials.
        dpi: DPI for PDF conversion.

    Returns:
        Combined text from all pages.
    """
    try:
        import pdf2image
    except ImportError:
        logger.error("pdf2image not installed. Install via 'pip install pdf2image'.")
        raise

    # Ensure output directory exists
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    # Convert PDF to images
    logger.info(f"Converting PDF {pdf_path} to images...")
    images = pdf2image.convert_from_path(
        pdf_path=pdf_path,
        dpi=dpi,
        output_folder=None,  # we'll handle saving manually
        first_page=None,
        last_page=None,
        fmt="JPEG",
    )

    combined_text = ""
    for i, image in enumerate(images):
        # Save temporary image
        temp_image_path = Path(output_dir) / f"page_{i+1}.jpg"
        image.save(str(temp_image_path), "JPEG")

        # OCR
        logger.info(f"OCR page {i+1}...")
        text = recognize_text(str(temp_image_path), cred_path)
        combined_text += " " + text

        # Save raw OCR JSON (optional)
        # For simplicity, we skip saving raw JSON here; can be added later.

        # Clean up temp image
        temp_image_path.unlink()

        # Rate limiting: wait between pages to avoid 429
        time.sleep(OCR_SLEEP)

    logger.info(f"OCR completed for {pdf_path}")
    return combined_text.strip()
