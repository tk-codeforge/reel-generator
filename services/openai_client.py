"""
Lazy OpenAI client so the API key can be set from Streamlit sidebar or .env at runtime.
"""
import os

from openai import OpenAI


def get_openai_api_key() -> str:
    # Support OPENAI_API_KEY (standard) or openai_api_key in .env
    return (
        os.getenv("OPENAI_API_KEY", "").strip()
        or os.getenv("openai_api_key", "").strip()
    )


def get_openai_client() -> OpenAI:
    k = get_openai_api_key()
    if not k:
        raise ValueError(
            "OPENAI_API_KEY is not set. Paste your key in the sidebar (OpenAI API key) "
            "or add OPENAI_API_KEY to your .env file."
        )
    return OpenAI(api_key=k)
