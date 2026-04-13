<<<<<<< HEAD
# AI Content Intelligence Platform 🎙️📊

> A YouTube-focused market research, content analysis, and transcription platform powered by the YouTube Data API v3 and OpenAI.

---

## Overview

A modular Python backend with a Streamlit frontend providing six integrated tools:

| # | Tool | Purpose |
|---|------|---------|
| 1 | **Market Research** | Rank podcasts by region; **Generate reel insights** (Whisper + GPT hooks) on the same page |
| 2 | **Shorts Scraper** | Extract top-performing YouTube Shorts from any channel |
| 3.1 | **Pattern Finder** | Transcribe Shorts and identify repeatable content formats |
| 3.2 | **Hook Finder** | Classify podcast opening hooks into 7 proven patterns |
| 4 | **Creativity Tools** | E-commerce storefront, basic & AI animation generator |
| 5 | **Reel Generator** | Same pipeline as Market Research: long-form URL → Whisper chunks → GPT 15-second hook ideas (standalone page) |

---

## Project Structure

```
d:\Gargi\
├── app/                        # Streamlit frontend
│   ├── app.py                  # Entry point & home page
│   ├── styles.py               # Shared CSS + hook constants
│   ├── openai_settings.py      # Sidebar OpenAI key (optional override of .env)
│   └── pages/
│       ├── 1_🔍_Market_Research.py
│       ├── 2_📊_Shorts_Scraper.py
│       ├── 3_🎙️_Pattern_Finder.py
│       ├── 4_🎣_Hook_Finder.py
│       ├── 5_✨_Creativity.py
│       └── 6_🎬_Reel_Generator.py
├── api/                        # FastAPI routes (optional REST layer)
│   └── routes/
│       ├── research.py
│       ├── scraper.py
│       ├── transcription.py
│       └── hook_analysis.py
├── services/
│   ├── openai_client.py        # Lazy OpenAI client (key from .env or Streamlit sidebar)
│   ├── youtube/
│   │   ├── search.py           # Podcast channel search
│   │   ├── channel.py          # Channel metadata
│   │   ├── shorts.py           # Top Shorts fetcher
│   │   └── filters.py          # News/inactive channel filters
│   ├── transcription/
│   │   ├── downloader.py       # yt-dlp audio downloader
│   │   ├── chunker.py          # ffmpeg-based audio splitter
│   │   └── whisper_client.py   # OpenAI Whisper transcription
│   └── analysis/
│       ├── hook_classifier.py  # GPT-4o-mini hook classification
│       ├── pattern_finder.py   # Multi-video pattern analysis
│       ├── report_generator.py # Markdown report writer
│       ├── reel_generator.py   # GPT extracts ~15s clip text from transcript chunks
│       └── reel_pipeline.py    # Download → Whisper chunks → optional GPT reels
├── models/                     # Pydantic data models
├── utils/                      # Logger, cache, rate limiter
├── outputs/                    # Generated reports, transcripts, audio
├── config.py                   # Loads API keys from .env
├── main.py                     # FastAPI app entry point
├── requirements.txt
└── .env                        # API keys (not committed)
```

---

## Setup

### 1. Prerequisites

