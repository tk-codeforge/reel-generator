import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import asyncio
import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Market Research", page_icon="🔍", layout="wide")

from app.styles import inject_css
from app.openai_settings import render_openai_key_section
inject_css()
render_openai_key_section()

from services.youtube.search import search_podcasts, get_channel_videos
from services.youtube.channel import get_channel_details
from services.youtube.filters import is_news_broadcaster, has_recent_activity
from services.analysis.report_generator import generate_report
from services.openai_client import get_openai_api_key

# ── Header ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div style="margin-bottom:2rem;">
    <h1 style="font-size:2rem; font-weight:800;
               background:linear-gradient(135deg,#6366f1,#8b5cf6);
               -webkit-background-clip:text; -webkit-text-fill-color:transparent; margin:0;">
        🔍 Market Research
    </h1>
    <p style="color:#64748b; margin:0.3rem 0 0;">Discover & rank top podcasts on YouTube by region or topic</p>
</div>
""", unsafe_allow_html=True)

# ── Controls ───────────────────────────────────────────────────────────────────
with st.container():
    c1, c2, c3 = st.columns([3, 1, 1])
    with c1:
        query = st.text_input("🔎 Topic / Region Query",
                              value="business podcast Africa",
                              placeholder="e.g. entrepreneurship podcast Nigeria")
    with c2:
        limit = st.slider("Results", min_value=5, max_value=100, value=30, step=5)
    with c3:
        max_age_days = st.selectbox("Active within", [30, 60, 90, 180, 365],
                                    index=2, format_func=lambda x: f"{x} days")

run = st.button("🚀 Run Market Research", use_container_width=True)

# ── Fetch (only when Run is clicked) ───────────────────────────────────────────
if run and query:
    progress = st.progress(0, text="Searching YouTube…")

    try:
        raw = asyncio.run(search_podcasts(query, limit=limit * 2))
        progress.progress(20, text=f"Found {len(raw)} channels — enriching…")

        enriched = []
        for idx, ch in enumerate(raw):
            channel_id = ch.get("channel_id")
            if not channel_id:
                continue
            try:
                details = asyncio.run(get_channel_details(channel_id))
            except Exception:
                continue
            if not details:
                continue
            if is_news_broadcaster(details.get("channel_name", ""), details.get("description", "")):
                continue
            if not has_recent_activity(details.get("last_published", ""), max_days=max_age_days):
                continue
            
            try:
                top_vids = asyncio.run(get_channel_videos(channel_id, max_results=1))
                if top_vids:
                    details["top_video_title"] = top_vids[0]["title"]
                    details["top_video_url"] = top_vids[0]["url"]
                else:
                    details["top_video_title"] = "No suitable video"
                    details["top_video_url"] = ""
            except Exception:
                details["top_video_title"] = "Metadata unavailable"
                details["top_video_url"] = ""

            enriched.append(details)
            progress.progress(20 + int(70 * (idx + 1) / max(len(raw), 1)),
                              text=f"Enriched {len(enriched)} channels…")
            if len(enriched) >= limit:
                break

        enriched.sort(key=lambda x: x.get("subscriber_count", 0), reverse=True)
        progress.progress(95, text="Building report…")

        st.session_state["mr_enriched"] = enriched
        st.session_state["mr_query"] = query
        st.session_state.pop("mr_reel_result", None)

        with st.spinner("Generating Markdown report…"):
            try:
                report_path = asyncio.run(generate_report(query, limit=limit))
                with open(report_path, "r", encoding="utf-8") as f:
                    st.session_state["mr_report_md"] = f.read()
            except Exception as e:
                st.session_state["mr_report_md"] = None
                st.warning(f"Report generation skipped: {e}")

        progress.progress(100, text="Done!")

    except Exception as e:
        st.error(f"Error: {e}")
        progress.empty()

enriched = st.session_state.get("mr_enriched")


# ── Results (persist after Run; any other button e.g. Extract keeps this visible) ─
if enriched is not None:
    q = st.session_state.get("mr_query", query)

    if not enriched:
        st.info("No podcasts matched the filters. Try broadening the query or increasing the active window.")
    else:
        # ── Summary metrics ────────────────────────────────────────────────────
        st.markdown("---")
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Channels Found", len(enriched))
        m2.metric("Avg Subscribers",
                  f"{int(sum(c.get('subscriber_count',0) for c in enriched)/max(len(enriched),1)):,}")
        countries = [c.get("country","?") for c in enriched if c.get("country")]
        m3.metric("Countries", len(set(countries)))
        m4.metric("Query", f'"{q[:25]}…"' if len(q)>25 else f'"{q}"')

        # ── Table ──────────────────────────────────────────────────────────────
        df = pd.DataFrame([{
            "Rank":        i + 1,
            "Channel":     c.get("channel_name", ""),
            "Country":     c.get("country", "—"),
            "Subscribers": c.get("subscriber_count", 0),
            "Videos":      c.get("video_count", 0),
            "Last Active": (c.get("last_published") or "—")[:10],
            "Top Video Title": c.get("top_video_title", "—"),
            "Video Link":  c.get("top_video_url", ""),
            "Channel ID":  c.get("channel_id", ""),
        } for i, c in enumerate(enriched)])

        st.subheader("📋 Ranked Results")
        _sub_max = df["Subscribers"].max()
        _sub_cap = max(1, int(_sub_max)) if pd.notna(_sub_max) else 1
        st.dataframe(
            df.drop(columns=["Channel ID"]),
            use_container_width=True,
            hide_index=True,
            column_config={
                "Subscribers": st.column_config.ProgressColumn(
                    "Subscribers",
                    min_value=0,
                    max_value=_sub_cap,
                    format="%d",
                ),
                "Video Link": st.column_config.LinkColumn(
                    "Video Link",
                    display_text="Watch Video"
                )
            }
        )

        # ── Chart ──────────────────────────────────────────────────────────
        fig = px.bar(
            df.head(20), x="Subscribers", y="Channel", orientation="h",
            color="Subscribers", color_continuous_scale=["#6366f1","#8b5cf6","#ec4899"],
            title="Top 20 Channels by Subscribers",
            template="plotly_dark",
        )
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            showlegend=False,
            yaxis={"categoryorder":"total ascending"},
            margin=dict(l=10, r=10, t=40, b=10),
        )
        st.plotly_chart(fig, use_container_width=True)

        # ── Download report (built when you last ran research) ─────────────
        report_md = st.session_state.get("mr_report_md")
        if report_md:
            st.download_button(
                "⬇️ Download Markdown Report",
                data=report_md,
                file_name=f"gargi_report_{q[:30].replace(' ','_')}.md",
                mime="text/markdown",
                use_container_width=True,
            )
        else:
            st.caption("Markdown report was not generated on the last run.")

        # ── Generate reel (same page) ─
        st.markdown("---")
        st.subheader("Reel insights from top video")
        st.caption(
            "Transcribes the selected video with Whisper, then suggests short-form hook ideas. "
            "Requires an OpenAI API key (sidebar or `.env`)."
        )

        valid_channels = [c for c in enriched if c.get("top_video_url")]

        if valid_channels:
            selected_channel = st.selectbox(
                "Video",
                options=valid_channels,
                format_func=lambda x: f"{x.get('channel_name')} — {x.get('top_video_title')}",
                key="mr_pick_channel",
            )

            run_here = st.button(
                "Generate reel insights",
                use_container_width=True,
                key="mr_transcribe_here",
            )

            if run_here:
                if not get_openai_api_key():
                    st.error(
                        "Add your OpenAI API key in the sidebar (**OpenAI API key**) or set `OPENAI_API_KEY` in `.env`."
                    )
                else:
                    vid_url = selected_channel["top_video_url"]
                    progress_mr = st.progress(0, text="Working…")
                    stat_mr = st.empty()
                    try:
                        from services.analysis.reel_pipeline import transcribe_then_extract_reels

                        progress_mr.progress(15, text="Preparing…")
                        stat_mr.markdown("*Long videos may take several minutes.*")
                        result = asyncio.run(
                            transcribe_then_extract_reels(
                                vid_url,
                                chunk_duration_sec=600,
                                skip_reel_extraction=False,
                            )
                        )
                        progress_mr.progress(100, text="Done")
                        stat_mr.empty()
                        progress_mr.empty()
                        st.session_state["mr_reel_result"] = {
                            "channel_name": selected_channel["channel_name"],
                            "video_url": vid_url,
                            "video_title": selected_channel.get("top_video_title", ""),
                            "chunk_transcripts": result["chunk_transcripts"],
                            "reels": result["reels"],
                        }
                        st.success("Analysis complete. Results appear below.")
                    except Exception as e:
                        progress_mr.empty()
                        stat_mr.empty()
                        st.error(f"Could not complete: {e}")

            mr_out = st.session_state.get("mr_reel_result")
            if mr_out:
                st.markdown("---")
                st.subheader("Results")
                st.markdown(f"**{mr_out.get('channel_name', 'Channel')}**")
                if mr_out.get("video_title"):
                    st.caption(mr_out["video_title"])

                chunks = mr_out.get("chunk_transcripts") or []
                if not chunks:
                    st.warning(
                        "No transcript was returned. Verify the URL, API key, and that yt-dlp and ffmpeg are installed."
                    )
                else:
                    st.markdown("##### Transcript")
                    st.caption(f"{len(chunks)} segments · ~10 minutes each")
                    for i, txt in enumerate(chunks):
                        label = f"Segment {i + 1} · ~{i * 10}–{(i + 1) * 10} min"
                        with st.expander(label, expanded=(i == 0 and len(chunks) <= 3)):
                            st.code(txt or "(empty)", language=None)

                reels = mr_out.get("reels") or []
                if chunks and not reels:
                    st.info(
                        "No hook suggestions for this run. Segments may be too short or low on speech."
                    )
                elif reels:
                    st.markdown("##### Suggested hooks (~15 seconds)")
                    for r in reels:
                        clip = r["clip"]
                        chunk_num = r["chunk"]
                        st.markdown(f"""
                        <div class="gargi-card" style="border-left: 4px solid #8b5cf6; margin-bottom:1rem;">
                            <div style="font-weight:700; color:#a78bfa; margin-bottom:0.3rem;">
                                Segment {chunk_num} · ~{(chunk_num - 1) * 10}–{chunk_num * 10} min
                                <span style="font-size:0.8rem; color:#94a3b8;"> · ~{clip.approximate_start_percentage}% into segment</span>
                            </div>
                            <div style="font-size:1.05rem; font-weight:bold; color:#f1f5f9; background:#1e293b; padding:1rem; border-radius:0.5rem; margin-bottom:0.6rem; border-left:3px solid #f59e0b;">
                                "{clip.clip_text}"
                            </div>
                            <div style="font-size:0.9rem; color:#cbd5e1;">
                                <span style="font-weight:600; color:#94a3b8;">Why it works:</span> {clip.explanation}
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
        else:
            st.info("No videos available for analysis.")

