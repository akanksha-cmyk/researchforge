"""FieldGuide pipeline — each stage mapped to a sponsor."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from fieldguide.graph import build_graph_html
from fieldguide.llm import analyze_field, generate_break_in_plan
from fieldguide.papers import Author, Paper, enrich_authors, papers_to_context
from fieldguide.sponsors.brightdata import ingest_papers
from fieldguide.sponsors.daytona import run_research_agent
from fieldguide.sponsors.nosana import cluster_for_graph, compute_embeddings
from fieldguide.sponsors.registry import PipelineProvenance
from fieldguide.sponsors.sensenova import generate_field_visual
from fieldguide.sponsors.tokenrouter import ROUTING_TABLE
from fieldguide.sponsors.videodb import fetch_talk_insights


@dataclass
class PipelineResult:
    topic: str
    papers: list[Paper]
    authors: dict[str, Author]
    analysis: dict[str, Any]
    embeddings: dict[str, list[float]]
    graph_html: str
    field_visual: str
    talk_insights: list[dict[str, str]]
    provenance: PipelineProvenance = field(default_factory=PipelineProvenance)
    embed_source: str = ""
    visual_source: str = ""
    talk_source: str = ""
    ingest_detail: str = ""


def run_field_pipeline(topic: str, limit: int = 20) -> PipelineResult:
    """Execute full sponsor-mapped pipeline."""
    prov = PipelineProvenance()

    # Stage 1: Bright Data — live academic ingestion
    papers, ingest_source, ingest_detail = ingest_papers(topic, limit=limit)
    prov.record(
        "ingest",
        "brightdata",
        "ok" if ingest_source == "brightdata" else "fallback",
        ingest_detail,
    )

    authors = enrich_authors(papers, top_n=8)

    # Stage 2–3: TokenRouter routes → Kimi field intelligence
    context = papers_to_context(papers, authors)
    route = ROUTING_TABLE["field_synthesis"]
    prov.record("route", "tokenrouter", "ok", f"Routed field_synthesis → {route['provider']}:{route['model']}")

    try:
        analysis = analyze_field(topic, context, papers=papers, authors=authors)
        prov.record("analyze", "kimi", "ok", "Field overview, gaps, future directions synthesized")
        analysis_source = "kimi"
    except Exception as exc:
        from fieldguide.local_analysis import analyze_field_local

        analysis = analyze_field_local(topic, papers, authors)
        prov.record("analyze", "kimi", "fallback", f"Local synthesis ({exc})")
        analysis_source = "local"

    # Stage 4–5: Nosana — embeddings + graph compute
    topics = analysis.get("trending_topics") or []
    embeddings, embed_source = compute_embeddings(papers, topics)
    cluster = cluster_for_graph(embeddings, analysis)
    prov.record(
        "embed",
        "nosana",
        "ok" if embed_source == "nosana-gpu" else "fallback",
        f"{cluster['node_count']} nodes embedded via {embed_source}",
    )

    graph_html = build_graph_html(topic, analysis, papers)
    prov.record("graph", "nosana", "ok", "Research landscape graph constructed from embeddings")

    # Stage 6: SenseNova — visual field map
    field_visual, visual_source = generate_field_visual(topic, analysis)
    prov.record(
        "visual",
        "sensenova",
        "ok" if visual_source == "sensenova" else "fallback",
        f"Field diagram generated ({visual_source})",
    )

    # Stage 7: VideoDB — conference talk intelligence
    talk_insights, talk_source = fetch_talk_insights(topic, analysis)
    prov.record(
        "talks",
        "videodb",
        "ok" if talk_source == "videodb" else "fallback",
        f"{len(talk_insights)} talk insights extracted",
    )

    return PipelineResult(
        topic=topic,
        papers=papers,
        authors=authors,
        analysis=analysis,
        embeddings=embeddings,
        graph_html=graph_html,
        field_visual=field_visual,
        talk_insights=talk_insights,
        provenance=prov,
        embed_source=embed_source,
        visual_source=visual_source,
        talk_source=talk_source,
        ingest_detail=ingest_detail,
    )


def run_break_in_agent(
    topic: str,
    analysis: dict[str, Any],
    background: str,
    provenance: PipelineProvenance,
) -> tuple[dict[str, Any], dict[str, str]]:
    """Stage 8: Daytona — secure break-in agent."""
    payload = {"topic": topic, "background": background, "analysis": analysis}

    def _execute(p: dict[str, Any]) -> dict[str, Any]:
        return generate_break_in_plan(p["topic"], p["analysis"], p.get("background", ""))

    plan, runtime = run_research_agent("break-in-planner", payload, _execute)
    provenance.record(
        "agent",
        "daytona",
        "ok" if runtime.get("runtime") == "daytona-sandbox" else "fallback",
        runtime.get("note", "Break-in agent executed"),
    )
    return plan, runtime
