import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st

st.set_page_config(
    page_title="AI Content Intelligence",
    page_icon="🎙️",
    layout="wide",
    initial_sidebar_state="expanded",
)

from app.styles import inject_css
from app.openai_settings import render_openai_key_section
inject_css()

# ── Sidebar branding ──────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="text-align:center; padding: 1rem 0 1.5rem;">
        <div style="font-size:2.8rem;">🎙️</div>
        <div style="font-size:1.6rem; font-weight:700; background:linear-gradient(135deg,#6366f1,#8b5cf6);
                    -webkit-background-clip:text; -webkit-text-fill-color:transparent;">AI CONTENT</div>
        <div style="font-size:0.75rem; color:#94a3b8; letter-spacing:2px; margin-top:2px;">INTELLIGENCE PLATFORM</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("""
    <div style="color:#64748b; font-size:0.8rem; padding:0 0.5rem;">
    <b style="color:#94a3b8;">TOOLS</b><br><br>
    🔍 <b>Market Research</b> — discover top podcasts<br><br>
    📊 <b>Shorts Scraper</b> — rank YouTube Shorts<br><br>
    🎙️ <b>Pattern Finder</b> — analyse content formats<br><br>
    🎣 <b>Hook Finder</b> — classify podcast hooks<br><br>
    ✨ <b>Creativity</b> — e-commerce & animation
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    render_openai_key_section()

    st.markdown("""
    <div style="color:#4b5563; font-size:0.72rem; text-align:center;">
        Powered by YouTube Data API v3<br>+ OpenAI Whisper & GPT-4o-mini
    </div>
    """, unsafe_allow_html=True)

# ── Home page ─────────────────────────────────────────────────────────────────
st.markdown("""
<div style="text-align:center; padding: 3rem 0 2rem;">
    <div style="font-size:3.5rem;">🎙️</div>
    <h1 style="font-size:2.8rem; font-weight:800;
               background:linear-gradient(135deg,#6366f1,#8b5cf6,#ec4899);
               -webkit-background-clip:text; -webkit-text-fill-color:transparent; margin:0.5rem 0;">
        Tanmay
    </h1>
    <p style="color:#94a3b8; font-size:1.1rem; max-width:600px; margin:0 auto;">
        AI-powered content intelligence — research podcasts, scrape top Shorts,
        transcribe & analyse hooks, and generate creative briefs.
    </p>
</div>
""", unsafe_allow_html=True)

# Feature grid
c1, c2, c3, c4, c5 = st.columns(5)
cards = [
    ("🔍", "Market Research", "Discover & rank top podcasts by region"),
    ("📊", "Shorts Scraper", "Extract top-performing YouTube Shorts"),
    ("🎙️", "Pattern Finder", "Transcribe & find repeatable formats"),
    ("🎣", "Hook Finder", "Classify podcast hooks into 7 patterns"),
    ("✨", "Creativity", "E-commerce storefront & AI animation"),
]
for col, (icon, title, desc) in zip([c1, c2, c3, c4, c5], cards):
    with col:
        st.markdown(f"""
        <div class="gargi-card" style="text-align:center; min-height:150px;">
            <div style="font-size:2rem;">{icon}</div>
            <div style="font-weight:700; color:#e2e8f0; margin:0.5rem 0 0.3rem;">{title}</div>
            <div style="font-size:0.78rem; color:#64748b;">{desc}</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("""
<div style="text-align:center; color:#4b5563; font-size:0.85rem; margin-top:2rem;">
    ← Select a tool from the sidebar to get started
</div>
""", unsafe_allow_html=True)
