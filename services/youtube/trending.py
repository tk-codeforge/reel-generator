import asyncio
from services.youtube.shorts import get_top_shorts

TRENDING_CHANNELS = [
    "UCX6OQ3DkcsbYNE6H8uQQuVA",
]

async def fetch_trending_shorts():
    tasks = [get_top_shorts(ch) for ch in TRENDING_CHANNELS]
    results = await asyncio.gather(*tasks)

    all_shorts = []
    for shorts in results:
        all_shorts.extend(shorts[:10])

    return all_shorts