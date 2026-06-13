"""Kimi — field intelligence engine."""

from __future__ import annotations

import os

import httpx

KIMI_BASES = (
    "https://api.moonshot.ai/v1",
    "https://api.moonshot.cn/v1",
)
KIMI_MODELS = ("kimi-k2", "moonshot-v1-32k", "moonshot-v1-8k", "moonshot-v1-auto")


def kimi_complete(
    messages: list[dict[str, str]],
    model: str = "kimi-k2",
    temperature: float = 0.4,
) -> str:
    api_key = os.getenv("KIMI_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError("KIMI_API_KEY not set")

    models = (model,) + tuple(m for m in KIMI_MODELS if m != model)
    for base in KIMI_BASES:
        for m in models:
            with httpx.Client(timeout=120.0, trust_env=False) as client:
                resp = client.post(
                    f"{base}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {api_key}",
                        "Content-Type": "application/json",
                    },
                    json={"model": m, "messages": messages, "temperature": temperature},
                )
                if resp.status_code == 200:
                    return resp.json()["choices"][0]["message"]["content"]
    raise RuntimeError("Kimi authentication failed")
