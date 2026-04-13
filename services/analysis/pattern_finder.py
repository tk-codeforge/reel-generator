import re
from collections import Counter

from models.analysis_models import PatternSummary
from services.transcription.downloader import download_audio
from services.transcription.whisper_client import transcribe_audio
from utils.logger import get_logger

logger = get_logger(__name__)


async def find_patterns(youtube_urls: list[str]) -> PatternSummary:
    """
    Transcribe a list of YouTube Shorts URLs and find repeatable patterns.
    """
    transcripts = []
    for url in youtube_urls:
        try:
            audio_path = await download_audio(url)
            text = await transcribe_audio(audio_path)
            if text and text.strip():
                transcripts.append({"url": url, "transcript": text[:1000]})
            else:
                logger.warning(f"Empty transcript for {url} — skipping.")
        except Exception as e:
            logger.warning(f"Skipping {url}: {e}")

    if not transcripts:
        return PatternSummary(
            common_topics=[],
            dominant_hook_types=[],
            repeatable_formats=[],
            top_performing_structure="No data — all videos failed to transcribe."
        )

    # ── Extract all transcript text ────────────────────────────────────────────
    all_text = " ".join(t["transcript"] for t in transcripts)

    # ── Common topics via keyword frequency ───────────────────────────────────
    keywords = extract_keywords(all_text)
    keyword_counts = Counter(keywords)
    common_topics = [word for word, _ in keyword_counts.most_common(5)]

    # ── Hook type detection (first 200 chars of each transcript) ──────────────
    hooks = []
    for t in transcripts:
        first_part = t["transcript"][:200]
        hooks.append(detect_hook_type(first_part))

    hook_counts = Counter(hooks)
    dominant_hooks = [h for h, _ in hook_counts.most_common(3)]

    # ── Format detection ───────────────────────────────────────────────────────
    formats = []
    for t in transcripts:
        text = t["transcript"].lower()
        if "1." in text or "first" in text or "second" in text or "third" in text:
            formats.append("list-style")
        elif "story" in text or "when i" in text or "one day" in text:
            formats.append("storytelling")
        elif "how to" in text or "step" in text:
            formats.append("tutorial")
        elif "?" in text[:100]:
            formats.append("question-led")
        else:
            formats.append("direct value")

    format_counts = Counter(formats)
    repeatable_formats = [f for f, _ in format_counts.most_common(3)]

    # ── Top structure insight ──────────────────────────────────────────────────
    top_hook = dominant_hooks[0] if dominant_hooks else "strong hook"
    top_format = repeatable_formats[0] if repeatable_formats else "direct value delivery"
    top_structure = (
        f"Opens with a '{top_hook}' hook in the first 3 seconds, "
        f"follows a '{top_format}' structure, "
        "delivers the core value quickly, and closes with a memorable insight or punchline."
    )

    return PatternSummary(
        common_topics=common_topics,
        dominant_hook_types=dominant_hooks,
        repeatable_formats=repeatable_formats,
        top_performing_structure=top_structure
    )


def extract_keywords(text: str) -> list[str]:
    words = re.findall(r'\b\w+\b', text.lower())
    stopwords = {
        "the", "is", "in", "and", "to", "of", "a", "for", "on", "with",
        "that", "this", "it", "was", "are", "be", "have", "has", "had",
        "but", "not", "you", "your", "they", "we", "he", "she", "at",
        "by", "an", "as", "if", "so", "do", "its", "or", "my", "me",
        "just", "all", "can", "get", "will", "about", "know", "like"
    }
    return [w for w in words if w not in stopwords and len(w) > 3]


def detect_hook_type(text: str) -> str:
    text = text.lower()
    if "?" in text[:100]:
        return "question"
    elif any(w in text for w in ["secret", "truth", "mistake", "nobody", "hidden"]):
        return "curiosity"
    elif any(w in text for w in ["you", "your"]):
        return "direct address"
    elif any(w in text for w in ["million", "billion", "%", "dollar", "number"]):
        return "data-driven"
    elif any(w in text for w in ["stop", "never", "always", "don't", "avoid"]):
        return "authority / warning"
    return "generic"


