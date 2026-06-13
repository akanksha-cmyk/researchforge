"""FieldGuide — light glassmorphic research dashboard."""

import importlib
import os
import urllib.parse

import streamlit as st
import streamlit.components.v1 as components
from dotenv import load_dotenv

load_dotenv()
for k, v in list(os.environ.items()):
    if k.endswith("_API_KEY") and isinstance(v, str):
        os.environ[k] = v.strip()

# Prevent Streamlit from using stale cached graph module
import fieldguide.graph as _graph_mod
import fieldguide.pipeline as _pipeline_mod
importlib.reload(_graph_mod)
importlib.reload(_pipeline_mod)
from fieldguide.pipeline import run_break_in_agent, run_field_pipeline
from fieldguide.sponsors.registry import PIPELINE_STAGES, SPONSORS

st.set_page_config(page_title="FieldGuide", page_icon="🧭", layout="wide", initial_sidebar_state="expanded")

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

.stApp {
    background: linear-gradient(145deg, #dce8f8 0%, #e8e0f4 40%, #ddeaf6 100%) !important;
    font-family: 'Inter', -apple-system, sans-serif !important;
}
.block-container { padding: 1.25rem 1.75rem 2.5rem !important; max-width: 1200px !important; }
header, footer, #MainMenu, .stDeployButton { visibility: hidden; height: 0; }

section[data-testid="stSidebar"] {
    background: rgba(255,255,255,0.55) !important;
    backdrop-filter: blur(20px) !important;
    border-right: 1px solid rgba(255,255,255,0.8) !important;
}
section[data-testid="stSidebar"] .block-container { padding-top: 1.25rem; }
section[data-testid="stSidebar"] h3 { font-size: 0.95rem !important; color: #1a1a2e !important; }
section[data-testid="stSidebar"] .stCaption { font-size: 0.72rem !important; }

.tile {
    background: rgba(255,255,255,0.72);
    backdrop-filter: blur(20px) saturate(160%);
    -webkit-backdrop-filter: blur(20px) saturate(160%);
    border: 1px solid rgba(255,255,255,0.95);
    border-radius: 28px;
    padding: 1.5rem 1.75rem;
    box-shadow: 0 4px 24px rgba(100,120,180,0.12), 0 1px 3px rgba(0,0,0,0.04);
    margin-bottom: 1rem;
    color: #1a1a2e;
}
.tile-blue {
    background: linear-gradient(135deg, #4f8ef7 0%, #6366f1 100%);
    border: none; color: #fff;
    box-shadow: 0 8px 32px rgba(99,102,241,0.35);
}
.tile-label { font-size: 0.72rem; font-weight: 600; color: #8892a4; letter-spacing: 0.04em; text-transform: uppercase; margin-bottom: 0.35rem; }
.tile-blue .tile-label { color: rgba(255,255,255,0.65); }
.tile-value { font-size: 2.2rem; font-weight: 700; letter-spacing: -0.03em; line-height: 1.1; }
.tile-sub { font-size: 0.82rem; color: #8892a4; margin-top: 0.3rem; }
.tile-blue .tile-sub { color: rgba(255,255,255,0.75); }

.bar-wrap { display: flex; align-items: flex-end; gap: 0.5rem; height: 80px; margin-top: 0.75rem; }
.bar { flex: 1; border-radius: 8px 8px 4px 4px; background: rgba(99,102,241,0.12); min-height: 12px; position: relative; }
.bar.active { background: linear-gradient(180deg, #6366f1, #a5b4fc); }
.bar-label { font-size: 0.65rem; color: #8892a4; text-align: center; margin-top: 0.35rem; }

.row-item {
    display: flex; align-items: center; gap: 0.85rem;
    padding: 0.75rem 0; border-bottom: 1px solid rgba(0,0,0,0.05);
}
.row-item:last-child { border-bottom: none; }
.row-icon {
    width: 38px; height: 38px; border-radius: 12px; flex-shrink: 0;
    background: linear-gradient(135deg, #e0e7ff, #dbeafe);
    display: flex; align-items: center; justify-content: center;
    font-size: 0.85rem; font-weight: 700; color: #6366f1;
}
.row-title { font-weight: 600; font-size: 0.88rem; color: #1a1a2e; }
.row-meta { font-size: 0.75rem; color: #8892a4; margin-top: 0.1rem; }
.row-insight { font-size: 0.78rem; color: #4f46e5; margin-top: 0.35rem; line-height: 1.45; }
.row-right { margin-left: auto; font-size: 0.78rem; color: #6366f1; font-weight: 500; }

.pill { display: inline-block; padding: 0.3rem 0.75rem; border-radius: 999px;
    background: rgba(99,102,241,0.08); color: #4f46e5; font-size: 0.78rem;
    margin: 0.15rem 0.25rem 0.15rem 0; font-weight: 500; }
.growth { color: #16a34a; font-weight: 600; font-size: 0.85rem; }

.sponsor-row { font-size: 0.75rem; color: #555; padding: 0.3rem 0; display: flex; gap: 0.5rem; align-items: center; }
.sponsor-dot { width: 6px; height: 6px; border-radius: 50%; flex-shrink: 0; }

.stTextInput > div > div > input {
    background: rgba(255,255,255,0.8) !important; border: 1px solid rgba(0,0,0,0.08) !important;
    border-radius: 16px !important; color: #1a1a2e !important; font-size: 0.95rem !important;
}
.stTextArea > div > div > textarea {
    background: rgba(255,255,255,0.9) !important;
    border: 1px solid rgba(99,102,241,0.2) !important;
    border-radius: 16px !important;
    color: #1a1a2e !important;
}
div[data-testid="stTextArea"] { margin-top: -0.25rem !important; margin-bottom: 0.5rem !important; }
.stTextArea textarea::placeholder { color: #8892a4 !important; opacity: 1 !important; }
.stTabs [data-baseweb="tab-panel"] { color: #1a1a2e !important; }
.stTabs [data-baseweb="tab-panel"] p, .stTabs [data-baseweb="tab-panel"] li,
.stTabs [data-baseweb="tab-panel"] pre, .stTabs [data-baseweb="tab-panel"] b {
    color: #1a1a2e !important;
}
.tile pre { color: #334155 !important; background: rgba(241,245,249,0.8) !important;
    border-radius: 12px; padding: 0.75rem; border: none; }
.tile span[style*="6366f1"] { color: #4f46e5 !important; }
.stButton > button {
    border-radius: 14px !important; font-weight: 500 !important;
    background: rgba(255,255,255,0.7) !important; border: 1px solid rgba(0,0,0,0.08) !important;
    color: #333 !important;
}
div[data-testid="stFormSubmitButton"] button, .stButton > button[kind="primary"] {
    background: #1a1a2e !important; color: #fff !important; border: none !important;
    box-shadow: 0 4px 14px rgba(0,0,0,0.15) !important;
}
.stTabs [data-baseweb="tab-list"] { background: rgba(255,255,255,0.5); border-radius: 12px; }
.stTabs [data-baseweb="tab"] {
    color: #64748b !important;
    font-weight: 500 !important;
}
.stTabs [data-baseweb="tab"][aria-selected="true"] {
    color: #4f46e5 !important;
    background: rgba(99,102,241,0.12) !important;
    border-radius: 8px !important;
}
[data-testid="stSpinner"], [data-testid="stSpinner"] p,
[data-testid="stSpinner"] span, [data-testid="stSpinner"] div {
    color: #1a1a2e !important;
}
[data-testid="stStatusWidget"] p, [data-testid="stStatusWidget"] span,
[data-testid="stStatusWidget"] label {
    color: #1a1a2e !important;
}
.footer-note { text-align: center; font-size: 0.72rem; color: #8892a4; padding: 1.5rem 0 0.5rem; }
.send-email-btn > a {
    display: inline-block; margin-top: 0.5rem; padding: 0.45rem 1.1rem;
    background: #4f46e5 !important; color: #fff !important;
    border-radius: 12px !important; text-decoration: none !important;
    font-size: 0.85rem !important; font-weight: 600 !important;
}
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

for key, default in [("pipeline", None), ("break_in", None), ("daytona_runtime", None), ("topic", "")]:
    if key not in st.session_state:
        st.session_state[key] = default


def tile(label: str, value: str, sub: str = "", blue: bool = False) -> str:
    cls = "tile tile-blue" if blue else "tile"
    return f'<div class="{cls}"><div class="tile-label">{label}</div><div class="tile-value">{value}</div>{f"<div class=\'tile-sub\'>{sub}</div>" if sub else ""}</div>'


def bar_chart(topics: list[str]) -> str:
    if not topics:
        return ""
    bars = ""
    labels = ""
    for i, t in enumerate(topics[:6]):
        h = 30 + (len(topics) - i) * 10
        active = "active" if i == 0 else ""
        short = t[:3].upper()
        bars += f'<div style="flex:1;display:flex;flex-direction:column;align-items:center;"><div class="bar {active}" style="height:{h}px;width:100%;"></div><div class="bar-label">{short}</div></div>'
    return f'<div class="bar-wrap">{bars}</div>'


def row(icon: str, title: str, meta: str, right: str = "") -> str:
    if right and len(right) > 40:
        return (
            f'<div class="row-item" style="align-items:flex-start;">'
            f'<div class="row-icon">{icon}</div>'
            f'<div style="flex:1;min-width:0;">'
            f'<div class="row-title">{title}</div>'
            f'<div class="row-meta">{meta}</div>'
            f'<div class="row-insight">{right}</div>'
            f"</div></div>"
        )
    r = f'<div class="row-right">{right}</div>' if right else ""
    return f'<div class="row-item"><div class="row-icon">{icon}</div><div><div class="row-title">{title}</div><div class="row-meta">{meta}</div></div>{r}</div>'


# ── Sidebar: sponsors only ────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🧭 FieldGuide")
    st.markdown(
        '<p style="font-size:0.78rem;color:#64748b;line-height:1.55;margin:0.25rem 0 1rem;">'
        "Perplexity for academic careers. Search any field to discover trends, "
        "researchers, labs, gaps — and how to break in."
        "</p>",
        unsafe_allow_html=True,
    )
    st.markdown("---")
    st.markdown("**Infrastructure**")
    for _stage, sid, label in PIPELINE_STAGES:
        s = SPONSORS[sid]
        st.markdown(
            f'<div class="sponsor-row"><span class="sponsor-dot" style="background:{s.color}"></span>'
            f'<span><b>{s.name}</b> · {label}</span></div>',
            unsafe_allow_html=True,
        )
    st.markdown("---")
    st.caption("Built using Bright Data · Kimi · TokenRouter · Nosana · Daytona · SenseNova · VideoDB")

# ── Main ────────────────────────────────────────────────────────────────────
st.markdown('<div style="font-size:1.6rem;font-weight:700;color:#1a1a2e;margin-bottom:0.1rem;">Field Intelligence</div>', unsafe_allow_html=True)
st.markdown('<div style="color:#8892a4;font-size:0.9rem;margin-bottom:1.25rem;">Navigate your future research community</div>', unsafe_allow_html=True)

EXAMPLES = ["griefbots", "refugee language learning", "participatory design AI", "accessibility in VR"]
ec = st.columns(4)
for col, ex in zip(ec, EXAMPLES):
    if col.button(ex, key=f"ex_{ex}", use_container_width=True):
        st.session_state.prefill = ex

prefill = st.session_state.pop("prefill", "")

with st.form("search"):
    c1, c2 = st.columns([5, 1])
    with c1:
        topic = st.text_input("q", value=prefill or st.session_state.topic, placeholder="Search a research field…", label_visibility="collapsed")
    with c2:
        submitted = st.form_submit_button("Explore →", type="primary", use_container_width=True)

if submitted and topic.strip():
    st.session_state.topic = topic.strip()
    st.session_state.break_in = None
    st.session_state.daytona_runtime = None
    with st.spinner("Mapping field…"):
        st.session_state.pipeline = run_field_pipeline(st.session_state.topic)

pipeline = st.session_state.pipeline

if pipeline:
    topic = pipeline.topic
    analysis = pipeline.analysis
    papers = pipeline.papers
    growth = analysis.get("growth_percent", 35)
    topics = analysis.get("trending_topics", [])

    # ── Stat tiles row ──
    t1, t2, t3, t4 = st.columns(4)
    with t1:
        st.markdown(tile("Papers", str(len(papers)), "Live academic index"), unsafe_allow_html=True)
    with t2:
        st.markdown(tile("Researchers", str(len(analysis.get("key_researchers", []))), "Key voices"), unsafe_allow_html=True)
    with t3:
        st.markdown(tile("Growth", f"↑{growth}%", "Recent activity", blue=True), unsafe_allow_html=True)
    with t4:
        st.markdown(tile("Talks", str(len(pipeline.talk_insights)), "Conference signals"), unsafe_allow_html=True)

    # ── Overview + Topics ──
    r1c1, r1c2 = st.columns([3, 2])
    with r1c1:
        overview = analysis.get("overview", "").replace("**", "")
        st.markdown(
            f'<div class="tile"><div class="tile-label">Field Overview</div>'
            f'<p style="line-height:1.7;font-size:0.92rem;color:#333;margin:0.5rem 0 0.75rem;">{overview}</p>'
            f'<span class="growth">↑ {growth}% field growth</span></div>',
            unsafe_allow_html=True,
        )
    with r1c2:
        pills = "".join(f'<span class="pill">{t}</span>' for t in topics[:5])
        bars = bar_chart(topics)
        st.markdown(
            f'<div class="tile"><div class="tile-label">Trending Topics</div>{bars}{pills}</div>',
            unsafe_allow_html=True,
        )

    # ── Visual + Graph ──
    r2c1, r2c2 = st.columns(2)
    with r2c1:
        components.html(pipeline.field_visual, height=450, scrolling=False)
    with r2c2:
        st.markdown('<div class="tile-label" style="margin-bottom:0.25rem;">Research Landscape</div>', unsafe_allow_html=True)
        components.html(pipeline.graph_html, height=400, scrolling=False)

    # ── Researchers + Gaps ──
    r3c1, r3c2 = st.columns(2)
    with r3c1:
        rows = "".join(
            row((r.get("name", "?")[0]).upper(), r.get("name", ""), r.get("affiliation", ""), "→")
            for r in analysis.get("key_researchers", [])[:5]
        )
        st.markdown(f'<div class="tile"><div class="tile-label">Key Researchers</div>{rows}</div>', unsafe_allow_html=True)
    with r3c2:
        gaps = ""
        for g in analysis.get("research_gaps", [])[:4]:
            gaps += f'<div style="padding:0.5rem 0;border-bottom:1px solid rgba(0,0,0,0.05);"><div style="font-weight:600;font-size:0.88rem;">{g.get("gap","")}</div></div>'
        dirs = "".join(f'<span class="pill">{d}</span>' for d in analysis.get("future_directions", [])[:4])
        st.markdown(f'<div class="tile"><div class="tile-label">Research Gaps</div>{gaps}<div style="margin-top:0.75rem;"><div class="tile-label">Future Directions</div>{dirs}</div></div>', unsafe_allow_html=True)

    # ── Talks + Papers list ──
    talk_rows = "".join(
        row("🎤", t.get("title", ""), f'{t.get("speaker","")} · {t.get("venue","")}', t.get("insight", ""))
        for t in pipeline.talk_insights
    )
    st.markdown(f'<div class="tile"><div class="tile-label">Conference Talk Insights</div>{talk_rows}</div>', unsafe_allow_html=True)

    with st.expander(f"Source papers ({len(papers)})"):
        for p in papers[:10]:
            st.markdown(f"**[{p.title[:70]}]({p.url})** · {p.venue} · {p.citation_count}c")

    # ── Break in ──
    st.markdown(
        '<div class="tile" style="padding-bottom:0.75rem;">'
        '<div class="tile-label">Break Into This Field</div>'
        '<p style="color:#64748b;font-size:0.85rem;margin:0 0 0.75rem;">'
        "Run the research agent to get collaborators, cold emails, and an action plan."
        "</p></div>",
        unsafe_allow_html=True,
    )
    bg = st.text_area(
        "bg",
        placeholder="Your background (optional) — e.g. MS student in HCI with UX experience",
        height=68,
        label_visibility="collapsed",
    )
    if st.button("Generate break-in plan →", type="primary"):
        with st.spinner("Running agent…"):
            plan, runtime = run_break_in_agent(topic, analysis, bg, pipeline.provenance)
            st.session_state.break_in = plan
            st.session_state.daytona_runtime = runtime

    if st.session_state.daytona_runtime:
        st.caption(f"Agent runtime: {st.session_state.daytona_runtime.get('note', '')}")

    plan = st.session_state.break_in
    if plan:
        tabs = st.tabs(["Emails", "Collaborators", "Conferences", "Action plan"])
        with tabs[0]:
            for i, e in enumerate(plan.get("cold_emails", [])):
                recipient = e.get("recipient", "")
                subject = e.get("subject", "")
                body = e.get("body", "")
                st.markdown(
                    f'<div class="tile"><b style="color:#1a1a2e;">{recipient}</b><br>'
                    f'<span style="color:#4f46e5;">{subject}</span>'
                    f'<pre style="white-space:pre-wrap;font-size:0.82rem;margin-top:0.5rem;color:#334155;">{body}</pre></div>',
                    unsafe_allow_html=True,
                )
                mailto = "mailto:?{}".format(
                    urllib.parse.urlencode({"subject": subject, "body": body}, quote_via=urllib.parse.quote)
                )
                st.markdown(
                    f'<div class="send-email-btn"><a href="{mailto}" target="_blank">Send email</a></div>',
                    unsafe_allow_html=True,
                )
        with tabs[1]:
            for c in plan.get("potential_collaborators", []):
                st.markdown(
                    f'<p style="color:#1a1a2e;margin:0.5rem 0;"><b>{c.get("name","")}</b> — '
                    f'<span style="color:#475569;">{c.get("alignment","")}</span></p>',
                    unsafe_allow_html=True,
                )
        with tabs[2]:
            for conf in plan.get("upcoming_conferences", []):
                st.markdown(
                    f'<p style="color:#1a1a2e;margin:0.35rem 0;">• <b>{conf.get("name","")}</b> '
                    f'<span style="color:#6366f1;">(~{conf.get("deadline","")})</span></p>',
                    unsafe_allow_html=True,
                )
        with tabs[3]:
            for i, step in enumerate(plan.get("action_plan", []), 1):
                st.markdown(
                    f'<p style="color:#1a1a2e;font-size:0.9rem;margin:0.4rem 0;">'
                    f"<b>{i}.</b> {step}</p>",
                    unsafe_allow_html=True,
                )

else:
    st.markdown(
        '<div class="tile" style="text-align:center;padding:3rem;">'
        '<div style="font-size:2rem;">🔍</div>'
        '<p style="color:#8892a4;margin:0.5rem 0 0;">Search a field to see papers, people, gaps, and how to break in.</p></div>',
        unsafe_allow_html=True,
    )

st.markdown('<div class="footer-note">Bright Data · Kimi · TokenRouter · Nosana · Daytona · SenseNova · VideoDB</div>', unsafe_allow_html=True)
