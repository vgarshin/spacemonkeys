#!/usr/bin/env python3
"""
Download CSV from S3 and inspect its structure.
"""
import sys
import os
import tempfile
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.utils.s3_client import download_file_from_s3
from src.config.settings import S3_CHECK_BUCKET, CSV_KEY


def main():
    csv_key = CSV_KEY
    with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as f:
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
        # read CSV with pandas
        df = pd.read_csv(local_path, sep="\t")  # tab-separated?
        print(f"Shape: {df.shape}")
        print("Columns:", df.columns.tolist())
        print("\nFirst few rows:")
        print(df.head())
        # Check Grade and Maximum grade columns
        if "Grade" in df.columns:
            print("\nGrade column sample:", df["Grade"].head())
        if "Maximum grade" in df.columns:
            print("Maximum grade sample:", df["Maximum grade"].head())
    finally:
        os.unlink(local_path)


if __name__ == "__main__":
    main()
