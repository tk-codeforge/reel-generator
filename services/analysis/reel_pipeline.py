import asyncio
from services.transcription.downloader import download_audio
from services.transcription.whisper_client import transcribe_audio_chunks
from services.analysis.reel_generator import extract_multiple_reels
from services.analysis.segmenter import split_into_segments
from services.analysis.ml_scorer import score_segment
from utils.logger import get_logger

logger = get_logger(__name__)


# ── Text similarity (for mapping Gemini output) ─────────────────
def similarity_score(a: str, b: str) -> float:
    a_words = set(a.lower().split())
    b_words = set(b.lower().split())

    if not a_words:
        return 0

    return len(a_words & b_words) / len(a_words)


async def transcribe_then_extract_reels(
    youtube_url: str,
    gemini_api_key: str,
    chunk_duration_sec: int = 600,
) -> dict:

    # ── Step 1: Download & Transcribe ───────────────────────────
    audio_path = await download_audio(youtube_url)

    chunk_transcripts = await transcribe_audio_chunks(
        audio_path,
        chunk_duration_sec=chunk_duration_sec
    )

    # ── Step 2: Segment transcript ──────────────────────────────
    segments = split_into_segments(chunk_transcripts, chunk_duration_sec)

    if not segments:
        return {
            "chunk_transcripts": chunk_transcripts,
            "reels": [],
            "audio_path": audio_path,
        }

    # ── Step 3: Score segments ──────────────────────────────────
    scored = []
    for seg in segments:
        score = score_segment(seg["text"], seg["position"])
        scored.append({**seg, "score": score})

    # ── Step 4: Select top segments ─────────────────────────────
    top_segments = [s for s in scored if s["score"] > 0.4]

    # fallback if too few
    if len(top_segments) < 3:
        top_segments = sorted(scored, key=lambda x: x["score"], reverse=True)[:7]

    # ── Step 5: Prepare structured input for Gemini ─────────────
    combined_text = "\n\n".join([
        f"[Segment {i+1}] {s['text']}"
        for i, s in enumerate(top_segments)
    ])

    # ── Step 6: Gemini extraction ───────────────────────────────
    reels_data = await extract_multiple_reels(combined_text, gemini_api_key)

    # ── Step 7: Map Gemini clips → real segments (FIXED) ─────────
    formatted_reels = []

    for r in reels_data:
        best_match = max(
            top_segments,
            key=lambda s: similarity_score(s["text"], r.clip_text)
        )

        formatted_reels.append({
            "chunk": best_match["chunk"],
            "sentence_index": best_match.get("sentence_index", 0),
            "total_sentences": best_match.get("total_sentences", 10),
            "clip": r
        })

    return {
        "chunk_transcripts": chunk_transcripts,
        "reels": formatted_reels,
        "audio_path": audio_path,
    }