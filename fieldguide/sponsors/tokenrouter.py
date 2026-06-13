"""TokenRouter — model orchestration layer."""

from __future__ import annotations

import os
from typing import Any, Literal

import httpx

TOKENROUTER_BASE = "https://api.tokenrouter.io/v1"

TaskType = Literal["field_synthesis", "email_generation", "summarization", "embedding_route"]

# Model routing table — maps task types to providers
ROUTING_TABLE: dict[TaskType, dict[str, str]] = {
    "field_synthesis": {"provider": "kimi", "model": "moonshot-v1-8k", "reason": "Long-context field reasoning"},
    "email_generation": {"provider": "kimi", "model": "moonshot-v1-8k", "reason": "Personalized outreach drafting"},
    "summarization": {"provider": "kimi", "model": "moonshot-v1-8k", "reason": "Summarization via Kimi"},
    "embedding_route": {"provider": "nosana", "model": "text-embeddings", "reason": "Graph compute routing"},
}


def get_route(task: TaskType) -> dict[str, str]:
    """Return routing decision for a pipeline stage."""
    return ROUTING_TABLE[task]


def route_and_complete(
    task: TaskType,
    messages: list[dict[str, str]],
    temperature: float = 0.4,
) -> tuple[str, dict[str, str]]:
    """
    TokenRouter orchestrates model selection, then executes.
    Returns (response_text, routing_metadata).
    """
    route = get_route(task)
    router_key = os.getenv("TOKENROUTER_API_KEY", "").strip()

    if router_key:
        try:
            text = _tokenrouter_responses(messages, router_key, route["model"], temperature)
            return text, {**route, "via": "tokenrouter", "status": "ok"}
        except Exception as exc:
            route = {**route, "via": "tokenrouter", "status": "fallback", "error": str(exc)[:80]}
    else:
        route = {**route, "via": "direct", "status": "direct"}

    # Execute via routed provider (Kimi for synthesis/email)
    from fieldguide.sponsors.kimi import kimi_complete

    text = kimi_complete(messages, model=route.get("model", "moonshot-v1-8k"), temperature=temperature)
    return text, route


def _tokenrouter_responses(
    messages: list[dict[str, str]],
    api_key: str,
    model: str,
    temperature: float,
) -> str:
    prompt = "\n".join(f"{m['role']}: {m['content']}" for m in messages)
    with httpx.Client(timeout=120.0, trust_env=False) as client:
        resp = client.post(
            f"{TOKENROUTER_BASE}/responses",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json={"model": model, "input": prompt, "temperature": temperature},
        )
        resp.raise_for_status()
        data = resp.json()
        if "output_text" in data:
            return data["output_text"]
        if "choices" in data:
            return data["choices"][0]["message"]["content"]
        return str(data)
