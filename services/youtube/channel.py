import asyncio
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from config import YOUTUBE_API_KEY
from utils.rate_limiter import youtube_limiter
from utils.logger import get_logger

logger = get_logger(__name__)

def _get_client():
    return build("youtube", "v3", developerKey=YOUTUBE_API_KEY)


async def resolve_channel_handle(handle: str) -> str:
    """
    Resolve a YouTube @handle or custom URL to a channel ID (UC...).
    Accepts:
      - @ShortsBreak_Official
      - ShortsBreak_Official  (without @)
    Returns the channel ID string, or "" if not found.
    """
    await youtube_limiter.wait()
    loop = asyncio.get_running_loop()

    def _fetch():
        yt = _get_client()
        clean = handle.lstrip("@").strip()

        # Try forHandle first (works for @handle URLs)
        try:
            resp = yt.channels().list(part="id", forHandle=clean).execute()
            if resp.get("items"):
                return resp["items"][0]["id"]
        except Exception as e:
            logger.warning(f"forHandle lookup failed for '{clean}': {e}")

        # Fallback: forUsername (works for older custom URLs)
        try:
            resp = yt.channels().list(part="id", forUsername=clean).execute()
            if resp.get("items"):
                return resp["items"][0]["id"]
        except Exception as e:
            logger.warning(f"forUsername lookup failed for '{clean}': {e}")

        return ""

    return await loop.run_in_executor(None, _fetch)


async def get_channel_details(channel_id: str) -> dict:
    """Fetch channel metadata: name, subscribers, country, last upload."""
    await youtube_limiter.wait()
    loop = asyncio.get_running_loop()

    def _fetch():
        yt = _get_client()

        ch_resp = yt.channels().list(
            part="snippet,statistics,contentDetails",
            id=channel_id
        ).execute()

        if not ch_resp.get("items"):
            return {}

        item = ch_resp["items"][0]
        snippet = item.get("snippet", {})
        stats = item.get("statistics", {})
        uploads_playlist = item.get("contentDetails", {}).get("relatedPlaylists", {}).get("uploads")

        last_published = None
        if uploads_playlist:
            try:
                pl_resp = yt.playlistItems().list(
                    part="contentDetails",
                    playlistId=uploads_playlist,
                    maxResults=1
                ).execute()
                if pl_resp.get("items"):
                    last_published = pl_resp["items"][0]["contentDetails"].get("videoPublishedAt")
            except HttpError as e:
                logger.warning(f"  [SKIP playlist] channel_id={channel_id}, playlist={uploads_playlist}: {e.reason}")
            except Exception as e:
                logger.warning(f"  [SKIP playlist] channel_id={channel_id}: {e}")

        return {
            "channel_id": channel_id,
            "channel_name": snippet.get("title", ""),
            "description": snippet.get("description", ""),
            "country": snippet.get("country", ""),
            "subscriber_count": int(stats.get("subscriberCount", 0)),
            "video_count": int(stats.get("videoCount", 0)),
            "view_count": int(stats.get("viewCount", 0)),
            "last_published": last_published,
        }

    return await loop.run_in_executor(None, _fetch)
