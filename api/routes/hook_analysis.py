from fastapi import APIRouter, Body
from services.transcription.downloader import download_audio
from services.transcription.whisper_client import transcribe_audio
from services.analysis.hook_classifier import classify_hook

router = APIRouter()

@router.post("/classify")
async def classify(youtube_url: str = Body(..., embed=True)):
    """Transcribe first 60s of a podcast and classify its hook pattern."""
    audio_path = await download_audio(youtube_url, duration=60)
    transcript = await transcribe_audio(audio_path)
    result = await classify_hook(transcript)
    return {"url": youtube_url, "transcript": transcript, "hook_analysis": result}
