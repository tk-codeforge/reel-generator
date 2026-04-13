import json
import os
from config import TRANSCRIPTS_DIR

def _cache_path(key: str) -> str:
    safe_key = key.replace("/", "_").replace(":", "_")
    return os.path.join(TRANSCRIPTS_DIR, f"{safe_key}.json")

def load_cache(key: str):
    path = _cache_path(key)
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return None

def save_cache(key: str, data):
    os.makedirs(TRANSCRIPTS_DIR, exist_ok=True)
    path = _cache_path(key)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
