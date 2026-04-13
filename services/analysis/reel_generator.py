import json
import re
import asyncio
import google.generativeai as genai
from pydantic import BaseModel
from typing import List
from utils.logger import get_logger

logger = get_logger(__name__)


class ReelClip(BaseModel):
    clip_text: str
    explanation: str
    approximate_start_percentage: int
    estimated_duration_minutes: float


async def extract_multiple_reels(full_transcript: str, api_key: str) -> List[ReelClip]:
    genai.configure(api_key=api_key)

    model = genai.GenerativeModel('gemini-2.5-flash')

    prompt = f"""
You are a viral content expert.

From the given transcript, Identify 5–10 HIGH-QUALITY viral segments.

IMPORTANT:
- Mix of short (15–30s), medium (30–60s), and long (60–120s) clips
- Prefer complete thoughts, not just hooks
- Do NOT bias toward only short clips
- Each clip must feel complete and valuable

Return JSON:
[
    {{
        "clip_text": "...",
        "explanation": "...",
        "approximate_start_percentage": 0-99,
        "estimated_duration_minutes": choose from:
0.3 (20s), 0.5 (30s), 0.75 (45s), 1.0 (60s), 1.5 (90s), 2.0 (120s)
    }}
]

Transcript:
{full_transcript}
"""

    try:
        response = await model.generate_content_async(prompt)

        json_match = re.search(r'\[.*\]', response.text, re.DOTALL)

        if not json_match:
            logger.warning("No JSON found in Gemini response")
            return []

        data = json.loads(json_match.group(0))

        # ✅ Limit output to max 10 clips
        data = data[:10]

        return [ReelClip(**clip) for clip in data]

    except Exception as e:
        logger.error(f"Gemini failed: {str(e)}")
        return []