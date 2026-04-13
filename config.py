import os
from dotenv import load_dotenv

# Always load .env from project root (Streamlit cwd is often app/ or elsewhere)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DOTENV_PATH = os.path.join(BASE_DIR, ".env")
load_dotenv(dotenv_path=DOTENV_PATH, override=True)

YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY", "") or os.getenv("youtube_api_key", "")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "") or os.getenv("gemini_api_key", "")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "") or os.getenv("openai_api_key", "")
OUTPUT_DIR = os.path.join(BASE_DIR, "outputs")
REPORTS_DIR = os.path.join(OUTPUT_DIR, "reports")
TRANSCRIPTS_DIR = os.path.join(OUTPUT_DIR, "transcripts")
AUDIO_DIR = os.path.join(OUTPUT_DIR, "audio")
