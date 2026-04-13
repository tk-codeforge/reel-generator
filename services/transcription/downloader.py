import os
import asyncio
import subprocess
from config import AUDIO_DIR
from utils.logger import get_logger
from typing import Optional

logger = get_logger(__name__)

async def download_audio(youtube_url: str, duration: Optional[int] = None) -> str:
    os.makedirs(AUDIO_DIR, exist_ok=True)

    # Extract video ID for filename
    video_id = youtube_url.split("v=")[-1].split("&")[0].split("/")[-1]
    
    filename = f"{video_id}_{duration}s.mp3" if duration else f"{video_id}.mp3"
    output_path = os.path.join(AUDIO_DIR, filename)

    if os.path.exists(output_path):
        logger.info(f"Audio already cached: {output_path}")
        return output_path

    # THE FIX: Added --no-part and --no-mtime to resolve Windows access errors
    cmd = [
        "yt-dlp",
        "-f", "bestaudio",
        "--extract-audio",
        "--audio-format", "mp3",
        "--audio-quality", "0",
        "--no-part",           # Fixes WinError 32 (rename error)
        "--no-mtime",          # Prevents file-locking during metadata write
        "--no-cache-dir",      # Keeps it clean
        "-o", output_path,
        "--no-playlist",
    ]

    if duration:
        cmd += ["--download-sections", f"*0-{duration}"]

    cmd.append(youtube_url)

    logger.info(f"Downloading audio: {youtube_url}")
    loop = asyncio.get_running_loop()

    def _run():
        # Check if we can see ffmpeg from within the subprocess
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            # Enhanced error message to help debug
            error_msg = result.stderr if result.stderr else result.stdout
            raise RuntimeError(f"yt-dlp failed: {error_msg}")
        return output_path

    return await loop.run_in_executor(None, _run)