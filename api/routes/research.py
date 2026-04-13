from fastapi import APIRouter, Query
from services.youtube.search import search_podcasts
from services.analysis.report_generator import generate_report

router = APIRouter()

@router.get("/podcasts")
async def find_podcasts(query: str = Query("business podcast Africa"), limit: int = 50):
    """Search and rank top podcasts from YouTube."""
    podcasts = await search_podcasts(query, limit)
    return {"count": len(podcasts), "podcasts": podcasts}

@router.get("/report")
async def podcast_report(query: str = Query("business podcast Africa")):
    """Generate a Markdown report of top podcasts."""
    report_path = await generate_report(query)
    return {"report_path": report_path}
