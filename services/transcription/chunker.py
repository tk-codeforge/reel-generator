import math
import os
import subprocess
from utils.logger import get_logger

logger = get_logger(__name__)

MAX_CHUNK_BYTES = 24 * 1024 * 1024  # 24 MB (Whisper limit is 25 MB)
CHUNK_DURATION_SEC = 10 * 60  # 10 minutes per chunk


def _get_duration_seconds(audio_path: str) -> float:
    """Use ffprobe to get the duration of an audio file in seconds."""
    result = subprocess.run(
        [
            "ffprobe", "-v", "error",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            audio_path,
        ],
        capture_output=True,
        text=True,
    )
    try:
        return float(result.stdout.strip())
    except ValueError:
        return 0.0


def split_audio(audio_path: str, chunk_duration_sec: int = CHUNK_DURATION_SEC, force_chunking: bool = False) -> list[str]:
    """
    Split a large audio file into chunks small enough for Whisper API or enforced segment brackets.
    Uses ffmpeg directly — no pydub/pyaudioop dependency.

    Args:
        audio_path: Path to the source .mp3 file
        chunk_duration_sec: Max chunk duration in seconds (default: 10 min)
        force_chunking: Set to True to skip file size check and strictly segment the video.

    Returns:
        List of chunk file paths (original file if small enough and force_chunking=False)
    """
    file_size = os.path.getsize(audio_path)

    # If small enough and not forced to chunk, no splitting needed
    if not force_chunking and file_size <= MAX_CHUNK_BYTES:
        return [audio_path]

    total_sec = _get_duration_seconds(audio_path)
    if total_sec == 0:
        logger.warning("Could not determine audio duration, returning original file.")
        return [audio_path]

    num_chunks = math.ceil(total_sec / chunk_duration_sec)
    logger.info(f"File too large ({file_size / 1e6:.1f} MB), splitting into {num_chunks} chunks...")

    base_name = os.path.splitext(audio_path)[0]
    chunk_paths = []

    for i in range(num_chunks):
        start = i * chunk_duration_sec
        chunk_path = f"{base_name}_chunk{i}.mp3"
        cmd = [
            "ffmpeg", "-y",
            "-ss", str(start),
            "-t", str(chunk_duration_sec),
            "-i", audio_path,
            "-acodec", "libmp3lame",
            "-q:a", "2",
            chunk_path,
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            raise RuntimeError(f"ffmpeg chunk failed: {result.stderr}")
        chunk_paths.append(chunk_path)
        logger.info(f"  Chunk {i+1}/{num_chunks}: {chunk_path}")

    return chunk_paths
