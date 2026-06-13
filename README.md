# FieldGuide

**Navigate your future research community.**

Perplexity for academic careers — search any research field and get a living map of the people, trends, gaps, and concrete steps to break in.

## The problem

Researchers don't struggle to find papers anymore. They struggle to answer:

- What's actually happening in this field?
- Who are the important people and labs?
- What gaps are worth working on?
- How do I contact researchers and get involved?

FieldGuide turns a single search query into field intelligence, an interactive research landscape, and an actionable break-in plan.

## What it does

Search a topic (e.g. *griefbots*, *human-AI collaboration*, *computational social science*) and FieldGuide returns:

- **Field overview** — synthesis of where the field is headed
- **Trending topics** — what's gaining momentum right now
- **Research landscape graph** — interactive node map of papers, themes, and connections
- **Key researchers & labs** — who to follow and where to apply
- **Research gaps & future directions** — open problems worth pursuing
- **Conference talk insights** — signals extracted from academic talks
- **Break-in plan** — cold email drafts, collaborators, conferences, and a step-by-step action plan

## Sponsor integrations

Each sponsor powers a distinct stage in the pipeline:

| Sponsor | Role | Integration |
|---------|------|-------------|
| **Bright Data** | Live Academic Web Layer | Ingests papers from Google Scholar, OpenAlex, and Semantic Scholar |
| **Kimi** | Field Intelligence Engine | Clusters topics, surfaces gaps, and generates future directions |
| **TokenRouter** | Model Orchestration | Routes synthesis, email generation, and summarization to optimal models |
| **Nosana** | Embedding + Graph Compute | Computes embeddings for the research landscape graph |
| **Daytona** | Secure Agent Runtime | Runs the break-in research agent in an isolated sandbox |
| **SenseNova** | Multimodal Insight Layer | Generates structured visual field maps |
| **VideoDB** | Academic Talk Intelligence | Extracts structured signals from conference talks |

## Tech stack

- **Frontend:** Streamlit (light glassmorphic dashboard)
- **Graph:** pyvis / vis-network interactive node graph
- **LLM:** Kimi via TokenRouter with local fallbacks
- **Agent runtime:** Daytona sandbox
- **Data:** OpenAlex → Semantic Scholar → Bright Data scraping pipeline

## Quick start

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # add your API keys
streamlit run app.py
```

Open `http://localhost:8501` and search any research field.

## Environment variables

```env
BRIGHTDATA_API_KEY=...
BRIGHTDATA_ZONE=scraping_browser1   # optional
KIMI_API_KEY=...
TOKENROUTER_API_KEY=...
NOSANA_API_KEY=...
NOSANA_EMBED_URL=...                # optional
DAYTONA_API_KEY=...
SENSENOVA_API_KEY=...
VIDEODB_API_KEY=...
```

The app includes intelligent fallbacks when keys are unavailable, so you can explore the UI without every integration configured.

## Project structure

```
fieldguide/
  pipeline.py          # orchestrates all sponsor stages
  graph.py             # interactive research landscape graph
  llm.py               # Kimi + TokenRouter routing
  papers.py            # paper search pipeline
  sponsors/            # Bright Data, Kimi, TokenRouter, Nosana,
                        # Daytona, SenseNova, VideoDB
app.py                 # Streamlit dashboard
scripts/check_sponsors.py
```

## Built with

Bright Data · Kimi · TokenRouter · Nosana · Daytona · SenseNova · VideoDB
