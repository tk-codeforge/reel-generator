import asyncio
import os

from services.transcription.chunker import split_audio
from utils.cache import load_cache, save_cache
from utils.logger import get_logger

logger = get_logger(__name__)

# Cache models by name so switching between tiny/base doesn't reload
_model_cache: dict = {}


def _load_model(model_name: str = "tiny"):
    """Load and cache the local Whisper model (loaded once per model per session)."""
    global _model_cache
    if model_name not in _model_cache:
        import whisper
        logger.info(f"Loading local Whisper model: '{model_name}' — first-run only.")
        _model_cache[model_name] = whisper.load_model(model_name)
        logger.info(f"Whisper model '{model_name}' ready.")
    return _model_cache[model_name]


def _transcribe_file(audio_path: str, model_name: str = "tiny") -> str:
    """
    Transcribe a single audio file synchronously using local Whisper.

    Speed optimisations applied:
      - model_name="tiny"            : 4-5x faster than base, acceptable accuracy
      - language="en"                : skip auto language-detection pass (~20% faster)
      - beam_size=1                  : greedy decoding instead of beam search (3x faster)
      - best_of=1                    : no sampling candidates
      - temperature=0                : deterministic, no temperature fallback retries
      - condition_on_previous_text=False : no inter-segment conditioning overhead
      - fp16=False                   : required on CPU (GPU users can set True)
    """
    model = _load_model(model_name)
    result = model.transcribe(
        audio_path,
        language="en",
        fp16=False,
        beam_size=1,
        best_of=1,
        temperature=0,
        condition_on_previous_text=False,
    )
    return result.get("text", "").strip()


async def transcribe_audio(audio_path: str, model_name: str = "tiny") -> str:
    """
    Transcribe an audio file using local Whisper.
    Automatically splits large files into chunks.
    Uses 'tiny' model by default for maximum speed.

    Returns:
        Full transcript text as a single string.
    """
    cache_key = f"{model_name}_" + os.path.basename(audio_path)
    cached = load_cache(cache_key)
    if cached:
        logger.info(f"Transcript loaded from cache: {cache_key}")
        return cached.get("text", "")

    loop = asyncio.get_running_loop()

    def _run():
        chunks = split_audio(audio_path)
        full_text = []

        for chunk_path in chunks:
            logger.info(f"Transcribing: {chunk_path}")
            text = _transcribe_file(chunk_path, model_name=model_name)
            full_text.append(text)

            if chunk_path != audio_path and "_chunk" in chunk_path:
                try:
                    os.remove(chunk_path)
                except OSError:
                    pass

        return " ".join(full_text)

    text = await loop.run_in_executor(None, _run)
    save_cache(cache_key, {"text": text})
    logger.info(f"Transcription complete: {len(text)} characters")
    return text


async def transcribe_audio_chunks(
    audio_path: str,
    chunk_duration_sec: int = 600,
    model_name: str = "tiny",
) -> list[str]:
    """
    Split audio into fixed-duration chunks and transcribe each independently.
    Uses 'tiny' model by default for maximum speed.

    Returns:
        A list of transcript strings, one per chunk.
    """
    cache_key = f"{model_name}_chunks_{chunk_duration_sec}_" + os.path.basename(audio_path)
    cached = load_cache(cache_key)
    if cached:
        logger.info(f"Chunk transcripts loaded from cache: {cache_key}")
        return cached.get("chunks", [])

    loop = asyncio.get_running_loop()

    def _run():
        chunks = split_audio(audio_path, chunk_duration_sec=chunk_duration_sec, force_chunking=True)
        chunk_texts = []

        for chunk_path in chunks:
            logger.info(f"Transcribing chunk: {chunk_path}")
            try:
                text = _transcribe_file(chunk_path, model_name=model_name)
                chunk_texts.append(text)
            except Exception as e:
                logger.error(f"Failed to transcribe chunk {chunk_path}: {e}")
                chunk_texts.append("")
            finally:
                if chunk_path != audio_path and "_chunk" in chunk_path:
                    try:
                        os.remove(chunk_path)
                    except OSError:
                        pass

        return chunk_texts

    texts = await loop.run_in_executor(None, _run)
    save_cache(cache_key, {"chunks": texts})
    logger.info(f"Chunk transcription complete: {len(texts)} chunks generated.")
    return texts