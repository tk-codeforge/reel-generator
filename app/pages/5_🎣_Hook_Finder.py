import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import asyncio
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="Hook Finder", page_icon="🎣", layout="wide")

from app.styles import inject_css, HOOK_COLORS, HOOK_DESCRIPTIONS
from app.openai_settings import render_openai_key_section
inject_css()
render_openai_key_section()

from services.transcription.downloader import download_audio
from services.transcription.whisper_client import transcribe_audio
from services.analysis.hook_classifier import classify_hook

# ── Header ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div style="margin-bottom:2rem;">
    <h1 style="font-size:2rem; font-weight:800;
               background:linear-gradient(135deg,#f59e0b,#ec4899);
               -webkit-background-clip:text; -webkit-text-fill-color:transparent; margin:0;">
        🎣 Hook Finder
    </h1>
    <p style="color:#64748b; margin:0.3rem 0 0;">
        Classify podcast episode hooks into 7 proven patterns using local Whisper
    </p>
</div>
""", unsafe_allow_html=True)

# ── Reference: 7 hook types ────────────────────────────────────────────────────
with st.expander("📖 The 7 Hook Patterns", expanded=False):
    cols = st.columns(2)
    for i, (hook_name, (icon, desc, template)) in enumerate(HOOK_DESCRIPTIONS.items()):
        color = HOOK_COLORS.get(hook_name, "#6366f1")
        with cols[i % 2]:
            st.markdown(f"""
            <div class="gargi-card" style="border-left:3px solid {color}; padding:0.8rem 1rem; margin-bottom:0.5rem;">
                <div style="font-weight:700; color:{color};">{icon} {hook_name}</div>
                <div style="font-size:0.8rem; color:#94a3b8; margin:0.3rem 0;">{desc}</div>
                <div style="font-size:0.75rem; color:#4b5563; font-style:italic;">{template}</div>
            </div>
            """, unsafe_allow_html=True)

# ── Input ──────────────────────────────────────────────────────────────────────
urls_raw = st.text_area(
    "🎙️ Podcast Episode URLs (one per line)",
    height=120,
    placeholder="https://www.youtube.com/watch?v=xxxx\nhttps://www.youtube.com/watch?v=yyyy",
)

run = st.button("🚀 Analyse Hooks", use_container_width=True)

if run:
    urls = [u.strip() for u in urls_raw.strip().splitlines() if u.strip()]
    if not urls:
        st.warning("Please enter at least one YouTube URL.")
        st.stop()

    results = []
    progress = st.progress(0)
    status = st.empty()

    for i, url in enumerate(urls):
        status.markdown(f"⏳ `{url[:65]}` — downloading first 60s…")
        progress.progress(int(100 * i / len(urls)))
        try:
            audio_path = asyncio.run(download_audio(url, duration=60))
            status.markdown("🎤 Transcribing hook…")
            transcript = asyncio.run(transcribe_audio(audio_path))
            status.markdown("🧠 Classifying hook pattern…")
            analysis = asyncio.run(classify_hook(transcript))
            results.append({"url": url, "transcript": transcript, "analysis": analysis})
        except Exception as e:
            st.warning(f"⚠️ Skipped: {url[:60]} — {e}")

    progress.progress(100)
    status.empty()

    if not results:
        st.error("All URLs failed. Check them and try again.")
        st.stop()

    st.markdown("---")
    st.subheader(f"📊 Results — {len(results)} Episode(s) Analysed")

    # ── Per-result cards ───────────────────────────────────────────────────────
    for idx, r in enumerate(results):
        a = r["analysis"]
        color = HOOK_COLORS.get(a.hook_type, "#6366f1")
        icon, desc, _ = HOOK_DESCRIPTIONS.get(a.hook_type, ("🎣", "", ""))
        score = a.strength_score

        with st.container():
            st.markdown(f"""
            <div class="gargi-card" style="border-left: 4px solid {color};">
                <div style="display:flex; justify-content:space-between; align-items:flex-start;">
                    <div>
                        <span class="hook-badge" style="background:linear-gradient(135deg,{color},{color}aa);">
                            {icon} {a.hook_type}
                        </span>
                        <div style="color:#94a3b8; font-size:0.78rem; margin-top:0.5rem;">
                            {r['url'][:80]}
                        </div>
                    </div>
                    <div style="text-align:right;">
                        <div style="font-size:1.8rem; font-weight:800; color:{color};">
                            {int(score * 100)}
                        </div>
                        <div style="font-size:0.7rem; color:#64748b;">strength score</div>
                    </div>
                </div>
                <div style="margin:0.8rem 0 0.4rem; color:#e2e8f0; font-size:0.85rem;">
                    <b>Template:</b> <span style="color:#a5b4fc;">{a.template_match}</span>
                </div>
                <div style="color:#94a3b8; font-size:0.82rem; line-height:1.5;">
                    {a.explanation}
                </div>
            </div>
            """, unsafe_allow_html=True)

            # Strength gauge — unique key per result to avoid duplicate element ID error
            fig = go.Figure(go.Indicator(
                mode="gauge+number",
                value=score * 100,
                domain={"x": [0, 1], "y": [0, 1]},
                gauge={
                    "axis": {"range": [0, 100], "tickcolor": "#4b5563"},
                    "bar": {"color": color},
                    "bgcolor": "rgba(0,0,0,0)",
                    "borderwidth": 0,
                    "steps": [
                        {"range": [0, 40],  "color": "rgba(255,255,255,0.03)"},
                        {"range": [40, 70], "color": "rgba(255,255,255,0.05)"},
                        {"range": [70, 100],"color": "rgba(255,255,255,0.07)"},
                    ],
                },
                number={"suffix": "%", "font": {"color": color, "size": 24}},
            ))
            fig.update_layout(
                height=180,
                paper_bgcolor="rgba(0,0,0,0)",
                font={"color": "#94a3b8", "size": 11},
                margin=dict(l=20, r=20, t=10, b=10),
            )
            st.plotly_chart(fig, use_container_width=True, key=f"gauge_{idx}")

            with st.expander("📄 Transcript (first 60s)", expanded=False):
                st.caption(r["transcript"][:1500])

    # ── Summary distribution ───────────────────────────────────────────────────
    if len(results) > 1:
        st.markdown("---")
        st.subheader("📈 Hook Type Distribution")
        hook_counts = {}
        for r in results:
            ht = r["analysis"].hook_type
            hook_counts[ht] = hook_counts.get(ht, 0) + 1

        fig2 = px.pie(
            names=list(hook_counts.keys()),
            values=list(hook_counts.values()),
            color=list(hook_counts.keys()),
            color_discrete_map=HOOK_COLORS,
            hole=0.45,
            template="plotly_dark",
        )
        fig2.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            legend=dict(font=dict(color="#94a3b8")),
        )
        st.plotly_chart(fig2, use_container_width=True, key="hook_distribution_pie")