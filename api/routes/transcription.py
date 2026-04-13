from fastapi import APIRouter, Body
from services.transcription.downloader import download_audio
from services.transcription.whisper_client import transcribe_audio
from services.analysis.pattern_finder import find_patterns

router = APIRouter()

@router.post("/transcribe")
async def transcribe(youtube_url: str = Body(..., embed=True)):
    """Download audio from a YouTube URL and transcribe it."""
    audio_path = await download_audio(youtube_url)
    transcript = await transcribe_audio(audio_path)
    return {"url": youtube_url, "transcript": transcript}

@router.post("/analyze-patterns")
async def analyze_patterns(youtube_urls: list[str] = Body(..., embed=True)):
    """Transcribe multiple Shorts and find repeatable patterns."""
    patterns = await find_patterns(youtube_urls)
    return {"patterns": patterns}
