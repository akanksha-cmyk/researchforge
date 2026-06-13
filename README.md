# FieldGuide

**Navigate your future research community.**

Perplexity for academic careers — a multi-layer AI research infrastructure.

## Sponsor Architecture (for judges)

Each sponsor powers a **distinct pipeline stage**:

| Sponsor | System Role | What It Does |
|---------|-------------|--------------|
| **Bright Data** | Live Academic Web Layer | Scrapes Google Scholar, OpenAlex, Semantic Scholar for live papers |
| **Kimi** | Field Intelligence Engine | Clusters topics, finds gaps, generates future directions |
| **TokenRouter** | Model Orchestration Layer | Routes field synthesis, email generation, summarization to optimal models |
| **Nosana** | Embedding + Graph Compute | Distributed embedding computation for research landscape graph |
| **Daytona** | Secure Agent Runtime | Break-in research agent runs in isolated sandbox |
| **SenseNova** | Multimodal Insight Layer | Generates structured visual field maps |
| **VideoDB** | Academic Talk Intelligence | Converts conference talks into structured research signals |

## Quick start

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

## Demo script (60 seconds)

1. Open app → expand **FieldGuide Architecture** (shows all 7 sponsors)
2. Search **griefbots** → watch pipeline status (each sponsor lights up)
3. Show **SenseNova Visual Field Map** + **Nosana Research Landscape** graph
4. Show **VideoDB Conference Talk Insights**
5. Click **Run break-in agent (Daytona sandbox)** → cold emails
6. Point to footer: *Built using Bright Data · Kimi · TokenRouter · Nosana · Daytona · SenseNova · VideoDB*

## Environment

```env
BRIGHTDATA_API_KEY=...
BRIGHTDATA_ZONE=serp_api1        # optional, for Google Scholar scraping
KIMI_API_KEY=...
TOKENROUTER_API_KEY=...
NOSANA_API_KEY=...
NOSANA_EMBED_URL=...             # optional, for GPU embeddings
DAYTONA_API_KEY=...
SENSENOVA_API_KEY=...
VIDEODB_API_KEY=...
```

App works without valid keys via intelligent fallbacks — but sponsor layers remain visible in UI.

## What to say to judges

> "FieldGuide isn't a search tool — it's a full-stack AI research infrastructure. Bright Data ingests live academic data. Kimi synthesizes field intelligence. TokenRouter orchestrates models per stage. Nosana computes embeddings for our graph. SenseNova generates visual field maps. VideoDB extracts signals from conference talks. And when you want to break into a field, our research agent runs in a secure Daytona sandbox."
