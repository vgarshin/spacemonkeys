#!/usr/bin/env python3
"""
Pipeline runner: executes all modules in sequence.
"""

import logging
import sys
from pathlib import Path

# Add parent directory to path to treat src as a package
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.utils.logging_config import setup_logging
from src.module1_upload.uploader import upload_all_files
from src.module2_ocr.pdf_ocr import process_all_pdfs
from src.module3_ai_detect.ai_detector import batch_detect
from src.module4_ai_grade.ai_grader import batch_grade, save_to_s3


def main():
    """Run the full pipeline."""
    setup_logging(log_level=logging.INFO)
    logger = logging.getLogger(__name__)

    logger.info("Starting PDF AI Pipeline")

    # Step 1: Upload files to S3
    logger.info("=== MODULE 1: Upload files to S3 ===")
    uploaded = upload_all_files()
    if uploaded == 0:
        logger.warning("No files uploaded. Check local path.")

    # Step 2: Process PDFs with OCR
    logger.info("=== MODULE 2: OCR PDFs ===")
    ocr_results = process_all_pdfs()
    if not ocr_results:
        logger.error("No OCR results. Exiting.")
        sys.exit(1)

    # Step 3: AI detection
    logger.info("=== MODULE 3: AI-generated text detection ===")
    detection_results = batch_detect(ocr_results)

    # Step 4: Quality grading
    logger.info("=== MODULE 4: Quality grading ===")
    grading_results = batch_grade(ocr_results)

    # Combine results
    combined = {
        "ocr_texts": ocr_results,
        "detection": detection_results,
        "grading": grading_results,
    }

    # Save to S3
    logger.info("Saving results to S3...")
    success = save_to_s3(
        combined,
        s3_key="pipeline_results.json",
        bucket="cosmo-gsom-result-data",
    )
    if success:
        logger.info("Pipeline completed successfully.")
    else:
        logger.error("Failed to save results to S3.")
        sys.exit(1)


if __name__ == "__main__":
    main()
