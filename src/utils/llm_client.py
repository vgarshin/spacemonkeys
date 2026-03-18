"""Yandex LLM client using OpenAI SDK."""

import logging
import time
from typing import Optional

import openai
from openai import OpenAIError

from .s3_client import load_credentials
from ..config.settings import LLM_SLEEP

logger = logging.getLogger(__name__)


def ask_llm(
    prompt: str,
    instruction_text: str,
    model_name: str = "yandexgpt",
    folder_id: Optional[str] = None,
    api_key: Optional[str] = None,
    temperature: float = 0.1,
    max_tokens: int = 2000,
    cred_path: Optional[str] = None,
) -> str:
    """
    Send request to Yandex LLM and return response text.

    Args:
        prompt: User prompt.
        instruction_text: System instruction.
        model_name: Model identifier (e.g., 'yandexgpt', 'yandexgpt-lite').
        folder_id: Yandex Cloud folder ID.
        api_key: API key for LLM.
        temperature: Generation temperature.
        max_tokens: Maximum tokens in response.
        cred_path: Path to credentials JSON.

    Returns:
        Generated text.
    """
    if cred_path is None:
        creds = load_credentials()
        folder_id = creds["yandex"]["folder_id"]
        api_key = creds["yandex"]["llm_api_key"]
    else:
        creds = load_credentials(cred_path)
        if folder_id is None:
            folder_id = creds["yandex"]["folder_id"]
        if api_key is None:
            api_key = creds["yandex"]["llm_api_key"]

    # Determine base URL for Yandex Cloud OpenAI‑compatible API
    base_url = "https://ai.api.cloud.yandex.net/v1"

    client = openai.OpenAI(
        api_key=api_key,
        base_url=base_url,
        project=folder_id,
    )

    # Model URI as expected by Yandex Cloud
    model = f"gpt://{folder_id}/{model_name}"

    messages = [
        {"role": "system", "content": instruction_text},
        {"role": "user", "content": prompt},
    ]

    while True:
        try:
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=False,
            )
            text = response.choices[0].message.content
            if text is None:
                logger.error("LLM returned empty content")
                time.sleep(LLM_SLEEP)
                continue
            return text
        except OpenAIError as e:
            logger.error(f"OpenAI API error: {e}")
            time.sleep(LLM_SLEEP)
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            time.sleep(LLM_SLEEP)
