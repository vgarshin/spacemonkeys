"""Module 3: AI agent to detect AI-generated text."""

import logging
import os
from typing import Optional

from ..utils.llm_client import ask_llm

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


PROMPT_1 = _load_prompt("prompt_ai_detect.txt")


def detect_ai_generated(
    text: str,
    model_name: str = "deepseek-v32",
    temperature: float = 0.1,
    max_tokens: int = 32000,
    cred_path: Optional[str] = None,
) -> str:
    """
    Analyze text for AI-generated content.

    Args:
        text: Text to analyze.
        model_name: LLM model.
        temperature: Generation temperature.
        max_tokens: Max response tokens.
        cred_path: Path to credentials.

    Returns:
        LLM response with detection score and reasoning.
    """
    prompt = f"""
    {text}
    """
    response = ask_llm(
        prompt=prompt,
        instruction_text=PROMPT_1,
        model_name=model_name,
        temperature=temperature,
        max_tokens=max_tokens,
        cred_path=cred_path,
    )
    logger.info(f"AI detection response: {response}")
    return response


def batch_detect(
    texts: dict,
    output_path: Optional[str] = None,
    cred_path: Optional[str] = None,
) -> dict:
    """
    Run detection on multiple texts.

    Args:
        texts: Dict mapping identifier to text.
        output_path: Optional file to save results.
        cred_path: Path to credentials.

    Returns:
        Dict mapping identifier to detection response.
    """
    results = {}
    for key, text in texts.items():
        logger.info(f"Detecting AI for {key}...")
        try:
            results[key] = detect_ai_generated(text, cred_path=cred_path)
        except Exception as e:
            logger.error(f"Failed for {key}: {e}")
            results[key] = f"ERROR: {e}"

    if output_path:
        import json

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        logger.info(f"Results saved to {output_path}")

    return results


if __name__ == "__main__":
    # Example usage
    logging.basicConfig(level=logging.INFO)
    sample_text = "Это пример текста, который нужно проверить."
    result = detect_ai_generated(sample_text)
    print(result)
