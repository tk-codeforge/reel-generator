import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import asyncio
import subprocess
import tempfile
import streamlit as st
import json

st.set_page_config(page_title="Reel Generator", page_icon="🎬", layout="wide")

from app.styles import inject_css
from services.analysis.reel_pipeline import transcribe_then_extract_reels
from services.analysis.timestamp_utils import get_clip_times
from utils.logger import get_logger

inject_css()
logger = get_logger(__name__)

# ── UI HEADER ─────────────────────────────────────
st.title("🎬 AI Reel Generator (Accurate Clipping Mode)")

# ── Sidebar ──────────────────────────────────────
with st.sidebar:
    gemini_key = st.text_input("Gemini API Key", type="password")

# ── Inputs ───────────────────────────────────────
url = st.text_input("📺 YouTube URL")

chunk_min = st.slider("Chunk Size (minutes)", 5, 20, 10)

use_manual_ai = st.toggle("🧠 Use Manual AI JSON")

ai_output_raw = ""
if use_manual_ai:
    ai_output_raw = st.text_area(
        "Paste AI JSON Output",
        height=200,
        placeholder='''
[
  {
    "clip_text": "...",
    "start_phrase": "...",
    "end_phrase": "...",
    "duration_seconds": 30
  }
]
'''
    )

generate_clips = st.toggle("✂️ Generate Clips", True)

# ── Buttons ──────────────────────────────────────
generate_transcript_btn = st.button("🎤 Generate Transcript")
generate_reels_btn = st.button("🎬 Generate Reels")

# ── Helpers ──────────────────────────────────────
def fmt_time(sec):
    m, s = divmod(int(sec), 60)
    return f"{m:02d}:{s:02d}"

def download_video(url, output_dir):
    output_template = os.path.join(output_dir, "video.%(ext)s")

    cmd = [
        "yt-dlp",
        "-f", "bestvideo[height<=720]+bestaudio/best",
        "--merge-output-format", "mp4",
        "-o", output_template,
        url,
    ]

    subprocess.run(cmd)

    for f in os.listdir(output_dir):
        if f.endswith(".mp4"):
            return os.path.join(output_dir, f)

    raise RuntimeError("Download failed")

def clip_video(source, start, duration, output):
    cmd = [
        "ffmpeg", "-y",
        "-ss", str(start),
        "-i", source,
        "-t", str(duration),
        "-c:v", "libx264",
        "-c:a", "aac",
        output
    ]
    subprocess.run(cmd)
    return output

# ─────────────────────────────────────────────────
# 🎤 STEP 1: TRANSCRIPT
# ─────────────────────────────────────────────────
if generate_transcript_btn:

    if not url:
        st.warning("Enter YouTube URL")
        st.stop()

    chunk_duration_sec = chunk_min * 60

    st.info("🎤 Generating transcript...")

    try:
        result = asyncio.run(
            transcribe_then_extract_reels(
                url,
                gemini_api_key=gemini_key if gemini_key else "",
                chunk_duration_sec=chunk_duration_sec
            )
        )

        st.session_state["chunks"] = result.get("chunk_transcripts", [])
        st.session_state["reels"] = result.get("reels", [])

    except Exception as e:
        st.error(e)
        st.stop()

    st.success("✅ Transcript Ready")

# ─────────────────────────────────────────────────
# 📄 SHOW TRANSCRIPTS
# ─────────────────────────────────────────────────
if "chunks" in st.session_state:

    st.subheader("📄 Transcript")

    for i, txt in enumerate(st.session_state["chunks"]):
        with st.expander(f"Chunk {i+1}"):
            st.write(txt)

# ─────────────────────────────────────────────────
# 🎬 STEP 2: REEL GENERATION
# ─────────────────────────────────────────────────
if generate_reels_btn:

    if "chunks" not in st.session_state:
        st.warning("Generate transcript first")
        st.stop()

    chunks = st.session_state["chunks"]
    reels = st.session_state.get("reels", [])

    chunk_duration_sec = chunk_min * 60
    tmp_dir = tempfile.mkdtemp()

    # ── Manual AI Override ─────────────────────────
    if use_manual_ai and ai_output_raw:
        try:
            manual = json.loads(ai_output_raw)

            reels = []
            for clip in manual:
                duration = clip.get("duration_seconds") or clip.get("estimated_duration_seconds") or 30

                reels.append({
        "chunk": 1,
        "clip": type("obj", (), {
            "clip_text": clip["clip_text"],
            "explanation": clip.get("reason", "Manual AI"),
            "start_phrase": clip["start_phrase"],
            "end_phrase": clip["end_phrase"],
            "estimated_duration_minutes": duration / 60
        })()
    })

        except Exception as e:
            st.error(f"Invalid JSON: {e}")
            st.stop()

    if not reels:
        st.warning("No reels found")
        st.stop()

    # ── Download Video ────────────────────────────
    source_video = None
    if generate_clips:
        try:
            source_video = download_video(url, tmp_dir)
        except:
            st.warning("Video download failed")

    clipped = []

    # ── MAIN CLIPPING LOOP ─────────────────────────
    for idx, r in enumerate(reels):

        clip = r["clip"]

        try:
            # ✅ NEW: Accurate timestamp using phrases
            start_sec, dur_sec = get_clip_times(
                chunks,
                getattr(clip, "start_phrase", ""),
                getattr(clip, "end_phrase", ""),
                chunk_duration_sec
            )
        except:
            # fallback
            start_sec = 0
            dur_sec = 30

        dur_sec = max(15, min(120, dur_sec))

        out_path = os.path.join(tmp_dir, f"clip_{idx}.mp4")

        if source_video:
            try:
                clip_video(source_video, start_sec, dur_sec, out_path)
                clipped.append((clip, out_path, start_sec, dur_sec))
            except:
                clipped.append((clip, None, start_sec, dur_sec))
        else:
            clipped.append((clip, None, start_sec, dur_sec))

    # ── DISPLAY ───────────────────────────────────
    st.success(f"🎬 Total Reels Generated: {len(clipped)}")

    for i, (clip, path, start, dur) in enumerate(clipped):

        st.markdown(f"""
        ### 🎬 Reel {i+1}
        ⏱ {fmt_time(start)} - {fmt_time(start+dur)}

        **Hook:** {clip.clip_text}

        **Why:** {clip.explanation}
        """)

        if path and os.path.exists(path):
            with open(path, "rb") as f:
                st.video(f.read())