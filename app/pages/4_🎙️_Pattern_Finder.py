import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import asyncio
import streamlit as st
import plotly.express as px
import pandas as pd

st.set_page_config(page_title="Pattern Finder", page_icon="🎙️", layout="wide")

from app.styles import inject_css
from app.openai_settings import render_openai_key_section
inject_css()
render_openai_key_section()

from services.transcription.downloader import download_audio
from services.transcription.whisper_client import transcribe_audio
from services.analysis.pattern_finder import find_patterns

# ✅ NEW IMPORTS (ML DATASET PIPELINE)
from services.analysis.dataset_builder import build_dataset_from_shorts

# (Optional) trending fetch
try:
    from services.youtube.trending import fetch_trending_shorts
    TRENDING_AVAILABLE = True
except:
    TRENDING_AVAILABLE = False


# ── Header ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div style="margin-bottom:2rem;">
    <h1 style="font-size:2rem; font-weight:800;
               background:linear-gradient(135deg,#10b981,#6366f1);
               -webkit-background-clip:text; -webkit-text-fill-color:transparent; margin:0;">
        🎙️ Pattern Finder
    </h1>
    <p style="color:#64748b; margin:0.3rem 0 0;">
        Transcribe Shorts → Find Patterns → Build ML Dataset 🚀
    </p>
</div>
""", unsafe_allow_html=True)


# ── Trending Button ────────────────────────────────────────────────────────────
if TRENDING_AVAILABLE:
    if st.button("🔥 Use Trending Shorts Data"):
        trending = asyncio.run(fetch_trending_shorts())
        urls = [s["url"] for s in trending[:10]]
        st.session_state["pattern_urls"] = "\n".join(urls)


# ── URL Input ──────────────────────────────────────────────────────────────────
pre_filled = st.session_state.get("pattern_urls", "")

if "shorts_urls" in st.session_state and st.session_state["shorts_urls"]:
    pre_filled = "\n".join(st.session_state["shorts_urls"][:10])
    ch = st.session_state.get("shorts_channel", "")
    st.info(f"✅ Pre-filled with Shorts from **{ch}**")

urls_raw = st.text_area(
    "📋 YouTube Shorts URLs (one per line)",
    value=pre_filled,
    height=160,
    placeholder="https://www.youtube.com/shorts/xxxxx\nhttps://www.youtube.com/shorts/yyyyy",
)

run = st.button("🚀 Transcribe, Analyze & Build Dataset", use_container_width=True)


# ── MAIN PIPELINE ──────────────────────────────────────────────────────────────
if run:
    urls = [u.strip() for u in urls_raw.strip().splitlines() if u.strip()]
    if not urls:
        st.warning("Please enter at least one YouTube Shorts URL.")
        st.stop()

    st.markdown(f"**Processing {len(urls)} video(s)…**")

    progress = st.progress(0)
    status = st.empty()

    transcripts = []
    dataset_rows = []
    errors = []

    # ── Process each video ─────────────────────────────────────────────────────
    for i, url in enumerate(urls):
        progress.progress(int(100 * i / len(urls)))
        status.markdown(f"⏳ Processing `{url[:60]}…`")

        try:
            # Download + Transcribe
            audio_path = asyncio.run(download_audio(url))
            text = asyncio.run(transcribe_audio(audio_path))

            transcripts.append({"url": url, "transcript": text})

            # Show transcript
            with st.expander(f"📄 Transcript {i+1}", expanded=False):
                st.text_area("", value=text, height=100, key=f"t_{i}", disabled=True)

            # ── Generate FAKE engagement (replace later with API) ──
            views = 1000000 - i * 50000
            likes = int(views * 0.05)

            # ── Build dataset rows ────────────────────────────────
            rows = build_dataset_from_shorts(
                transcript=text,
                views=views,
                likes=likes
            )

            dataset_rows.extend(rows)

        except Exception as e:
            errors.append(f"{url}: {e}")
            st.warning(f"⚠️ Skipped: {url[:60]} — {e}")

    progress.progress(85)

    # ── Save Dataset ─────────────────────────────────────────────
    if dataset_rows:
        os.makedirs("data", exist_ok=True)
        df = pd.DataFrame(dataset_rows)
        df.to_csv("data/training_data.csv", index=False)

        st.success(f"✅ Dataset generated with {len(df)} rows")
        st.dataframe(df.head(20), use_container_width=True)

    # ── Pattern Analysis ─────────────────────────────────────────
    status.markdown("🧠 Analysing patterns with GPT...")

    if not transcripts:
        st.error("All videos failed to process.")
        st.stop()

    try:
        pattern = asyncio.run(find_patterns([t["url"] for t in transcripts]))

        progress.progress(100)
        status.empty()

        st.markdown("---")
        st.subheader("✨ Pattern Analysis")

        # Topics
        st.markdown("**Common Topics**")
        pills_html = " ".join(
            f'<span class="topic-pill">{t}</span>'
            for t in (pattern.common_topics or ["—"])
        )
        st.markdown(pills_html, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # Hook chart
        if pattern.dominant_hook_types:
            fig = px.pie(
                names=pattern.dominant_hook_types,
                title="Dominant Hook Types",
                hole=0.45,
                template="plotly_dark",
            )
            st.plotly_chart(fig, use_container_width=True)

        # Formats
        c1, c2 = st.columns(2)

        with c1:
            st.markdown("**⚡ Repeatable Formats**")
            for fmt in (pattern.repeatable_formats or ["—"]):
                st.markdown(f"""
                <div class="gargi-card" style="padding:0.8rem 1rem; margin-bottom:0.5rem;">
                    ▸ {fmt}
                </div>""", unsafe_allow_html=True)

        with c2:
            st.markdown("**🏆 Top-Performing Structure**")
            st.markdown(f"""
            <div class="gargi-card" style="padding:1rem;">
                {pattern.top_performing_structure or "Not enough data"}
            </div>""", unsafe_allow_html=True)

            if pattern.avg_duration_seconds:
                st.metric("⏱ Avg Duration", f"{pattern.avg_duration_seconds:.0f}s")

    except Exception as e:
        st.error(f"Pattern analysis failed: {e}")

    # ── Errors Section ───────────────────────────────────────────
    if errors:
        with st.expander("⚠️ Errors", expanded=False):
            for err in errors:
                st.error(err)