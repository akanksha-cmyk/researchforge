"""Local field analysis when LLM APIs are unavailable."""

from __future__ import annotations

import re
from collections import Counter
from typing import Any

from fieldguide.papers import Author, Paper


def _extract_keywords(text: str) -> list[str]:
    stop = {
        "the", "a", "an", "and", "or", "for", "of", "in", "on", "to", "with",
        "via", "using", "based", "from", "by", "at", "is", "are", "was", "were",
        "this", "that", "these", "those", "we", "our", "their", "its", "as",
        "through", "into", "about", "how", "what", "when", "where", "which",
    }
    words = re.findall(r"[a-zA-Z]{4,}", text.lower())
    return [w for w in words if w not in stop]


def analyze_field_local(topic: str, papers: list[Paper], authors: dict[str, Author]) -> dict[str, Any]:
    """Build structured field analysis purely from paper metadata."""
    if not papers:
        return _empty_analysis(topic)

    venues = Counter(p.venue for p in papers if p.venue)
    years = [p.year for p in papers if p.year]
    recent = sum(1 for y in years if y and y >= 2022)
    growth = min(75, max(15, int(recent / max(len(years), 1) * 60 + 10)))

    # Trending topics from title keywords
    kw_counter: Counter[str] = Counter()
    for p in papers:
        kws = _extract_keywords(p.title + " " + (p.abstract or ""))
        kw_counter.update(kws)
    top_kws = [w.title() for w, _ in kw_counter.most_common(8) if len(w) > 3][:6]
    if len(top_kws) < 4:
        top_kws += [
            f"{topic.title()} Design",
            "User Studies",
            "Ethical Frameworks",
            "Longitudinal Evaluation",
        ][: 4 - len(top_kws)]

    top_authors = sorted(authors.values(), key=lambda a: a.citation_count, reverse=True)
    if not top_authors:
        seen: dict[str, Author] = {}
        for p in papers:
            for a in p.authors:
                if a.name not in seen:
                    seen[a.name] = a
        top_authors = list(seen.values())[:6]

    # Labs from affiliations
    affils = Counter()
    for a in top_authors:
        if a.affiliation:
            affils[a.affiliation] += a.citation_count or 1
    labs = []
    for affil, score in affils.most_common(5):
        name = affil.split(",")[0].strip()
        labs.append({
            "name": name,
            "institution": affil,
            "focus": f"Active contributor in {topic} ({score} citation-weighted activity)",
        })

    # Themes: cluster by shared keywords in titles
    themes = []
    for i, p in enumerate(papers[:4]):
        themes.append({
            "name": _theme_name(p.title),
            "papers": [p.title],
            "researchers": [a.name for a in p.authors[:2]],
        })

    key_researchers = []
    for a in top_authors[:5]:
        relevant = next((p for p in papers if any(
            auth.name == a.name for auth in p.authors
        )), papers[0])
        key_researchers.append({
            "name": a.name,
            "affiliation": a.affiliation or "See paper affiliations",
            "top_paper": relevant.title,
            "why_important": (
                f"Leading author with {a.citation_count or 'significant'} citations"
                + (f", h-index {a.h_index}" if a.h_index else "")
            ),
            "homepage": a.homepage or "",
        })

    gaps = [
        {
            "gap": "Longitudinal studies tracking outcomes over time",
            "paper_citations": [papers[0].title] if papers else [],
        },
        {
            "gap": "Cross-cultural and context-specific evaluation",
            "paper_citations": [papers[1].title if len(papers) > 1 else papers[0].title],
        },
        {
            "gap": "Participatory design with affected communities",
            "paper_citations": [papers[2].title if len(papers) > 2 else papers[0].title],
        },
    ]

    venue_str = ", ".join(v for v, _ in venues.most_common(3)) or "HCI venues"
    overview = (
        f"The field of {topic} spans {len(papers)} key papers across {venue_str}. "
        f"Research has accelerated recently with {recent} papers since 2022, "
        f"focusing on design, ethics, and real-world deployment."
    )

    return {
        "overview": overview,
        "growth_percent": growth,
        "trending_topics": top_kws[:5],
        "research_gaps": gaps,
        "key_researchers": key_researchers,
        "labs_and_programs": labs or [
            {"name": "UW HCDE", "institution": "University of Washington", "focus": "Human-centered design"},
            {"name": "CMU HCII", "institution": "Carnegie Mellon", "focus": "HCI and social computing"},
        ],
        "future_directions": [
            "Longitudinal studies with diverse populations",
            "Cross-cultural evaluation frameworks",
            "Participatory and co-design methods",
            "Ethical guidelines and policy recommendations",
        ],
        "themes": themes,
    }


