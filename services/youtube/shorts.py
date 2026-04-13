import asyncio
import re
from googleapiclient.discovery import build
from config import YOUTUBE_API_KEY
from utils.rate_limiter import youtube_limiter
from utils.logger import get_logger

logger = get_logger(__name__)

def _get_client():
    return build("youtube", "v3", developerKey=YOUTUBE_API_KEY)

def _parse_duration(iso_duration: str) -> int:
    """Convert ISO 8601 duration (PT1M30S) to total seconds."""
    pattern = re.compile(r"PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?")
    m = pattern.match(iso_duration or "")
    if not m:
        return 0
    h, mn, s = (int(x or 0) for x in m.groups())
    return h * 3600 + mn * 60 + s

async def get_top_shorts(channel_id: str, limit: int = 50) -> list:
    """
    Fetch the top YouTube Shorts from a channel ranked by view count.
    Shorts are filtered by: duration <= 60s and title/tags contain #Shorts.
    """
    await youtube_limiter.wait()
    loop = asyncio.get_running_loop()

    def _fetch():
        yt = _get_client()

        # Step 1: Get uploads playlist ID
        ch_resp = yt.channels().list(
            part="contentDetails",
            id=channel_id
        ).execute()

        if not ch_resp.get("items"):
            logger.warning(f"Channel not found: {channel_id}")
            return []

        uploads_playlist = ch_resp["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]

        # Step 2: Collect video IDs from uploads playlist
        video_ids = []
        next_page = None
        while True:
            pl_params = dict(part="contentDetails", playlistId=uploads_playlist, maxResults=50)
            if next_page:
                pl_params["pageToken"] = next_page
            pl_resp = yt.playlistItems().list(**pl_params).execute()
            for item in pl_resp.get("items", []):
                video_ids.append(item["contentDetails"]["videoId"])
            next_page = pl_resp.get("nextPageToken")
            if not next_page or len(video_ids) >= 500:
                break

        # Step 3: Fetch video details in batches of 50
        shorts = []
        for i in range(0, len(video_ids), 50):
            batch = video_ids[i:i+50]
            v_resp = yt.videos().list(
                part="snippet,statistics,contentDetails",
                id=",".join(batch)
            ).execute()

            for v in v_resp.get("items", []):
                duration = _parse_duration(v["contentDetails"].get("duration", ""))
                title = v["snippet"].get("title", "")
                tags = v["snippet"].get("tags", [])

                # Filter: must be <= 60 seconds OR explicitly tagged as Shorts
                is_short = duration <= 60 or "#shorts" in title.lower() or \
                           any("#shorts" in t.lower() for t in tags)
                if not is_short:
                    continue

                stats = v.get("statistics", {})
                shorts.append({
                    "video_id": v["id"],
                    "title": title,
                    "url": f"https://www.youtube.com/shorts/{v['id']}",
                    "view_count": int(stats.get("viewCount", 0)),
                    "like_count": int(stats.get("likeCount", 0)),
                    "comment_count": int(stats.get("commentCount", 0)),
                    "duration_seconds": duration,
                    "published_at": v["snippet"].get("publishedAt", ""),
                    "thumbnail": v["snippet"].get("thumbnails", {}).get("high", {}).get("url", ""),
                })

        # Step 4: Sort by view count descending, return top N
        shorts.sort(key=lambda x: x["view_count"], reverse=True)
        return shorts[:limit]

    return await loop.run_in_executor(None, _fetch)
