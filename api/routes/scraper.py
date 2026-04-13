from fastapi import APIRouter, Query
from services.youtube.shorts import get_top_shorts

router = APIRouter()

@router.get("/top-shorts")
async def top_shorts(channel_id: str = Query(..., description="YouTube Channel ID"), limit: int = 50):
    """Fetch top YouTube Shorts from a channel ranked by views."""
    results = await get_top_shorts(channel_id, limit)
    return {"channel_id": channel_id, "count": len(results), "shorts": results}