- Python 3.10+
- [ffmpeg](https://ffmpeg.org/download.html) installed and on `PATH`
- [yt-dlp](https://github.com/yt-dlp/yt-dlp) (installed via pip)

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure API Keys

Create a `.env` file in the project root:

```env
YOUTUBE_API_KEY=AIza...          # YouTube Data API v3 key
OPENAI_API_KEY=sk-proj-...       # OpenAI API key (also accepts openai_api_key)
```

> Get a YouTube Data API v3 key from [Google Cloud Console](https://console.cloud.google.com/).  
> Get an OpenAI key from [platform.openai.com](https://platform.openai.com/).

**Streamlit:** You can also paste the OpenAI key in the sidebar under **OpenAI API key** (optional override). The app reads the key at runtime so Whisper and GPT calls pick it up without restarting.

---

## Running the App

### Streamlit Frontend (recommended)

```bash
cd d:\Gargi
python -m streamlit run app/app.py
```

Visit `http://localhost:8501`

### FastAPI Backend (optional REST API)

```bash
uvicorn main:app --reload
```

Visit `http://localhost:8000/docs` for the interactive Swagger UI.

---

## Tools

### 1. 🔍 Market Research
Search for top business podcasts on YouTube filtered by region. Excludes news broadcasters and inactive channels. Outputs a ranked table with subscriber bars and a downloadable Markdown report.

**Reel insights (same page):** After results load, select a top video and click **Generate reel insights** — the app downloads audio (yt-dlp), transcribes ~10-minute segments with **OpenAI Whisper** (`whisper-1`), shows each segment’s text, then uses **GPT-4o-mini** to suggest ~15-second Short/Reel hooks. Re-running **Market Research** clears the last on-page result.

### 2. 📊 Shorts Scraper
Enter any YouTube channel URL or ID to fetch the top 50 Shorts ranked by view count. Results shown as a thumbnail grid, Plotly bar chart, and ranked data table. One-click hand-off to Pattern Finder.

### 3.1 🎙️ Pattern Finder (Shorts)
Paste YouTube Shorts URLs (or send from the Scraper). Downloads audio, transcribes via Whisper, then uses GPT-4o-mini to extract:
- Common topics & themes
- Dominant hook types
- Repeatable content formats
- Top-performing content structure

### 3.2 🎣 Hook Finder (Podcasts)
Paste podcast episode URLs. Downloads the first 60 seconds, transcribes, then classifies the hook:

| Hook Type | Description |
|-----------|-------------|
| Big Promise | Bold claim that triggers curiosity |
| I Was Wrong | Vulnerability + belief reversal |
| Shock / Controversy | Polarising statement |
| Insider Secret | Exclusive access framing |
| Tension Setup | Conflict introduced early |
| Mini-Story Cold Open | Starts mid-drama |
| Counterintuitive / Weird | Breaks expectations |

### 4. ✨ Creativity Tools
- **E-commerce Storefront** — Intent-based search for premium video assets (GPT-powered matching)
- **Basic Animation Generator** — Style picker + prompt → motion concept brief
- **AI Animation Generator** — Text-to-video brief, style transfer, and brand motion identity generator

### 5. 🎬 Reel Generator
Enter a long-form YouTube URL (optional: pre-filled from Market Research session state). Same backend as Market Research: download → Whisper chunk transcription → GPT ~15-second hook ideas. Use this page when you want the pipeline without running podcast search first.

---

## API Endpoints (FastAPI)

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/research/podcasts` | Search & rank YouTube podcasts |
| `GET` | `/research/report` | Generate Markdown report |
| `GET` | `/scraper/top-shorts` | Fetch top Shorts from a channel |
| `POST` | `/transcription/transcribe` | Transcribe a YouTube URL |
| `POST` | `/transcription/analyze-patterns` | Find patterns across Shorts |
| `POST` | `/hooks/classify` | Classify a podcast hook |

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Streamlit |
| Backend | FastAPI + Python async |
| YouTube Data | YouTube Data API v3 |
| Transcription | OpenAI Whisper (`whisper-1`) |
| AI Analysis | OpenAI GPT-4o-mini |
| Audio Download | yt-dlp |
| Audio Processing | ffmpeg (via subprocess) |
| Data Validation | Pydantic v2 |
| Charts | Plotly |

---

## Notes

- Audio files > 24 MB are automatically split with ffmpeg before sending to Whisper.
- Transcripts and audio are cached in `outputs/` to avoid re-downloading.
- YouTube API quota: each search costs ~100 units. Default daily quota is 10,000 units.
- Base API keys load from `.env` at import (`load_dotenv(override=True)`). Clearing the sidebar OpenAI field reloads `.env` into the environment for that session.
=======
# reel-generator
>>>>>>> 4965db744c29290c3fdcf63edf07efc6e726d3d2
