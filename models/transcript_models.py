from pydantic import BaseModel
from typing import Optional

class Transcript(BaseModel):
    video_id: str
    url: str
    text: str
    language: Optional[str] = None
    duration_seconds: Optional[float] = None

class TranscriptChunk(BaseModel):
    chunk_index: int
    start_time: float
    end_time: float
    text: str
