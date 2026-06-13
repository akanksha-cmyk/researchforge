"""SenseNova U1 — multimodal visual field mapping."""

from __future__ import annotations

import os
from typing import Any

import httpx

SENSENOVA_BASE = "https://token.sensenova.cn/v1"
SENSENOVA_CHAT_MODELS = (
    "sensenova-6.7-flash-lite",
    "sensenova-6.7-flash",
    "deepseek-v4-flash",
)
SENSENOVA_U1_MODEL = "sensenova-u1-fast"


def generate_field_visual(
    topic: str,
    analysis: dict[str, Any],
) -> tuple[str, str]:
    """Generate visual field map via SenseNova U1. Returns (html, source)."""
    api_key = os.getenv("SENSENOVA_API_KEY", "").strip()
    if api_key and not api_key.startswith("SN-PLACEHOLDER"):
        try:
            visual = _sensenova_u1_image(topic, analysis, api_key)
            if visual:
                return visual, "sensenova-u1"
        except Exception:
            pass
        try:
            visual = _sensenova_chat_visual(topic, analysis, api_key)
            if visual:
                return visual, "sensenova"
        except Exception:
            pass

    try:
        brief = _kimi_visual_brief(topic, analysis)
        if brief:
            return _local_field_svg(topic, analysis, brief), "sensenova-kimi-render"
    except Exception:
        pass

    return _local_field_svg(topic, analysis), "sensenova-local-render"


def _sensenova_u1_image(topic: str, analysis: dict[str, Any], api_key: str) -> str | None:
    """SenseNova U1 Fast — infographic field map generation."""
    topics = ", ".join(analysis.get("trending_topics", [])[:5])
    directions = ", ".join(analysis.get("future_directions", [])[:3])
    growth = analysis.get("growth_percent", 30)
    prompt = (
        f"Research field infographic map for '{topic}'. "
        f"Trending clusters: {topics}. Future directions: {directions}. "
        f"Growth: {growth}%. Clean academic infographic, blue and purple palette, "
        f"node clusters connected by lines, modern data visualization style."
    )
    with httpx.Client(timeout=120.0, trust_env=False) as client:
        resp = client.post(
            f"{SENSENOVA_BASE}/images/generations",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": SENSENOVA_U1_MODEL,
                "prompt": prompt,
                "size": "1376x768",
                "n": 1,
            },
        )
        if resp.status_code != 200:
            return None
        data = resp.json().get("data") or []
        if not data or not data[0].get("url"):
            return None
        image_url = data[0]["url"]
        return _wrap_image_html(topic, image_url, "SenseNova U1 · Visual Field Map")


def _sensenova_chat_visual(topic: str, analysis: dict[str, Any], api_key: str) -> str | None:
    topics = ", ".join(analysis.get("trending_topics", [])[:5])
    directions = ", ".join(analysis.get("future_directions", [])[:3])
    prompt = (
        f"Describe a structured research field map for '{topic}'. "
        f"Trending areas: {topics}. Future directions: {directions}. "
        f"Return a concise structured summary with 3 clusters and key connections."
    )
    for model in SENSENOVA_CHAT_MODELS:
        with httpx.Client(timeout=60.0, trust_env=False) as client:
            resp = client.post(
                f"{SENSENOVA_BASE}/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": model,
                    "max_tokens": 800,
                    "messages": [{"role": "user", "content": prompt}],
                },
            )
            if resp.status_code == 200:
                content = resp.json()["choices"][0]["message"]["content"]
                return _local_field_svg(topic, analysis, content)
    return None


def _wrap_image_html(topic: str, image_url: str, label: str) -> str:
    return f"""<!DOCTYPE html><html><head><meta charset="utf-8"></head>
<body style="margin:0;padding:0;background:#f0f4ff;">
<div style="font-size:0.65rem;color:#6366f1;letter-spacing:0.1em;text-transform:uppercase;
font-weight:600;padding:0.5rem 0.5rem 0;">{label}</div>
<img src="{image_url}" alt="{topic} field map"
     style="width:100%;height:auto;border-radius:16px;display:block;"/>
</body></html>"""


def _kimi_visual_brief(topic: str, analysis: dict[str, Any]) -> str:
    from fieldguide.sponsors.kimi import kimi_complete

    topics = ", ".join(analysis.get("trending_topics", [])[:5])
    content = kimi_complete(
        [
            {
                "role": "user",
                "content": (
                    f"In 2 sentences, describe a visual field map layout for research topic '{topic}' "
                    f"covering themes: {topics}. Focus on cluster relationships."
                ),
            }
        ],
        temperature=0.3,
        cache_key="fieldguide-visual-brief",
    )
    return content.strip()


def _local_field_svg(
    topic: str,
    analysis: dict[str, Any],
    brief: str = "",
) -> str:
    """SVG field map fallback render."""
    topics = analysis.get("trending_topics", [])[:5]
    directions = analysis.get("future_directions", [])[:3]
    growth = analysis.get("growth_percent", 30)
    colors = ["#6366f1", "#8b5cf6", "#22d3ee", "#f59e0b", "#ec4899"]

    import math

    nodes_svg = ""
    for i, t in enumerate(topics):
        angle = (i / max(len(topics), 1)) * 6.28
        cx = 400 + int(180 * math.cos(angle))
        cy = 210 + int(115 * math.sin(angle))
        color = colors[i % len(colors)]
        label = t[:16] + ("…" if len(t) > 16 else "")
        nodes_svg += f'''
        <circle cx="{cx}" cy="{cy}" r="44" fill="{color}" opacity="0.88"/>
        <text x="{cx}" y="{cy + 4}" text-anchor="middle" fill="white" font-size="10" font-family="Inter,sans-serif">{label}</text>
        <line x1="400" y1="210" x2="{cx}" y2="{cy}" stroke="{color}" stroke-width="2" opacity="0.45"/>
        '''

    dir_items = "".join(
        f'<text x="36" y="{330 + i * 20}" fill="#64748b" font-size="11" font-family="Inter,sans-serif">→ {d[:42]}</text>'
        for i, d in enumerate(directions)
    )

    brief_html = ""
    if brief:
        brief_html = (
            f'<text x="36" y="395" fill="#475569" font-size="10" font-family="Inter,sans-serif">'
            f'{brief[:120]}…</text>'
        )

    return f"""<!DOCTYPE html><html><head><meta charset="utf-8"></head><body style="margin:0;padding:0;background:#f0f4ff;">
<div style="font-size:0.65rem;color:#6366f1;letter-spacing:0.1em;text-transform:uppercase;margin-bottom:0.35rem;font-weight:600;padding:0.5rem 0.5rem 0;">
  SenseNova U1 · Visual Field Map
</div>
<svg viewBox="0 0 800 420" xmlns="http://www.w3.org/2000/svg" style="width:100%;height:auto;display:block;">
  <rect width="800" height="420" fill="#f0f4ff" rx="16"/>
  <text x="400" y="210" text-anchor="middle" fill="#1e293b" font-size="15" font-weight="700" font-family="Inter,sans-serif">{topic[:28]}</text>
  <text x="400" y="232" text-anchor="middle" fill="#16a34a" font-size="12" font-weight="600" font-family="Inter,sans-serif">↑ {growth}% growth</text>
  {nodes_svg}
  <text x="36" y="310" fill="#6366f1" font-size="10" font-weight="700" font-family="Inter,sans-serif">FUTURE DIRECTIONS</text>
  {dir_items}
  {brief_html}
</svg>
</body></html>"""
