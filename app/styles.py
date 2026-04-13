def inject_css():
    import streamlit as st
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    /* ── Font ──────────────────────────────────────────────────────────────── */
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    /* ── Buttons ───────────────────────────────────────────────────────────── */
    .stButton > button {
        background: linear-gradient(135deg, #6366f1, #8b5cf6);
        color: white !important;
        border: none;
        border-radius: 10px;
        font-weight: 600;
        padding: 0.5rem 1.5rem;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(99,102,241,0.3);
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(99,102,241,0.5);
        color: white !important;
    }

    /* ── Inputs & Text Areas ───────────────────────────────────────────────── */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea {
        background: var(--background-color) !important;
        border: 1px solid rgba(99,102,241,0.5) !important;
        border-radius: 10px !important;
        color: var(--text-color) !important;
        font-weight: 500 !important;
    }

    /* ── Selectbox trigger ─────────────────────────────────────────────────── */
    .stSelectbox > div > div {
        background: var(--background-color) !important;
        border: 1px solid rgba(99,102,241,0.5) !important;
        border-radius: 10px !important;
        color: var(--text-color) !important;
    }
    .stSelectbox [data-baseweb="select"] > div,
    .stSelectbox [data-baseweb="select"] span {
        background: var(--background-color) !important;
        color: var(--text-color) !important;
    }

    /* ── Selectbox dropdown popover ────────────────────────────────────────── */
    div[data-baseweb="popover"],
    div[data-baseweb="popover"] > div,
    ul[data-baseweb="menu"] {
        background: var(--secondary-background-color) !important;
        border: 1px solid rgba(99,102,241,0.3) !important;
        border-radius: 10px !important;
    }
    li[role="option"] {
        background: transparent !important;
        color: var(--text-color) !important;
    }
    li[role="option"]:hover,
    li[aria-selected="true"] {
        background: rgba(99,102,241,0.15) !important;
        color: var(--text-color) !important;
    }

    /* ── Sidebar ───────────────────────────────────────────────────────────── */
    [data-testid="stSidebar"] {
        border-right: 1px solid rgba(99,102,241,0.2);
    }

    /* ── Metric cards ──────────────────────────────────────────────────────── */
    [data-testid="metric-container"] {
        background: rgba(99,102,241,0.08);
        border: 1px solid rgba(99,102,241,0.2);
        border-radius: 12px;
        padding: 1rem;
    }

    /* ── Dataframe ─────────────────────────────────────────────────────────── */
    [data-testid="stDataFrame"] {
        border-radius: 12px;
        overflow: hidden;
    }

    /* ── Expander ──────────────────────────────────────────────────────────── */
    .streamlit-expanderHeader {
        background: rgba(99,102,241,0.1) !important;
        border-radius: 10px !important;
        font-weight: 600 !important;
    }

    /* ── Tabs ──────────────────────────────────────────────────────────────── */
    .stTabs [data-baseweb="tab-list"] {
        background: rgba(99,102,241,0.06);
        border-radius: 12px;
        padding: 4px;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 10px;
        font-weight: 500;
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #6366f1, #8b5cf6) !important;
        color: white !important;
    }

    /* ── Progress bar ──────────────────────────────────────────────────────── */
    .stProgress > div > div > div {
        background: linear-gradient(90deg, #6366f1, #8b5cf6) !important;
    }

    /* ── Alerts ────────────────────────────────────────────────────────────── */
    .stSuccess, .stInfo, .stWarning, .stError {
        border-radius: 10px;
    }

    /* ── Custom card ───────────────────────────────────────────────────────── */
    .gargi-card {
        background: var(--secondary-background-color);
        border: 1px solid rgba(99,102,241,0.2);
        border-radius: 16px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        transition: border-color 0.3s;
    }
    .gargi-card:hover {
        border-color: rgba(99,102,241,0.5);
    }

    /* ── Badge ─────────────────────────────────────────────────────────────── */
    .hook-badge {
        display: inline-block;
        background: linear-gradient(135deg, #6366f1, #8b5cf6);
        color: white !important;
        padding: 4px 14px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        letter-spacing: 0.5px;
    }

    /* ── Pill ──────────────────────────────────────────────────────────────── */
    .topic-pill {
        display: inline-block;
        background: rgba(99,102,241,0.15);
        border: 1px solid rgba(99,102,241,0.3);
        padding: 3px 12px;
        border-radius: 20px;
        font-size: 0.8rem;
        margin: 2px;
    }

    /* ── Scrollbar ─────────────────────────────────────────────────────────── */
    ::-webkit-scrollbar { width: 6px; }
    ::-webkit-scrollbar-track { background: transparent; }
    ::-webkit-scrollbar-thumb {
        background: rgba(99,102,241,0.4);
        border-radius: 3px;
    }


    /* ════════════════════════════════════════════════════════════════════════
       DARK THEME  (Streamlit sets data-theme="dark" on <html>)
       ════════════════════════════════════════════════════════════════════════ */
    html[data-theme="dark"] .gargi-card,
    [data-theme="dark"] .gargi-card {
        background: rgba(255,255,255,0.05);
        border-color: rgba(99,102,241,0.25);
    }

    /* Inline-style colours used inside st.markdown() HTML blocks — dark theme */
    html[data-theme="dark"] [style*="color:#64748b"],
    html[data-theme="dark"] [style*="color: #64748b"] { color: #94a3b8 !important; }

    html[data-theme="dark"] [style*="color:#94a3b8"],
    html[data-theme="dark"] [style*="color: #94a3b8"] { color: #94a3b8 !important; }

    html[data-theme="dark"] [style*="color:#e2e8f0"],
    html[data-theme="dark"] [style*="color: #e2e8f0"] { color: #e2e8f0 !important; }

    html[data-theme="dark"] [style*="color:#a5b4fc"],
    html[data-theme="dark"] [style*="color: #a5b4fc"] { color: #a5b4fc !important; }

    html[data-theme="dark"] [style*="color:#4b5563"],
    html[data-theme="dark"] [style*="color: #4b5563"] { color: #9ca3af !important; }

    html[data-theme="dark"] .topic-pill { color: #a5b4fc !important; }
    html[data-theme="dark"] .streamlit-expanderHeader { color: #a5b4fc !important; }


    /* ════════════════════════════════════════════════════════════════════════
       LIGHT THEME  (Streamlit sets data-theme="light" on <html>)
       All hardcoded light-grey inline colours are remapped to dark equivalents
       so they stay readable on the white background.
       ════════════════════════════════════════════════════════════════════════ */
    html[data-theme="light"] .gargi-card,
    [data-theme="light"] .gargi-card {
        background: #f8f7ff;
        border-color: rgba(99,102,241,0.3);
        box-shadow: 0 2px 8px rgba(99,102,241,0.08);
    }

    /* Very-light greys → dark readable greys */
    html[data-theme="light"] [style*="color:#e2e8f0"],
    html[data-theme="light"] [style*="color: #e2e8f0"] { color: #1e293b !important; }

    html[data-theme="light"] [style*="color:#94a3b8"],
    html[data-theme="light"] [style*="color: #94a3b8"] { color: #475569 !important; }

    html[data-theme="light"] [style*="color:#64748b"],
    html[data-theme="light"] [style*="color: #64748b"] { color: #334155 !important; }

    html[data-theme="light"] [style*="color:#4b5563"],
    html[data-theme="light"] [style*="color: #4b5563"] { color: #1f2937 !important; }

    /* Light purple → deeper purple that reads on white */
    html[data-theme="light"] [style*="color:#a5b4fc"],
    html[data-theme="light"] [style*="color: #a5b4fc"] { color: #4f46e5 !important; }

    /* Near-white → near-black */
    html[data-theme="light"] [style*="color:#f8fafc"],
    html[data-theme="light"] [style*="color: #f8fafc"] { color: #0f172a !important; }

    html[data-theme="light"] [style*="color:#cbd5e1"],
    html[data-theme="light"] [style*="color: #cbd5e1"] { color: #475569 !important; }

    /* Expander header */
    html[data-theme="light"] .streamlit-expanderHeader {
        color: #4f46e5 !important;
    }

    /* Topic pill */
    html[data-theme="light"] .topic-pill {
        color: #4f46e5 !important;
        background: rgba(99,102,241,0.1);
        border-color: rgba(99,102,241,0.4);
    }

    /* Sidebar subtle tint */
    html[data-theme="light"] [data-testid="stSidebar"] {
        background: #f5f4ff;
        border-right: 1px solid rgba(99,102,241,0.2);
    }

    /* Metric container on light */
    html[data-theme="light"] [data-testid="metric-container"] {
        background: rgba(99,102,241,0.06);
        border-color: rgba(99,102,241,0.25);
    }
    </style>
    """, unsafe_allow_html=True)


HOOK_COLORS = {
    "Big Promise":               "#6366f1",
    "I Was Wrong":               "#ec4899",
    "Shock / Controversy":       "#ef4444",
    "Insider Secret":            "#f59e0b",
    "Tension Setup":             "#10b981",
    "Mini-Story Cold Open":      "#3b82f6",
    "Counterintuitive / Weird":  "#8b5cf6",
}

HOOK_DESCRIPTIONS = {
    "Big Promise":             ("🚀", "Bold claim that triggers curiosity.",                   '"Here\'s the thing nobody tells you about X…"'),
    "I Was Wrong":             ("💔", "Vulnerability combined with belief reversal.",           '"I did everything wrong for 10 years until this…"'),
    "Shock / Controversy":     ("⚡", "Polarising statements that force attention.",            '"Founders shouldn\'t raise money until THIS moment…"'),
    "Insider Secret":          ("🔐", "Makes listeners feel they\'re gaining exclusive access.", '"Here\'s what VCs really look for — nobody tells founders this."'),
    "Tension Setup":           ("🎢", "Introduces conflict to keep viewers watching.",          '"We were running out of money… then one email changed everything."'),
    "Mini-Story Cold Open":    ("🎬", "Starts in the middle of a dramatic moment.",             '"He looked at me and said — fire half the team today."'),
    "Counterintuitive / Weird":("🌀", "Breaks expectations with surprising insight.",           '"The best founders are not logical — they\'re emotional."'),
}