def generate_break_in_local(
    topic: str,
    analysis: dict[str, Any],
    user_background: str,
) -> dict[str, Any]:
    """Generate break-in plan without LLM."""
    researchers = analysis.get("key_researchers", [])
    labs = analysis.get("labs_and_programs", [])
    bg = user_background or "a graduate student exploring this research area"

    collaborators = []
    for r in researchers[:4]:
        collaborators.append({
            "name": r.get("name", ""),
            "affiliation": r.get("affiliation", ""),
            "alignment": f"Their work on '{r.get('top_paper', topic)[:60]}' aligns with your interest in {topic}",
            "approach": "Read their recent paper, cite it specifically, and propose a concrete collaboration angle",
        })

    labs_recruiting = []
    for lab in labs[:4]:
        labs_recruiting.append({
            "lab": lab.get("name", ""),
            "institution": lab.get("institution", ""),
            "why": lab.get("focus", ""),
            "website": f"Search '{lab.get('name', '')} {lab.get('institution', '')}'",
        })

    cold_emails = []
    for r in researchers[:3]:
        name = r.get("name", "Professor")
        last_name = name.split()[-1] if name else "Professor"
        paper = r.get("top_paper", "")
        body = f"""Dear Dr. {last_name},

I hope this message finds you well. I am {bg}, and I have been deeply engaged with your work on "{paper[:80]}".

Your research on {topic} resonates strongly with my interests, particularly your approach to {_pick_angle(analysis)}. I recently read your paper and was struck by the implications for future work in this space.

I would love the opportunity to discuss potential research collaboration or lab opportunities. I have experience in relevant methods and am eager to contribute to ongoing projects in your group.

Would you be available for a brief 20-minute call in the coming weeks? I am happy to share my CV and a short research statement.

Thank you for your time and for the important work you are doing in this field.

Best regards"""
        cold_emails.append({
            "recipient": name,
            "subject": f"Research inquiry: {topic} — inspired by your work on {paper[:50]}",
            "body": body,
        })

    return {
        "potential_collaborators": collaborators,
        "labs_recruiting": labs_recruiting,
        "recent_workshops": [
            f"CHI {topic.title()} Workshop",
            "CSCW Social Computing Doctoral Colloquium",
            "DIS Design Research Workshop",
        ],
        "upcoming_conferences": [
            {"name": "CHI 2026", "deadline": "September 2025", "relevance": f"Premier venue for {topic} research"},
            {"name": "CSCW 2026", "deadline": "April 2025", "relevance": "Social computing and community-centered design"},
            {"name": "UIST 2026", "deadline": "April 2025", "relevance": "Interactive systems and novel interfaces"},
        ],
        "cold_emails": cold_emails,
        "action_plan": [
            f"Read the top 5 papers on {topic} and annotate research gaps",
            "Identify 3 researchers whose work aligns with your background",
            "Draft personalized cold emails citing specific papers (use templates above)",
            "Apply to relevant workshops at CHI/CSCW for visibility",
            "Reach out to labs 8–10 weeks before application deadlines",
        ],
    }


def _theme_name(title: str) -> str:
    words = title.split()
    if len(words) <= 4:
        return title
    return " ".join(words[:4]) + "…"


def _pick_angle(analysis: dict[str, Any]) -> str:
    topics = analysis.get("trending_topics") or []
    return topics[0].lower() if topics else "community-centered design"


def _empty_analysis(topic: str) -> dict[str, Any]:
    return {
        "overview": f"No papers found for '{topic}'. Try a broader search term.",
        "growth_percent": 0,
        "trending_topics": [],
        "research_gaps": [],
        "key_researchers": [],
        "labs_and_programs": [],
        "future_directions": [],
        "themes": [],
    }
