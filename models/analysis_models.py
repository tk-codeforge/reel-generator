from pydantic import BaseModel
from typing import List, Optional

class HookAnalysis(BaseModel):
    hook_type: str           # e.g. "Big Promise", "Shock / Controversy"
    template_match: str      # matched template string
    strength_score: float    # 0.0 - 1.0
    explanation: str

class PatternSummary(BaseModel):
    common_topics: List[str]
    dominant_hook_types: List[str]
    avg_duration_seconds: Optional[float] = None
    repeatable_formats: List[str]
    top_performing_structure: Optional[str] = None
