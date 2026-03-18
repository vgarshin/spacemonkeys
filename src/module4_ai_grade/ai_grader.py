"""Module 4: AI agent to estimate quality and grade text work."""

import logging
import json
import os
from typing import Optional, Dict, Any

from ..utils.llm_client import ask_llm
from ..utils.s3_client import get_s3_client
from ..config.settings import S3_RESULT_BUCKET

logger = logging.getLogger(__name__)


def _load_prompt(file_name: str) -> str:
    """Load prompt text from data directory."""
    base_dir = os.path.dirname(__file__)
    prompt_path = os.path.join(base_dir, "../../data", file_name)
    try:
        with open(prompt_path, "r", encoding="utf-8") as f:
            return f.read().strip()
    except Exception as e:
        logger.error(f"Failed to load prompt from {prompt_path}: {e}")
        raise


PROMPT_2 = _load_prompt("prompt_ai_grade.txt")


def grade_text_quality(
    text: str,
    model_name: str = "qwen3-235b-a22b-fp8/latest",
    temperature: float = 0.1,
    max_tokens: int = 32000,
    cred_path: Optional[str] = None,
) -> str:
    """
    Grade text quality on a scale 1-10 with reasoning.

    Args:
        text: Text to grade.
        model_name: LLM model.
        temperature: Generation temperature.
        max_tokens: Max response tokens.
        cred_path: Path to credentials.

    Returns:
        LLM response with grade and comments.
    """
    prompt = f"""
    {text}
    """
    response = ask_llm(
        prompt=prompt,
        instruction_text=PROMPT_2,
        model_name=model_name,
        temperature=temperature,
        max_tokens=max_tokens,
        cred_path=cred_path,
    )
    logger.info(f"Grading response: {response}")
    return response


def batch_grade(
    texts: Dict[str, str],
    output_path: Optional[str] = None,
    cred_path: Optional[str] = None,
) -> Dict[str, str]:
    """
    Grade multiple texts.

    Args:
        texts: Dict mapping identifier to text.
        output_path: Optional file to save results.
        cred_path: Path to credentials.

    Returns:
        Dict mapping identifier to grading response.
    """
    results = {}
    for key, text in texts.items():
        logger.info(f"Grading {key}...")
        try:
            results[key] = grade_text_quality(text, cred_path=cred_path)
        except Exception as e:
            logger.error(f"Failed for {key}: {e}")
            results[key] = f"ERROR: {e}"

    if output_path:
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        logger.info(f"Results saved to {output_path}")

    return results


def save_to_s3(
    data: Dict[str, Any],
    s3_key: str,
    bucket: Optional[str] = None,
    cred_path: Optional[str] = None,
) -> bool:
    """
    Save grading results to S3 bucket `cosmo-gsom-result-data`.

    Args:
        data: JSON-serializable data.
        s3_key: Key (path) in S3.
        bucket: Bucket name, defaults to cosmo-gsom-result-data.
        cred_path: Path to credentials.

    Returns:
        True if successful.
    """
    try:
        client = get_s3_client(cred_path)
        if bucket is None:
            bucket = S3_RESULT_BUCKET
        import tempfile

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            tmp_path = f.name
        client.upload_file(tmp_path, bucket, s3_key)
        import os

        os.unlink(tmp_path)
        logger.info(f"Uploaded grading results to s3://{bucket}/{s3_key}")
        return True
    except Exception as e:
        logger.error(f"Failed to upload to S3: {e}")
        return False


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    sample_text = "Это пример аналитической работы."
    result = grade_text_quality(sample_text)
    print(result)
