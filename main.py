from fastapi import FastAPI
from api.routes import research, scraper, transcription, hook_analysis # type: ignore

app = FastAPI(
    title="AI Content Intelligence API",
    description="Market research, scraper, transcription, and hook analysis tools",
    version="1.0.0"
)

app.include_router(research.router, prefix="/research", tags=["Market Research"])
app.include_router(scraper.router, prefix="/scraper", tags=["Scraper"])
app.include_router(transcription.router, prefix="/transcription", tags=["Transcription"])
app.include_router(hook_analysis.router, prefix="/hooks", tags=["Hook Analysis"])

@app.get("/")
def root():
    return {"status": "AI Content Intelligence API is running"}
