NEWS_KEYWORDS = [
    "news", "bbc", "cnn", "aljazeera", "ntv", "citizen tv",
    "tv47", "kcb", "the standard", "daily nation", "nation africa",
    "channels tv", "arise news", "africa independent television", "ait",
    "sabc", "dstv", "mnet", "africanews", "france24", "dw africa",
    "bloomberg", "reuters", "ap news", "associated press", "abc news",
    "nbc", "cbs", "fox news", "sky news"
]

def is_news_broadcaster(channel_name: str, description: str = "") -> bool:
    """Return True if channel appears to be a news/media broadcaster."""
    combined = (channel_name + " " + description).lower()
    return any(kw in combined for kw in NEWS_KEYWORDS)

def has_recent_activity(last_published_iso: str, max_days: int = 90) -> bool:
    """Return True if channel published within the last max_days days."""
    from datetime import datetime, timezone
    if not last_published_iso:
        return False
    try:
        published = datetime.fromisoformat(last_published_iso.replace("Z", "+00:00"))
        delta = datetime.now(timezone.utc) - published
        return delta.days <= max_days
    except Exception:
        return False
