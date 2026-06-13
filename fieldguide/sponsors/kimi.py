"""Kimi — field intelligence engine (K2.6 + context caching)."""

from __future__ import annotations

import os

import httpx

KIMI_BASES = (
    "https://api.moonshot.ai/v1",
    "https://api.moonshot.cn/v1",
)
KIMI_MODELS = (
    "kimi-k2.6",
    "kimi-k2.5",
    "kimi-k2",
    "moonshot-v1-32k",
    "moonshot-v1-8k",
    "moonshot-v1-auto",
)

# Stable system prompts cached across pipeline calls (prefix caching)
FIELD_SYSTEM = (
    "You are FieldGuide, an expert academic career navigator. "
    "Analyze research papers and return structured field intelligence."
)
EMAIL_SYSTEM = (
    "You are FieldGuide, helping researchers break into new fields with personalized outreach."
)


def kimi_complete(
    messages: list[dict[str, str]],
    model: str = "kimi-k2.6",
    temperature: float = 0.4,
    cache_key: str | None = None,
) -> str:
    api_key = os.getenv("KIMI_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError("KIMI_API_KEY not set")

    models = (model,) + tuple(m for m in KIMI_MODELS if m != model)
    body_base: dict = {"temperature": temperature}
    if cache_key:
        body_base["prompt_cache_key"] = cache_key

    for base in KIMI_BASES:
        for m in models:
            payload = {**body_base, "model": m, "messages": messages}
            with httpx.Client(timeout=120.0, trust_env=False) as client:
                resp = client.post(
                    f"{base}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {api_key}",
                        "Content-Type": "application/json",
                    },
                    json=payload,
                )
                if resp.status_code == 200:
                    return resp.json()["choices"][0]["message"]["content"]
    raise RuntimeError("Kimi authentication failed")
