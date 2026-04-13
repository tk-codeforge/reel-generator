from pydantic import BaseModel
from typing import Optional

class ShortVideo(BaseModel):
    video_id: str
    title: str
    url: str
    view_count: int
    like_count: Optional[int] = None
    comment_count: Optional[int] = None
    duration_seconds: Optional[int] = None
    published_at: Optional[str] = None
    thumbnail: Optional[str] = None

class ChannelInfo(BaseModel):
    channel_id: str
    channel_name: str
    subscriber_count: Optional[int] = None
    country: Optional[str] = None
    description: Optional[str] = None
    last_published: Optional[str] = None

class PodcastResult(BaseModel):
    rank: int
    channel: ChannelInfo
    relevance_score: float
