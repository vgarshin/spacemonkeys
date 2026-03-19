#!/usr/bin/env python3
"""
Pipeline runner: executes all modules in sequence and uploads results to S3.
Refactored to meet new requirements:
- Upload separate OCR, detection, grading files per PDF.
- Update CSV with grades and upload to result bucket.
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
from src.utils.result_uploader import upload_result_files
from src.utils.csv_updater import (
    download_csv,
    update_csv_rows,
    write_csv,
    upload_csv,
    extract_group_from_filename,
    group_mapping,
)
from src.config.settings import (
    S3_CHECK_BUCKET,
    S3_RESULT_BUCKET,
    discover_csv_key,
)


def map_pdf_key_to_identifier(pdf_key: str) -> str:
    """
    Map PDF S3 key to CSV group name by extracting first part before underscore.
    Example: "Дети солнца 2.0_4960_assignsubmission_file.pdf" -> "Дети солнца 2.0"
    """
    return extract_group_from_filename(pdf_key)


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

    # Combine results for per‑file upload
    per_file_results = {}
    for pdf_key in ocr_results:
        per_file_results[pdf_key] = {
            "ocr_text": ocr_results.get(pdf_key, ""),
            "detection": detection_results.get(pdf_key, ""),
            "grading": grading_results.get(pdf_key, ""),
        }

    # Upload separate result files
    logger.info("Uploading separate result files to S3...")
    files_uploaded = upload_result_files(per_file_results, bucket=S3_RESULT_BUCKET)
    logger.info(f"Uploaded {files_uploaded} result files.")

    # Update CSV with grades
    logger.info("Updating CSV with grades...")
    csv_key = discover_csv_key()
    rows = download_csv(csv_key, bucket=S3_CHECK_BUCKET)
    if rows is None:
        logger.error("Failed to download CSV, skipping CSV update.")
    else:
        # Build mapping from identifier to grading result
        grading_by_identifier = {}
        for pdf_key, result in per_file_results.items():
            identifier = map_pdf_key_to_identifier(pdf_key)
            grading_by_identifier[identifier] = result["grading"]

        # Use group mapping
        updated_rows = update_csv_rows(
            rows, grading_by_identifier, mapping_func=group_mapping
        )

        # Write updated CSV to temporary file
        import tempfile

        tmp_csv = tempfile.NamedTemporaryFile(suffix=".csv", delete=False).name
        if write_csv(updated_rows, tmp_csv, delimiter="\t"):
            # Upload to result bucket with same key
            if upload_csv(tmp_csv, csv_key, bucket=S3_RESULT_BUCKET):
                logger.info(
                    f"Updated CSV uploaded to s3://{S3_RESULT_BUCKET}/{csv_key}"
                )
            else:
                logger.error("Failed to upload updated CSV.")
            import os

            os.unlink(tmp_csv)
        else:
            logger.error("Failed to write updated CSV.")

    # Keep original JSON upload for backward compatibility
    combined = {
        "ocr_texts": ocr_results,
        "detection": detection_results,
        "grading": grading_results,
    }
    logger.info("Saving combined results to S3 as JSON...")
    success = save_to_s3(
        combined,
        s3_key="pipeline_results.json",
        bucket=S3_RESULT_BUCKET,
    )
    if success:
        logger.info("Pipeline completed successfully.")
    else:
        logger.error("Failed to save combined results to S3.")
        sys.exit(1)


if __name__ == "__main__":
    main()
