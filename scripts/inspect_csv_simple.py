#!/usr/bin/env python3
"""
Download CSV from S3 and inspect its structure using csv module.
"""
import sys
import os
import tempfile
import csv

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.utils.s3_client import download_file_from_s3
from src.config.settings import S3_CHECK_BUCKET, CSV_KEY


def main():
    csv_key = CSV_KEY
    with tempfile.NamedTemporaryFile(suffix=".csv", delete=False, mode="w") as f:
        local_path = f.name
    try:
        success = download_file_from_s3(
            s3_key=csv_key,
            local_path=local_path,
            bucket=S3_CHECK_BUCKET,
        )
        if not success:
            print("Failed to download CSV")
            return
        # read CSV with csv module
        with open(local_path, "r", encoding="utf-8") as f:
            # guess delimiter
            sample = f.readline()
            f.seek(0)
            delimiter = "\t" if "\t" in sample else ","
            reader = csv.DictReader(f, delimiter=delimiter)
            rows = list(reader)
            print(f"Number of rows: {len(rows)}")
            if rows:
                print("Columns:", rows[0].keys())
                print("\nFirst row:")
                for k, v in rows[0].items():
                    print(f"  {k}: {v}")
    finally:
        os.unlink(local_path)


if __name__ == "__main__":
    main()
