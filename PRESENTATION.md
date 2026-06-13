# FieldGuide — Demo Script & Presentation Collateral

Use this for your **video demo** and paste sections into **Gamma** to generate slides.

---

## Video demo script (~90 seconds)

**Setup before recording**
- Run `streamlit run app.py`
- Full screen the browser, sidebar visible
- Click **▶ Full demo (+ break-in plan)** once — let the pipeline run without touching anything

| Time | On screen | Narration |
|------|-----------|-----------|
| 0:00 | Landing hero + problem cards | "Researchers don't struggle to find papers anymore. They struggle to understand a field — who matters, where it's going, and how to break in." |
| 0:08 | Click **Full demo** | "FieldGuide is Perplexity for academic careers. One search, one pipeline." |
| 0:12 | Spinner: "Mapping field…" + sidebar | "Watch the sidebar — seven sponsors each power a distinct stage: Bright Data ingests live papers, Kimi synthesizes field intelligence, TokenRouter orchestrates models, Nosana builds the graph, SenseNova maps the field visually, VideoDB extracts conference talk signals." |
| 0:25 | Pipeline strip (green chips) + stat tiles | "In seconds we get papers, researchers, growth trends, and talk insights — all from live academic data." |
| 0:32 | Scroll to Field Overview + Trending Topics | "Kimi turns raw papers into a field overview and trending topics. Not just what was published — what's gaining momentum." |
| 0:40 | Visual Field Map + Research Landscape graph | "SenseNova generates a visual field map. Nosana computes embeddings for an interactive research landscape you can explore." |
| 0:48 | Key Researchers + Research Gaps | "Who are the key voices? What gaps are worth working on? What directions is the field moving toward?" |
| 0:55 | Conference Talk Insights | "VideoDB surfaces signals from conference talks — the conversations happening beyond papers." |
| 1:02 | Break-in section, agent running | "Now the part no other tool does: breaking in. Our agent runs in a secure Daytona sandbox." |
| 1:10 | Emails tab — cold email draft | "Personalized cold emails, ready to send." |
| 1:15 | Click **Send email** | "One click opens your mail client with the draft pre-filled." |
| 1:18 | Collaborators → Conferences → Action plan tabs | "Plus potential collaborators, upcoming conferences, and a step-by-step action plan." |
| 1:25 | Sidebar with all sponsors showing **live** | "Seven sponsors, one coherent pipeline — from search to cold email in under a minute." |
| 1:30 | End on hero tagline | "FieldGuide. Navigate your future research community." |

**Pro tips**
- Use **Full demo** not manual search — it auto-runs search + break-in plan
- If a sponsor shows "fallback" in sidebar, say: "Graceful fallbacks keep the demo running even when an API is unavailable"
- Pre-record once as backup in case live APIs are slow

---

## Gamma slide deck — copy/paste content

Paste the block below into Gamma. Suggested theme: **modern, light, blue/purple gradient**, font **Inter** or **Söhne**.

---

### Slide 1 — Title

**FieldGuide**
Navigate your future research community

Perplexity for academic careers
[Your name] · Hackathon Submission

---

### Slide 2 — The problem

**Finding papers is solved. Breaking into a field is not.**

Researchers still can't answer:
- Who are the important people and labs?
- What's actually happening in this field right now?
- What gaps are worth working on?
- How do I contact researchers and get involved?

Google Scholar gives you PDFs. FieldGuide gives you a map.

---

### Slide 3 — The solution

**One search → full field intelligence**

Search any research topic and get:
- Field overview & trending topics
- Interactive research landscape graph
- Key researchers, labs & research gaps
- Conference talk insights
- Break-in plan: emails, collaborators, conferences, action steps

---

### Slide 4 — Product screenshot

**FieldGuide dashboard**
[Insert screenshot: griefbots results with pipeline strip + stat tiles]

Light, glassmorphic UI designed for clarity — stats, graphs, and actionable outputs in one view.

---

### Slide 5 — How it works

**7-stage sponsor pipeline**

```
Search query
    ↓
Bright Data — live paper ingestion
    ↓
TokenRouter → Kimi — field intelligence
    ↓
Nosana — embeddings + research graph
    ↓
SenseNova — visual field map
    ↓
VideoDB — conference talk insights
    ↓
Daytona — break-in agent (emails + action plan)
```

Each sponsor = one distinct, code-integrated pipeline stage.

---

### Slide 6 — Sponsor integrations

