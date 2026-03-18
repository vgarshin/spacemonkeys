#!/usr/bin/env python3
"""
Test script for ask_llm function.
Uses the AI detection prompt and a sample OCR text.
"""

import sys
import logging
from pathlib import Path

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from utils.llm_client import ask_llm


def read_file(path: Path) -> str:
    """Read file content."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        logging.error(f"Failed to read {path}: {e}")
        sys.exit(1)


def main():
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    base = Path(__file__).parent.parent

    instruction_path = base / "data" / "prompt_ai_detect.txt"
    prompt_path = base / "cache" / "raw_ocr" / "Green Трио.txt"

    logger.info(f"Reading instruction from {instruction_path}")
    instruction = read_file(instruction_path)

    logger.info(f"Reading prompt from {prompt_path}")
    prompt = read_file(prompt_path)

    logger.info("Calling ask_llm...")
    try:
        response = ask_llm(
            prompt=prompt,
            instruction_text=instruction,
            model_name="deepseek-v32/latest",
            temperature=0.1,
            max_tokens=2000,
        )
        logger.info("Response received:")
        print("\n" + "=" * 80)
        print(response)
        print("=" * 80 + "\n")
    except Exception as e:
        logger.error(f"Error during LLM call: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
