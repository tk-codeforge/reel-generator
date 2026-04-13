"""
Streamlit sidebar: OpenAI API key override (Whisper + GPT use the same key).
"""
import os

import streamlit as st
from dotenv import load_dotenv

from config import DOTENV_PATH


def render_openai_key_section() -> None:
    with st.sidebar:
        with st.expander("OpenAI API key", expanded=False):
            st.caption(
                "Optional override — `OPENAI_API_KEY` in project `.env` is used if you leave this empty."
            )
            k = st.text_input(
                "Paste key",
                type="password",
                placeholder="sk-...",
                key="gargi_openai_key_input",
                label_visibility="collapsed",
            )
            if k and k.strip():
                os.environ["OPENAI_API_KEY"] = k.strip()
            else:
                os.environ.pop("OPENAI_API_KEY", None)
                load_dotenv(dotenv_path=DOTENV_PATH, override=True)
