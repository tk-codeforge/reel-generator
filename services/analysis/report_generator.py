import os
from datetime import datetime
from config import REPORTS_DIR
from services.youtube.search import search_podcasts
from services.youtube.channel import get_channel_details
from services.youtube.filters import is_news_broadcaster, has_recent_activity
from utils.logger import get_logger

logger = get_logger(__name__)

async def generate_report(query: str, limit: int = 50) -> str:
    """
    Search, filter, and rank podcasts, then write a Markdown report.
    Returns the path to the saved report file.
    """
    os.makedirs(REPORTS_DIR, exist_ok=True)

    logger.info(f"Searching podcasts: {query}")
    raw = await search_podcasts(query, limit=limit * 2)

    enriched = []
    for ch in raw:
        channel_id = ch.get("channel_id")
        if not channel_id:
            continue

        try:
            details = await get_channel_details(channel_id)
        except Exception as e:
            logger.warning(f"  [SKIP - fetch error] channel_id={channel_id}: {e}")
            continue

        if not details:
            continue

        if is_news_broadcaster(details.get("channel_name", ""), details.get("description", "")):
            logger.info(f"  [SKIP - news] {details.get('channel_name')}")
            continue

        if not has_recent_activity(details.get("last_published", ""), max_days=90):
            logger.info(f"  [SKIP - inactive] {details.get('channel_name')}")
            continue

        enriched.append(details)

    enriched.sort(key=lambda x: x.get("subscriber_count", 0), reverse=True)
    enriched = enriched[:limit]

    lines = [
        f"# Top {len(enriched)} Business Podcasts on YouTube",
        f"_Query: `{query}` | Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}_",
        "",
        "| # | Channel | Country | Subscribers | Last Published |",
        "|---|---------|---------|-------------|----------------|",
    ]

    for i, ch in enumerate(enriched, 1):
        name = ch.get("channel_name", "N/A")
        country = ch.get("country", "Unknown")
        subs = f"{ch.get('subscriber_count', 0):,}"
        last = (ch.get("last_published") or "N/A")[:10]
        ch_id = ch.get("channel_id", "")
        url = f"https://www.youtube.com/channel/{ch_id}"
        lines.append(f"| {i} | [{name}]({url}) | {country} | {subs} | {last} |")

    lines.append("")
    lines.append("---")
    lines.append("_Filtered: news broadcasters excluded. Only channels active within 90 days._")

    report_content = "\n".join(lines)

    safe_query = query.replace(" ", "_")[:40]
    filename = f"report_{safe_query}_{datetime.now().strftime('%Y%m%d_%H%M')}.md"
    report_path = os.path.join(REPORTS_DIR, filename)

    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report_content)

    logger.info(f"Report saved: {report_path}")
    return report_path

