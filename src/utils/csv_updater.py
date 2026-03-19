"""CSV updater for grading results."""

import os
import csv
import logging
import re
import tempfile
from datetime import datetime
from typing import Dict, List, Optional

from .s3_client import download_file_from_s3, upload_file_to_s3
from ..config.settings import S3_CHECK_BUCKET, S3_RESULT_BUCKET

logger = logging.getLogger(__name__)


def extract_grade_from_grading_result(text: str) -> Optional[int]:
    """
    Extract final grade from grading result text.

    Expects format: "Итого: X из Y." or "Тестовый балл: Z из 100."
    Returns grade as integer (0-100) if found, else None.
    """
    # Try to find "Итого: X из Y."
    match = re.search(r"Итого:\s*(\d+)\s*из\s*(\d+)", text)
    if match:
        score = int(match.group(1))
        total = int(match.group(2))
        if total == 0:
            return 0
        grade = round(score * 100 / total)
        return min(grade, 100)
    # Fallback: look for "Тестовый балл: Z из 100."
    match = re.search(r"Тестовый балл:\s*(\d+)\s*из\s*100", text)
    if match:
        return int(match.group(1))
    logger.warning(f"Cannot extract grade from text: {text[:200]}...")
    return None


def download_csv(
    csv_key: str, bucket: Optional[str] = None
) -> Optional[List[Dict[str, str]]]:
    """Download CSV from S3 and parse into list of dicts."""
    if bucket is None:
        bucket = S3_CHECK_BUCKET
    with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as f:
        local_path = f.name
    try:
        success = download_file_from_s3(
            s3_key=csv_key, local_path=local_path, bucket=bucket
        )
        if not success:
            logger.error(f"Failed to download CSV {csv_key}")
            return None
        with open(local_path, "r", encoding="utf-8") as f:
            # Detect delimiter
            sample = f.readline()
            f.seek(0)
            delimiter = "\t" if "\t" in sample else ","
            reader = csv.DictReader(f, delimiter=delimiter)
            rows = list(reader)
            logger.info(f"Loaded {len(rows)} rows from {csv_key}")
            return rows
    except Exception as e:
        logger.error(f"Error parsing CSV: {e}")
        return None
    finally:
        import os

        os.unlink(local_path)


def update_csv_rows(
    rows: List[Dict[str, str]],
    grading_results: Dict[str, str],
    mapping_func,
) -> List[Dict[str, str]]:
    """
    Update CSV rows with grades from grading_results.

    Args:
        rows: List of dicts representing CSV rows.
        grading_results: Dict mapping identifier to grading result text.
        mapping_func: Function that maps a row to an identifier key.

    Returns:
        Updated rows with 'Grade' and 'Last modified (grade)' columns.
    """
    updated = []
    for row in rows:
        identifier = mapping_func(row)
        grade_text = grading_results.get(identifier)
        if grade_text:
            grade = extract_grade_from_grading_result(grade_text)
            if grade is not None:
                row["Grade"] = str(grade)
                row["Last modified (grade)"] = datetime.now().strftime(
                    "%A, %d %B %Y, %I:%M %p"
                )
            else:
                logger.warning(f"Could not extract grade for {identifier}")
        else:
            logger.warning(f"No grading result for {identifier}")
        updated.append(row)
    return updated


def write_csv(
    rows: List[Dict[str, str]], output_path: str, delimiter: str = "\t"
) -> bool:
    """Write rows to CSV file."""
    if not rows:
        return False
    fieldnames = rows[0].keys()
    try:
        with open(output_path, "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter=delimiter)
            writer.writeheader()
            writer.writerows(rows)
        return True
    except Exception as e:
        logger.error(f"Failed to write CSV: {e}")
        return False


def upload_csv(
    local_path: str,
    s3_key: str,
    bucket: Optional[str] = None,
) -> bool:
    """Upload CSV to S3 bucket."""
    if bucket is None:
        bucket = S3_RESULT_BUCKET
    return upload_file_to_s3(local_path, s3_key, bucket=bucket)


def default_mapping(row: Dict[str, str]) -> str:
    """
    Default mapping from CSV row to identifier used in grading_results.

    Assumes grading_results keys are PDF S3 keys (paths). This function
    should be overridden based on actual mapping logic.
    """
    # For now, return the 'Identifier' column as is.
    return row.get("Identifier", "")


def extract_group_from_filename(filename: str) -> str:
    """
    Extract group name from a file name using underscore splitting.

    Example: "Дети солнца 2.0_4960_assignsubmission_file" -> "Дети солнца 2.0"
    Example: "4_5038_assignsubmission_file/Лапки.pdf" -> "4"
    """
    # Split by path separator and take first component
    path_parts = filename.split("/")
    first_component = path_parts[-2]
    # Remove file extension if present
    base = os.path.splitext(first_component)[0]
    # Split by underscore and take first part
    parts = base.split("_")
    return parts[0] if parts else ""


def group_mapping(row: Dict[str, str]) -> str:
    """
    Mapping that uses the 'Group' column of the CSV.
    """
    return row.get("Group", "")


if __name__ == "__main__":
    # Simple test
    logging.basicConfig(level=logging.INFO)
    sample_text = "Все критерии: 0 / 0 / 10 / 20 / 0 / 5. Итого: 35 из 60."
    grade = extract_grade_from_grading_result(sample_text)
    print(f"Extracted grade: {grade}")
