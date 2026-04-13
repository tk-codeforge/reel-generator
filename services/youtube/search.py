import asyncio
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from config import YOUTUBE_API_KEY
from utils.rate_limiter import youtube_limiter
from utils.logger import get_logger

logger = get_logger(__name__)

def _get_client():
    return build("youtube", "v3", developerKey=YOUTUBE_API_KEY)

async def search_podcasts(query: str, limit: int = 50) -> list:
    """
    Search YouTube for podcasts matching the query.
    Returns a list of channel-level dicts sorted by relevance score.
    """
    await youtube_limiter.wait()
    loop = asyncio.get_running_loop()

    def _fetch():
        yt = _get_client()
        results = []
        next_page = None

        while len(results) < limit:
            params = dict(
                part="snippet",
                q=query,
                type="channel",
                maxResults=min(50, limit - len(results)),
                relevanceLanguage="en",
            )
            if next_page:
                params["pageToken"] = next_page

            resp = yt.search().list(**params).execute()
            for item in resp.get("items", []):
                snippet = item.get("snippet", {})
                results.append({
                    "channel_id": item["id"].get("channelId", ""),
                    "channel_name": snippet.get("channelTitle", ""),
                    "description": snippet.get("description", ""),
                    "published_at": snippet.get("publishedAt", ""),
                    "thumbnail": snippet.get("thumbnails", {}).get("default", {}).get("url", ""),
                })

            next_page = resp.get("nextPageToken")
            if not next_page:
                break

        return results

    return await loop.run_in_executor(None, _fetch)


async def get_channel_videos(channel_id: str, max_results: int = 6) -> list:
    """
    Fetch the most viewed/recent videos from a channel.
    Returns a list of video dicts with title, url, thumbnail, views.
    Channels with private/hidden uploads playlists are silently skipped.
    """
    await youtube_limiter.wait()
    loop = asyncio.get_running_loop()

    def _fetch():
        yt = _get_client()

        ch_resp = yt.channels().list(
            part="contentDetails",
            id=channel_id
        ).execute()

        if not ch_resp.get("items"):
            return []

        uploads_id = (
            ch_resp["items"][0]
            .get("contentDetails", {})
            .get("relatedPlaylists", {})
            .get("uploads")
        )
        if not uploads_id:
            return []

        try:
            pl_resp = yt.playlistItems().list(
                part="contentDetails",
                playlistId=uploads_id,
                maxResults=max_results * 3,
            ).execute()
        except HttpError as e:
            logger.warning(f"  [SKIP playlist] channel_id={channel_id}, playlist={uploads_id}: {e.reason}")
            return []
        except Exception as e:
            logger.warning(f"  [SKIP playlist] channel_id={channel_id}: {e}")
            return []

        video_ids = [
            item["contentDetails"]["videoId"]
            for item in pl_resp.get("items", [])
        ]
        if not video_ids:
            return []

        try:
            v_resp = yt.videos().list(
                part="snippet,statistics,contentDetails",
                id=",".join(video_ids)
            ).execute()
        except HttpError as e:
            logger.warning(f"  [SKIP videos] channel_id={channel_id}: {e.reason}")
            return []

        videos = []
        for v in v_resp.get("items", []):
            vid = v["id"]
            snippet = v.get("snippet", {})
            stats = v.get("statistics", {})
            duration = v.get("contentDetails", {}).get("duration", "")

            from services.youtube.shorts import _parse_duration
            dur_secs = _parse_duration(duration)
            if dur_secs <= 60:
                continue

            videos.append({
                "video_id":       vid,
                "title":          snippet.get("title", ""),
                "url":            f"https://www.youtube.com/watch?v={vid}",
                "thumbnail":      snippet.get("thumbnails", {}).get("medium", {}).get("url", ""),
                "published_at":   snippet.get("publishedAt", "")[:10],
                "view_count":     int(stats.get("viewCount", 0)),
                "like_count":     int(stats.get("likeCount", 0)),
                "duration_secs":  dur_secs,
            })

        videos.sort(key=lambda x: x["view_count"], reverse=True)
        return videos[:max_results]

    return await loop.run_in_executor(None, _fetch)