| Sponsor | Role | What it does |
|---------|------|--------------|
| Bright Data | Live Academic Web Layer | Ingests papers from Scholar, OpenAlex, Semantic Scholar |
| Kimi | Field Intelligence Engine | Synthesizes overview, gaps, future directions |
| TokenRouter | Model Orchestration | Routes each stage to the optimal model |
| Nosana | Embedding + Graph Compute | Builds the research landscape graph |
| SenseNova | Multimodal Insight Layer | Generates visual field maps |
| VideoDB | Academic Talk Intelligence | Extracts signals from conference talks |
| Daytona | Secure Agent Runtime | Runs break-in agent in isolated sandbox |

**7/7 sponsors integrated at code level**

---

### Slide 7 — Innovation

**Not another paper search. A career navigation tool.**

What makes FieldGuide different:
- **People-first** — researchers and labs, not just citations
- **Forward-looking** — gaps, trends, and future directions
- **Actionable** — cold emails and break-in plans, not just summaries
- **Full-stack** — 7 AI services orchestrated into one coherent product

Inspired by Perplexity × Connected Papers × academic career coaching.

---

### Slide 8 — Who it's for

**Real pain, real users**

- PhD applicants exploring a new field before writing a proposal
- MS students looking for labs to join
- Researchers pivoting to an adjacent area
- HCI/design students breaking into emerging topics like griefbots or AI ethics

**Market gap:** Existing tools index papers. None help you *join* a field.

---

### Slide 9 — Technical execution

**Architecture**

- **Frontend:** Streamlit glassmorphic dashboard
- **Pipeline:** Python orchestrator with provenance tracking per sponsor
- **Data:** OpenAlex → Semantic Scholar → Bright Data fallback chain
- **LLM:** Kimi via TokenRouter with local fallbacks
- **Graph:** pyvis / vis-network with Nosana embeddings
- **Agent:** Daytona sandbox for break-in planning

Open source · Graceful fallbacks · Live integration status in UI

---

### Slide 10 — Live demo

**Try it now**

```bash
git clone https://github.com/akanksha-cmyk/researchforge
pip install -r requirements.txt
streamlit run app.py
```

Click **▶ Full demo (+ break-in plan)** — watch all 7 sponsors activate.

[QR code or repo URL: github.com/akanksha-cmyk/researchforge]

---

### Slide 11 — Impact

**From search to cold email in 60 seconds**

Before FieldGuide:
- 2 hours reading papers → still don't know who to email
- Manual Google searches for conferences and labs
- No structured view of field dynamics

After FieldGuide:
- One search → field map + people + gaps + action plan
- Send-ready cold emails with one click
- Clear next steps to break into any research area

---

### Slide 12 — Thank you

**FieldGuide**
Navigate your future research community

Built with Bright Data · Kimi · TokenRouter · Nosana · Daytona · SenseNova · VideoDB

github.com/akanksha-cmyk/researchforge
[Your name / contact / team]

Questions?

---

## Gamma generation prompt (optional)

Paste this as your Gamma AI prompt:

> Create a 12-slide hackathon pitch deck for "FieldGuide" — Perplexity for academic careers. Modern light theme with blue/purple gradients. Slides: (1) Title (2) Problem — researchers can't break into fields (3) Solution — one search gives field intelligence + break-in plan (4) Product screenshot placeholder (5) 7-stage pipeline diagram (6) Sponsor integration table with Bright Data, Kimi, TokenRouter, Nosana, Daytona, SenseNova, VideoDB (7) Innovation — people-first, actionable, not paper search (8) Target users — PhD applicants, MS students, field pivoters (9) Tech stack — Streamlit, Python pipeline, pyvis graph, Daytona agent (10) Live demo + GitHub link (11) Impact — search to cold email in 60 seconds (12) Thank you. Tone: confident, clear, investor-ready but academic.

---

## One-liner pitch (elevator)

> "FieldGuide is Perplexity for academic careers — search any research field and get the people, trends, gaps, and a break-in plan with ready-to-send cold emails, powered by seven integrated AI sponsors."

## 30-second pitch (live)

> "Researchers don't need more papers — they need to understand a field and break in. FieldGuide searches any topic and runs a seven-stage AI pipeline: Bright Data ingests live papers, Kimi synthesizes field intelligence, Nosana builds an interactive graph, SenseNova maps the field visually, VideoDB surfaces conference insights, and a Daytona agent generates cold emails and an action plan. From search to send-ready email in under a minute."
