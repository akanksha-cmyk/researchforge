"""Bright Data — live academic web ingestion layer."""

from __future__ import annotations

from fieldguide.papers import Paper, search_papers as _search_papers


def ingest_papers(query: str, limit: int = 20) -> tuple[list[Paper], str, str]:
    """
    Pull live academic data. Returns (papers, source_label, detail).
    source_label: brightdata | openalex | semantic_scholar | demo
    """
    from fieldguide.papers import _search_brightdata_scholar, _search_openalex, _search_semantic_scholar

    # Prefer Bright Data when configured
    try:
        papers = _search_brightdata_scholar(query, limit=limit)
        if papers:
            return papers, "brightdata", f"Google Scholar via Bright Data unlocker ({len(papers)} papers)"
    except Exception as exc:
        pass

    try:
        papers = _search_openalex(query, limit=limit)
        if papers:
            return papers, "openalex", f"OpenAlex live index ({len(papers)} papers) — Bright Data fallback ready"
    except Exception:
        pass

    try:
        papers = _search_semantic_scholar(query, limit=limit)
        if papers:
            return papers, "semantic_scholar", f"Semantic Scholar ({len(papers)} papers)"
    except Exception:
        pass

    papers = _search_papers(query, limit=limit)
    return papers, "multi-source", f"Multi-source academic ingestion ({len(papers)} papers)"
