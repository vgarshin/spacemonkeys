#!/usr/bin/env python3
"""
Verify that all modules can be imported.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

modules = [
    "module1_upload.uploader",
    "module2_ocr.pdf_ocr",
    "module3_ai_detect.ai_detector",
    "module4_ai_grade.ai_grader",
    "utils.s3_client",
    "utils.ocr_client",
    "utils.llm_client",
    "utils.logging_config",
    "config.settings",
]


def test_imports():
    for mod in modules:
        try:
            __import__(mod)
            print(f"✓ {mod}")
        except Exception as e:
            print(f"✗ {mod}: {e}")
            return False
    return True


if __name__ == "__main__":
    success = test_imports()
    sys.exit(0 if success else 1)
