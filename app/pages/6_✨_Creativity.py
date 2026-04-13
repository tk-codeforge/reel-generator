import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import streamlit as st

st.set_page_config(page_title="Creativity Tools", page_icon="✨", layout="wide")
from app.styles import inject_css
from app.openai_settings import render_openai_key_section
from services.openai_client import get_openai_client

inject_css()
render_openai_key_section()

# ── Header ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div style="margin-bottom:2rem;">
    <h1 style="font-size:2rem; font-weight:800;
               background:linear-gradient(135deg,#f59e0b,#ec4899,#8b5cf6);
               -webkit-background-clip:text; -webkit-text-fill-color:transparent; margin:0;">
        ✨ Creativity Tools
    </h1>
    <p style="color:#64748b; margin:0.3rem 0 0;">
        E-commerce storefront, animation concepts, and AI-generated motion briefs
    </p>
</div>
""", unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["🛒  E-commerce Storefront", "🎬  Basic Animation Generator", "🤖  AI Animation Generator"])

# ─────────────────────────────────────────────────────────────────────────────────
# TAB 1: E-Commerce Storefront
# ─────────────────────────────────────────────────────────────────────────────────
SAMPLE_ASSETS = [
    {"title": "Wealth Gap Visualiser",  "tags": ["data-viz","money","infographic"], "price": "$49", "preview": "📊"},
    {"title": "Startup Timeline Kit",   "tags": ["timeline","startup","motion"],    "price": "$79", "preview": "🚀"},
    {"title": "Podcast Wave Overlay",   "tags": ["audio","podcast","overlay"],      "price": "$29", "preview": "🎙️"},
    {"title": "Neon City Loop",         "tags": ["loop","urban","ambient"],         "price": "$59", "preview": "🌆"},
    {"title": "Kinetic Typography Pack","tags": ["text","kinetic","bold"],          "price": "$99", "preview": "✍️"},
    {"title": "Abstract Flow Morphs",   "tags": ["abstract","organic","flow"],      "price": "$69", "preview": "🌊"},
]

with tab1:
    st.markdown("""
    <div class="gargi-card" style="margin-bottom:1.5rem; text-align:center; padding:2rem;">
        <div style="font-size:1.5rem; font-weight:800; color:#e2e8f0;">Context-Aware Deep Search</div>
        <div style="color:#64748b; margin-top:0.5rem;">Search by intent, not keywords</div>
    </div>
    """, unsafe_allow_html=True)

    search = st.text_input("🔍 Search by intent",
                           placeholder="visualise the wealth gap  /  podcast intro with energy  /  dark ambient loop")

    if st.button("Search Assets", key="asset_search"):
        if search.strip():
            # Use GPT to match intent to asset titles
            with st.spinner("Finding best matches…"):
                try:
                    resp = get_openai_client().chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[
                            {"role": "system", "content":
                             "You are a creative asset search engine. Given a natural language search intent and a list of asset titles, "
                             "return the titles that best match the intent, ordered by relevance. "
                             "Respond ONLY with a JSON array of matching title strings."},
                            {"role": "user", "content":
                             f"Intent: {search}\n\nAssets: {[a['title'] for a in SAMPLE_ASSETS]}"}
                        ],
                        response_format={"type": "json_object"},
                        temperature=0.3,
                    )
                    import json
                    raw = resp.choices[0].message.content
                    # Try to extract array from JSON object
                    data = json.loads(raw)
                    matches = next(iter(data.values())) if isinstance(data, dict) else data
                    filtered = [a for a in SAMPLE_ASSETS if a["title"] in matches]
                    if not filtered:
                        filtered = SAMPLE_ASSETS
                except Exception:
                    filtered = SAMPLE_ASSETS
        else:
            filtered = SAMPLE_ASSETS
    else:
        filtered = SAMPLE_ASSETS

    cols_per_row = 3
    for row in range(0, len(filtered), cols_per_row):
        row_assets = filtered[row:row + cols_per_row]
        cols = st.columns(cols_per_row)
        for col, asset in zip(cols, row_assets):
            with col:
                tag_pills = " ".join(
                    f'<span class="topic-pill">{t}</span>' for t in asset["tags"]
                )
                st.markdown(f"""
                <div class="gargi-card" style="text-align:center; min-height:220px;">
                    <div style="font-size:3rem; margin-bottom:0.5rem;">{asset['preview']}</div>
                    <div style="font-weight:700; color:#e2e8f0; margin-bottom:0.4rem;">{asset['title']}</div>
                    <div style="margin-bottom:0.6rem;">{tag_pills}</div>
                    <div style="font-size:1.1rem; font-weight:800;
                                background:linear-gradient(135deg,#6366f1,#8b5cf6);
                                -webkit-background-clip:text; -webkit-text-fill-color:transparent;">
                        {asset['price']}
                    </div>
                </div>
                """, unsafe_allow_html=True)
                st.button("Preview & Buy", key=f"buy_{asset['title']}", use_container_width=True)

# ─────────────────────────────────────────────────────────────────────────────────
# TAB 2: Basic Animation Generator
# ─────────────────────────────────────────────────────────────────────────────────
with tab2:
    st.markdown("""
    <div class="gargi-card" style="margin-bottom:1.5rem; text-align:center;">
        <div style="font-size:1.3rem; font-weight:700; color:#e2e8f0;">Basic Animation Generator</div>
        <div style="color:#64748b; margin-top:0.3rem;">Describe your scene and get a motion concept</div>
    </div>
    """, unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        style = st.selectbox("Animation Style", [
            "Kinetic Typography", "Abstract Flow", "Data Visualisation",
            "Liquid Motion", "Geometric", "Glitch / Cyberpunk",
            "Minimal Clean", "Retro Neon",
        ])
        duration = st.slider("Duration (seconds)", 3, 60, 15)
        aspect   = st.selectbox("Aspect Ratio", ["9:16 (Shorts/Reels)", "16:9 (Video)", "1:1 (Square)"])
    with c2:
        prompt = st.text_area("Scene Description", height=120,
                              placeholder="A bar chart rising from zero showing GDP growth across African nations, ending with a bold title card")
        colour_palette = st.text_input("Colour Palette", placeholder="e.g. indigo, violet, electric pink")

    if st.button("🎬 Generate Concept", use_container_width=True, key="basic_gen"):
        if prompt.strip():
            with st.spinner("Generating animation concept…"):
                try:
                    full_prompt = (
                        f"Style: {style}\n"
                        f"Duration: {duration}s\n"
                        f"Aspect ratio: {aspect}\n"
                        f"Colours: {colour_palette or 'not specified'}\n"
                        f"Scene: {prompt}"
                    )
                    resp = get_openai_client().chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[
                            {"role": "system", "content":
                             "You are a senior motion designer. Given parameters, write a concise motion design brief "
                             "covering: (1) Scene breakdown by seconds, (2) Typography choices, "
                             "(3) Key easing/animation principles, (4) Sound design hint. Format with markdown."},
                            {"role": "user", "content": full_prompt}
                        ],
                        temperature=0.7,
                    )
                    brief = resp.choices[0].message.content
                    st.markdown(f"""
                    <div class="gargi-card">
                        <div style="font-weight:700; color:#a5b4fc; margin-bottom:0.7rem;">
                            🎬 Motion Brief — {style} · {duration}s · {aspect}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    st.markdown(brief)
                except Exception as e:
                    st.error(f"Generation failed: {e}")
        else:
            st.warning("Please enter a scene description.")

# ─────────────────────────────────────────────────────────────────────────────────
# TAB 3: AI Animation Generator
# ─────────────────────────────────────────────────────────────────────────────────
with tab3:
    st.markdown("""
    <div class="gargi-card" style="margin-bottom:1.5rem; text-align:center;">
        <div style="font-size:1.3rem; font-weight:700; color:#e2e8f0;">AI Animation Generator</div>
        <div style="color:#64748b; margin-top:0.3rem;">
            Text-to-animation briefs · Style transfer · Brand-consistent motion identities
        </div>
    </div>
    """, unsafe_allow_html=True)

    ai_tab1, ai_tab2, ai_tab3 = st.tabs(["📝 Text-to-Video", "🎨 Style Transfer", "🏷️ Brand Identity"])

    with ai_tab1:
        ai_prompt = st.text_area("Describe your animation",
                                 height=120,
                                 placeholder="A glowing neural network expanding outward, each node firing in sequence, then collapsing into a single brand logo")
        col1, col2 = st.columns(2)
        with col1:
            ai_style = st.selectbox("Output Style", [
                "Photorealistic", "Cel Animation", "Motion Graphics",
                "3D Abstract", "Minimalist", "Synthwave / Retro"
            ], key="ai_style")
        with col2:
            ai_fps = st.selectbox("Frame Rate", ["24fps", "30fps", "60fps"])

        if st.button("🤖 Generate Animation Brief", use_container_width=True, key="ai_gen"):
            if ai_prompt.strip():
                with st.spinner("GPT-4o-mini generating your animation brief…"):
                    try:
                        resp = get_openai_client().chat.completions.create(
                            model="gpt-4o-mini",
                            messages=[
                                {"role": "system", "content":
                                 "You are an AI animation director. Generate a detailed animation brief including: "
                                 "1. Shot-by-shot storyboard description (numbered), 2. Camera movement notes, "
                                 "3. Particle/FX recommendations, 4. Colour grading direction, "
                                 "5. Suggested music tempo/BPM and mood. Use markdown formatting."},
                                {"role": "user", "content":
                                 f"Style: {ai_style}\nFPS: {ai_fps}\nPrompt: {ai_prompt}"}
                            ],
                            temperature=0.8,
                        )
                        brief = resp.choices[0].message.content

                        st.markdown(f"""
                        <div class="gargi-card">
                            <div style="font-weight:700; color:#a5b4fc; margin-bottom:0.7rem;">
                                🎬 AI Generated Brief — {ai_style} · {ai_fps}
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                        st.markdown(brief)

                    except Exception as e:
                        st.error(f"Generation failed: {e}")
            else:
                st.warning("Please enter an animation description.")

    with ai_tab2:
        st.markdown("""
        <div class="gargi-card">
            <div style="font-weight:700; color:#e2e8f0; margin-bottom:0.5rem;">Style Transfer</div>
            <div style="color:#64748b; font-size:0.85rem;">
                Describe a reference style and a target scene to get a mixed motion style brief.
            </div>
        </div>
        """, unsafe_allow_html=True)
        ref_style = st.text_area("Reference Style", height=80,
                                 placeholder="e.g. Like Billie Eilish's 'Bad Guy' MV — dark, low-key, stark negative space, sudden cuts")
        target_scene = st.text_area("Target Scene", height=80,
                                    placeholder="A product reveal for noise-cancelling headphones in a busy café")
        if st.button("🎨 Generate Style Transfer Brief", use_container_width=True, key="style_transfer"):
            if ref_style.strip() and target_scene.strip():
                with st.spinner("Mixing styles…"):
                    try:
                        resp = get_openai_client().chat.completions.create(
                            model="gpt-4o-mini",
                            messages=[
                                {"role": "system", "content":
                                 "You are a creative director specialising in style transfer for motion design. "
                                 "Apply the visual style of the reference to the target scene. "
                                 "Output: visual style notes, pacing, colour palette, typography mood, and editing style."},
                                {"role": "user", "content":
                                 f"Reference style:\n{ref_style}\n\nTarget scene:\n{target_scene}"}
                            ],
                            temperature=0.75,
                        )
                        st.markdown(resp.choices[0].message.content)
                    except Exception as e:
                        st.error(f"Failed: {e}")
            else:
                st.warning("Fill in both fields.")

    with ai_tab3:
        st.markdown("""
        <div class="gargi-card">
            <div style="font-weight:700; color:#e2e8f0; margin-bottom:0.5rem;">Brand Motion Identity</div>
            <div style="color:#64748b; font-size:0.85rem;">
                Define your brand and get a complete motion identity system.
            </div>
        </div>
        """, unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            brand_name = st.text_input("Brand Name", placeholder="e.g. Acme Studio")
            brand_values = st.text_input("Brand Values", placeholder="e.g. intelligence, warmth, momentum")
        with c2:
            brand_colors = st.text_input("Primary Colours", placeholder="e.g. deep violet, electric indigo, off-white")
            brand_audience = st.text_input("Audience", placeholder="e.g. African tech founders aged 25-40")

        if st.button("🏷️ Generate Motion Identity", use_container_width=True, key="brand_id"):
            if brand_name.strip():
                with st.spinner("Building brand motion identity…"):
                    try:
                        resp = get_openai_client().chat.completions.create(
                            model="gpt-4o-mini",
                            messages=[
                                {"role": "system", "content":
                                 "You are a brand motion designer. Create a complete motion identity system covering: "
                                 "1. Logo animation style, 2. Transition style and timing, 3. Text animation rules, "
                                 "4. Colour usage in motion, 5. Sound logo concept, 6. Do's and don'ts. "
                                 "Format cleanly with markdown headers."},
                                {"role": "user", "content":
                                 f"Brand: {brand_name}\nValues: {brand_values}\n"
                                 f"Colours: {brand_colors}\nAudience: {brand_audience}"}
                            ],
                            temperature=0.7,
                        )
                        st.markdown(resp.choices[0].message.content)
                    except Exception as e:
                        st.error(f"Failed: {e}")
            else:
                st.warning("Please enter a brand name.")
