import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import asyncio
import re
import streamlit as st
import plotly.express as px
import pandas as pd

st.set_page_config(page_title="Shorts Scraper", page_icon="📊", layout="wide")

from app.styles import inject_css
inject_css()

from services.youtube.shorts import get_top_shorts
from services.youtube.channel import get_channel_details, resolve_channel_handle


def extract_channel_id(input_str: str) -> tuple[str, str]:
    """
    Parse the user input and return (channel_id_or_handle, input_type).
    input_type is one of: "id", "handle", "unknown"

    Supported formats:
      - https://www.youtube.com/channel/UCxxxxx
      - https://www.youtube.com/@HandleName
      - https://www.youtube.com/@HandleName/shorts  (or /videos, etc.)
      - @HandleName
      - UCxxxxx  (raw channel ID)
    """
    s = input_str.strip()

    # /channel/UC... URL
    m = re.search(r"/channel/(UC[^/?&\s]+)", s)
    if m:
        return m.group(1), "id"

    # /@handle URL  (with optional trailing path like /shorts)
    m = re.search(r"/@([^/?&\s]+)", s)
    if m:
        return m.group(1), "handle"

    # Raw UC... channel ID
    if re.match(r"^UC[A-Za-z0-9_\-]{20,}$", s):
        return s, "id"

    # Raw @handle
    if s.startswith("@"):
        return s.lstrip("@"), "handle"

    # Unknown — pass as-is and hope the API handles it
    return s, "unknown"


