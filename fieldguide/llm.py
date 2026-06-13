"""LLM integration — TokenRouter orchestrates, Kimi synthesizes."""

from __future__ import annotations

import json
import re
from typing import Any

from fieldguide.local_analysis import analyze_field_local, generate_break_in_local
from fieldguide.papers import Author, Paper
from fieldguide.sponsors.tokenrouter import route_and_complete


def _extract_json(text: str) -> dict[str, Any]:
    """Parse JSON from LLM response, handling markdown fences."""
    text = text.strip()
    fence = re.search(r"```(?:json)?\s*([\s\S]*?)```", text)
    if fence:
        text = fence.group(1).strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        start = text.find("{")
        end = text.rfind("}") + 1
        if start >= 0 and end > start:
            return json.loads(text[start:end])
        raise


def _chat_completions(
    messages: list[dict[str, str]],
    task: str = "field_synthesis",
    temperature: float = 0.4,
    cache_key: str | None = None,
) -> str:
    """TokenRouter orchestrates model selection, Kimi executes synthesis."""
    from fieldguide.sponsors.tokenrouter import TaskType

    task_type: TaskType = task if task in ("field_synthesis", "email_generation", "summarization") else "field_synthesis"
    text, _route = route_and_complete(task_type, messages, temperature)
    return text


def analyze_field(
    topic: str,
    paper_context: str,
    papers: list[Paper] | None = None,
    authors: dict[str, Author] | None = None,
) -> dict[str, Any]:
    """Generate structured field overview — LLM with local fallback."""
    try:
        return _analyze_field_llm(topic, paper_context)
    except Exception:
        if papers is not None:
            return analyze_field_local(topic, papers, authors or {})
        raise


def _analyze_field_llm(topic: str, paper_context: str) -> dict[str, Any]:
    system = (
        "You are FieldGuide, an expert academic career navigator. "
        "Analyze research papers and return ONLY valid JSON (no markdown)."
    )
    user = f"""Topic: "{topic}"

Based on these real papers and researchers:

{paper_context}

Return JSON with this exact structure:
{{
  "overview": "2-3 sentence field overview",
  "growth_percent": <integer 10-80 estimating recent field growth>,
  "trending_topics": ["topic1", "topic2", "topic3", "topic4"],
  "research_gaps": [
    {{"gap": "description", "paper_citations": ["Paper Title 1", "Paper Title 2"]}}
  ],
  "key_researchers": [
    {{
      "name": "Full Name",
      "affiliation": "University / Lab",
      "top_paper": "Most relevant paper title",
      "why_important": "One sentence",
      "homepage": "URL or empty string"
    }}
  ],
  "labs_and_programs": [
    {{"name": "Lab Name", "institution": "University", "focus": "One sentence"}}
  ],
  "future_directions": ["direction1", "direction2", "direction3"],
  "themes": [
    {{
      "name": "Theme Name",
      "papers": ["Paper Title A", "Paper Title B"],
      "researchers": ["Researcher X", "Researcher Y"]
    }}
  ]
}}

Use ONLY names and papers from the provided context. Include 3-5 items per list."""

    content = _chat_completions(
        [{"role": "system", "content": system}, {"role": "user", "content": user}],
        task="field_synthesis",
    )
    return _extract_json(content)


def generate_break_in_plan(
    topic: str,
    field_analysis: dict[str, Any],
    user_background: str,
) -> dict[str, Any]:
    """Generate personalized break-in plan — LLM with local fallback."""
    try:
        return _generate_break_in_llm(topic, field_analysis, user_background)
    except Exception:
        return generate_break_in_local(topic, field_analysis, user_background)


def _generate_break_in_llm(
    topic: str,
    field_analysis: dict[str, Any],
    user_background: str,
) -> dict[str, Any]:
    system = (
        "You are FieldGuide, helping researchers break into new fields. "
        "Return ONLY valid JSON."
    )
    user = f"""Topic: "{topic}"
User background: {user_background or "Graduate student exploring this field"}

Field analysis:
{json.dumps(field_analysis, indent=2)}

Return JSON:
{{
  "potential_collaborators": [
    {{
      "name": "Researcher Name",
      "affiliation": "Institution",
      "alignment": "Why they're a good fit",
      "approach": "How to reach out"
    }}
  ],
  "labs_recruiting": [
    {{
      "lab": "Lab Name",
      "institution": "University",
      "why": "Why this lab fits",
      "website": "URL or search hint"
    }}
  ],
  "recent_workshops": ["workshop1", "workshop2"],
  "upcoming_conferences": [
    {{"name": "CHI 2026", "deadline": "approx date", "relevance": "why attend"}}
  ],
  "cold_emails": [
    {{
      "recipient": "Prof. Name",
      "subject": "Email subject line",
      "body": "Full personalized cold email (150-200 words)"
    }}
  ],
  "action_plan": [
    "Step 1: ...",
    "Step 2: ...",
    "Step 3: ..."
  ]
}}"""

    content = _chat_completions(
        [{"role": "system", "content": system}, {"role": "user", "content": user}],
        task="email_generation",
    )
    return _extract_json(content)
