"""Interactive research landscape node graph."""

from __future__ import annotations

import tempfile
from typing import Any

from pyvis.network import Network


def build_graph_html(
    topic: str,
    analysis: dict[str, Any],
    papers: list[Any],
) -> str:
    """Build pyvis network: Theme → Papers → Researchers → Labs."""
    net = Network(
        height="480px",
        width="100%",
        bgcolor="#f0f4ff",
        font_color="#1a1a2e",
        directed=True,
    )
    net.set_options(
        """
    {
      "physics": {
        "enabled": true,
        "barnesHut": {
          "gravitationalConstant": -8000,
          "springLength": 180,
          "springConstant": 0.04
        },
        "stabilization": {"iterations": 120}
      },
      "interaction": {"hover": true, "navigationButtons": true},
      "nodes": {"font": {"size": 13, "face": "Inter, sans-serif", "color": "#1a1a2e"}},
      "edges": {"smooth": {"type": "continuous"}, "color": {"color": "#94a3b8", "opacity": 0.5}}
    }
    """
    )

    net.add_node(
        f"topic::{topic}",
        label=topic[:40],
        title=f"Field: {topic}",
        color="#6366f1",
        size=36,
        shape="diamond",
    )

    themes = analysis.get("themes") or []
    if not themes:
        themes = [
            {"name": t, "papers": [], "researchers": []}
            for t in (analysis.get("trending_topics") or [])[:4]
        ]

    paper_titles = {p.title: p for p in papers}
    labs = analysis.get("labs_and_programs") or []
    added_nodes: set[str] = {f"topic::{topic}"}

    for theme in themes[:5]:
        theme_name = theme.get("name", "Theme")
        theme_id = f"theme::{theme_name}"
        net.add_node(
            theme_id,
            label=theme_name[:30],
            title=theme_name,
            color="#8b5cf6",
            size=24,
            shape="box",
        )
        net.add_edge(f"topic::{topic}", theme_id, color="#6366f1")

        for paper_title in (theme.get("papers") or [])[:3]:
            paper = paper_titles.get(paper_title)
            pid = f"paper::{paper_title[:50]}"
            net.add_node(
                pid,
                label=(paper_title[:35] + "…") if len(paper_title) > 35 else paper_title,
                title=paper_title,
                color="#ffffff",
                size=16,
                shape="dot",
                font={"color": "#1a1a2e"},
                borderWidth=2,
                border="#cbd5e1",
            )
            net.add_edge(theme_id, pid, color="#a78bfa")

            if paper:
                for author in paper.authors[:2]:
                    aid = f"author::{author.name}"
                    net.add_node(
                        aid,
                        label=author.name[:25],
                        title=author.name,
                        color="#22d3ee",
                        size=18,
                        shape="ellipse",
                    )
                    net.add_edge(pid, aid, color="#67e8f9")

        for researcher in (theme.get("researchers") or [])[:2]:
            rid = f"author::{researcher}"
            if rid not in added_nodes:
                net.add_node(
                    rid,
                    label=researcher[:25],
                    title=researcher,
                    color="#22d3ee",
                    size=18,
                    shape="ellipse",
                )
                added_nodes.add(rid)
            net.add_edge(theme_id, rid, color="#67e8f9", dashes=True)

    for lab in labs[:4]:
        lab_name = lab.get("name", "Lab")
        lid = f"lab::{lab_name}"
        institution = lab.get("institution", "")
        net.add_node(
            lid,
            label=lab_name[:25],
            title=f"{lab_name} — {institution}",
            color="#f59e0b",
            size=22,
            shape="hexagon",
        )
        net.add_edge(f"topic::{topic}", lid, color="#fbbf24", dashes=True)

    with tempfile.NamedTemporaryFile(
        delete=False, suffix=".html", mode="w", encoding="utf-8"
    ) as f:
        net.save_graph(f.name)
        with open(f.name, encoding="utf-8") as html:
            content = html.read()
    content = content.replace('background-color:#1a1a22', 'background-color:#f0f4ff')
    content = content.replace('background-color:#222222', 'background-color:#f0f4ff')
    content = content.replace('background-color:#ffffff', 'background-color:#f0f4ff')
    return content