# ── Header ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div style="margin-bottom:2rem;">
    <h1 style="font-size:2rem; font-weight:800;
                background:linear-gradient(135deg,#6366f1,#ec4899);
                -webkit-background-clip:text; -webkit-text-fill-color:transparent; margin:0;">
        📊 Shorts Scraper
    </h1>
    <p style="color:#64748b; margin:0.3rem 0 0;">Extract & rank top-performing YouTube Shorts from any channel</p>
</div>
""", unsafe_allow_html=True)

# ── Controls ───────────────────────────────────────────────────────────────────
c1, c2 = st.columns([4, 1])
with c1:
    channel_input = st.text_input(
        "📺 Channel URL or ID",
        placeholder="https://www.youtube.com/@MrBeast  OR  UCX6OQ3DkcsbYNE6H8uQQuVA",
    )
with c2:
    limit = st.slider("Top N Shorts", min_value=5, max_value=50, value=20, step=5)

run = st.button("🚀 Scrape Top Shorts", use_container_width=True)

if run and channel_input:
    raw_value, input_type = extract_channel_id(channel_input)
    progress = st.progress(0, text="Resolving channel…")

    try:
        # ── Resolve handle → channel ID if needed ──────────────────────────────
        if input_type == "handle":
            progress.progress(10, text=f"Resolving @{raw_value}…")
            channel_id = asyncio.run(resolve_channel_handle(raw_value))
            if not channel_id:
                st.error(
                    f"Could not find a YouTube channel for **@{raw_value}**. "
                    "Check the spelling or try pasting the full channel URL."
                )
                st.stop()
        else:
            channel_id = raw_value

        # ── Channel details ────────────────────────────────────────────────────
        progress.progress(20, text="Fetching channel info…")
        try:
            info = asyncio.run(get_channel_details(channel_id))
            ch_name = info.get("channel_name", channel_id)
            subs = info.get("subscriber_count", 0)
        except Exception:
            ch_name = channel_id
            subs = 0

        # ── Fetch Shorts ───────────────────────────────────────────────────────
        progress.progress(30, text="Fetching Shorts…")
        shorts = asyncio.run(get_top_shorts(channel_id, limit=limit))
        progress.progress(90, text="Building results…")

        if not shorts:
            st.warning(
                "No Shorts found for this channel. "
                "The channel may not have public Shorts, or its uploads playlist is private."
            )
            st.stop()

        # ── Channel header ─────────────────────────────────────────────────────
        st.markdown(f"""
        <div class="gargi-card" style="display:flex; align-items:center; gap:1rem;">
            <div style="font-size:2.5rem;">📺</div>
            <div>
                <div style="font-size:1.2rem; font-weight:700; color:#e2e8f0;">{ch_name}</div>
                <div style="color:#64748b; font-size:0.85rem;">{subs:,} subscribers · Top {len(shorts)} Shorts</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # ── Metrics ────────────────────────────────────────────────────────────
        m1, m2, m3, m4 = st.columns(4)
        total_views = sum(s["view_count"] for s in shorts)
        avg_views   = total_views // max(len(shorts), 1)
        top_views   = shorts[0]["view_count"] if shorts else 0
        m1.metric("Total Views", f"{total_views:,}")
        m2.metric("Avg Views / Short", f"{avg_views:,}")
        m3.metric("Top Short Views", f"{top_views:,}")
        m4.metric("Shorts Analysed", len(shorts))

        # ── Plotly chart ───────────────────────────────────────────────────────
        df = pd.DataFrame(shorts)
        df["short_title"] = df["title"].str[:40] + "…"
        fig = px.bar(
            df, x="view_count", y="short_title", orientation="h",
            color="view_count", color_continuous_scale=["#6366f1","#8b5cf6","#ec4899"],
            title=f"Top {len(shorts)} Shorts by Views — {ch_name}",
            labels={"view_count": "Views", "short_title": ""},
            template="plotly_dark",
        )
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            showlegend=False,
            yaxis={"categoryorder":"total ascending"},
            margin=dict(l=10, r=10, t=40, b=10),
            height=max(350, len(shorts) * 28),
        )
        st.plotly_chart(fig, use_container_width=True)

        # ── Thumbnail grid ─────────────────────────────────────────────────────
        st.subheader("🎬 Shorts Gallery")
        cols_per_row = 4
        for row_start in range(0, min(len(shorts), 20), cols_per_row):
            row_shorts = shorts[row_start:row_start + cols_per_row]
            cols = st.columns(cols_per_row)
            for col, s in zip(cols, row_shorts):
                with col:
                    # Using HTML img tag inside the anchor to maintain aesthetic grid look
                    img_html = f'<img src="{s["thumbnail"]}" style="width:100%; border-radius:0.4rem; margin-bottom:0.3rem;" />' if s.get("thumbnail") else ''
                    
                    st.markdown(f"""
                    <a href="{s['url']}" target="_blank" style="text-decoration: none; color: inherit;">
                        <div style="cursor: pointer;">
                            {img_html}
                            <div style="font-size:0.75rem; color:#e2e8f0; font-weight:600;
                                        margin:0.3rem 0 0.1rem; line-height:1.3;">
                                {s['title'][:55]}{'…' if len(s['title'])>55 else ''}
                            </div>
                            <div style="font-size:0.72rem; color:#6366f1; font-weight:700;">
                                👁 {s['view_count']:,}
                            </div>
                            <div style="font-size:0.68rem; color:#4b5563; margin-bottom:0.5rem;">
                                ❤️ {s.get('like_count',0):,} · ⏱ {s.get('duration_seconds',0)}s
                            </div>
                        </div>
                    </a>
                    """, unsafe_allow_html=True)

        # ── Data table ─────────────────────────────────────────────────────────
        st.subheader("📋 Ranked Table")
        table_df = pd.DataFrame([{
            "Rank":      i + 1,
            "Title":     s["title"][:60],
            "Views":     s["view_count"],
            "Likes":     s.get("like_count", 0),
            "Duration":  f"{s.get('duration_seconds',0)}s",
            "Published": (s.get("published_at") or "")[:10],
            "URL":       s["url"],
        } for i, s in enumerate(shorts)])

        st.dataframe(
            table_df.drop(columns=["URL"]),
            use_container_width=True,
            hide_index=True,
            column_config={
                "Views": st.column_config.ProgressColumn(
                    "Views", min_value=0,
                    max_value=int(table_df["Views"].max()), format="%d",
                )
            }
        )

        # ── Hand-off to Pattern Finder ─────────────────────────────────────────
        urls = [s["url"] for s in shorts]
        st.session_state["shorts_urls"] = urls
        st.session_state["shorts_channel"] = ch_name

        st.success(f"✅ {len(shorts)} Shorts loaded. Click **Pattern Finder** in the sidebar to analyse them.")
        progress.progress(100, text="Done!")

    except Exception as e:
        st.error(f"Error: {e}")
        progress.empty()