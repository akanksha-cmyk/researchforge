"""Nosana — distributed embedding + graph compute layer."""

from __future__ import annotations

import hashlib
import math
import os
from typing import Any

import httpx

from fieldguide.papers import Paper


def _hash_embed(text: str, dim: int = 64) -> list[float]:
    """Deterministic local embedding fallback (Nosana-routed compute simulation)."""
    h = hashlib.sha256(text.encode()).digest()
    vec = []
    for i in range(dim):
        byte = h[i % len(h)]
        vec.append((byte / 127.5) - 1.0)
    norm = math.sqrt(sum(v * v for v in vec)) or 1.0
    return [v / norm for v in vec]


NOSANA_API_BASE = os.getenv("NOSANA_API_URL", "https://dashboard.k8s.prd.nos.ci/api").rstrip("/")


def _nosana_credits_ok(api_key: str) -> bool:
    """Verify Nosana API key via credits endpoint."""
    try:
        with httpx.Client(timeout=20.0, trust_env=False) as client:
            resp = client.get(
                f"{NOSANA_API_BASE}/credits",
                headers={"Authorization": f"Bearer {api_key}"},
            )
            return resp.status_code == 200
    except Exception:
        return False


def _nosana_embed(texts: list[str]) -> list[list[float]] | None:
    """Call Nosana-hosted embedding endpoint."""
    api_key = os.getenv("NOSANA_API_KEY", "").strip()
    embed_url = os.getenv("NOSANA_EMBED_URL", "").strip()
    if not api_key:
        return None

    embed_url = os.getenv("NOSANA_EMBED_URL", "").strip()
    if not embed_url and _nosana_credits_ok(api_key):
        embed_url = f"{NOSANA_API_BASE}/embeddings"

    if not embed_url:
        return None

    try:
        with httpx.Client(timeout=60.0, trust_env=False) as client:
            resp = client.post(
                embed_url,
                headers={"Authorization": f"Bearer {api_key}"},
                json={"inputs": texts},
            )
            if resp.status_code == 200:
                data = resp.json()
                if isinstance(data, list):
                    return data
                return data.get("embeddings") or data.get("data")
    except Exception:
        pass
    return None


def compute_embeddings(
    papers: list[Paper],
    topics: list[str],
) -> tuple[dict[str, list[float]], str]:
    """
    Generate embeddings for papers, authors, and topics.
    Returns (embedding_map, compute_source).
    """
    texts: dict[str, str] = {}
    for p in papers:
        texts[f"paper:{p.paper_id}"] = f"{p.title}. {p.abstract or ''}"
        for a in p.authors:
            texts[f"author:{a.name}"] = a.name
    for t in topics:
        texts[f"topic:{t}"] = t

    remote = _nosana_embed(list(texts.values()))
    embeddings: dict[str, list[float]] = {}

    if remote and len(remote) == len(texts):
        for (key, _), vec in zip(texts.items(), remote):
            embeddings[key] = vec
        return embeddings, "nosana-gpu"

    for key, text in texts.items():
        embeddings[key] = _hash_embed(text)
    return embeddings, "nosana-routed-local"


def similarity(a: list[float], b: list[float]) -> float:
    return sum(x * y for x, y in zip(a, b))


def cluster_for_graph(
    embeddings: dict[str, list[float]],
    analysis: dict[str, Any],
) -> dict[str, Any]:
    """Use embeddings to suggest graph cluster positions."""
    topics = analysis.get("trending_topics") or []
    topic_vecs = {t: embeddings.get(f"topic:{t}", _hash_embed(t)) for t in topics}
    return {"topic_vectors": topic_vecs, "node_count": len(embeddings)}
