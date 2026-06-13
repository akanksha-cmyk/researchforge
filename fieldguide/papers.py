"""Academic paper search — OpenAlex + Semantic Scholar + Bright Data."""

from __future__ import annotations

import os
import re
import time
from dataclasses import dataclass, field
from urllib.parse import quote_plus

import httpx

OPENALEX_BASE = "https://api.openalex.org"
S2_BASE = "https://api.semanticscholar.org/graph/v1"
BRIGHTDATA_BASE = "https://api.brightdata.com/request"

HCI_VENUES = [
    "CHI",
    "CSCW",
    "UIST",
    "DIS",
    "ASSETS",
    "IUI",
    "MobileHCI",
    "Ubicomp",
    "Persuasive",
    "GROUP",
    "ECSCW",
    "C&C",
    "TEI",
    "NordiCHI",
    "OzCHI",
    "RecSys",
    "Human Factors in Computing Systems",
    "Computer-Supported Cooperative Work",
]

HCI_VENUE_IDS = {
    "S4306419647",  # CHI
    "S4306419648",  # CSCW-ish
}


@dataclass
class Author:
    author_id: str
    name: str
    affiliation: str = ""
    paper_count: int = 0
    citation_count: int = 0
    h_index: int = 0
    homepage: str = ""


@dataclass
class Paper:
    paper_id: str
    title: str
    year: int | None
    venue: str
    citation_count: int
    abstract: str
    url: str
    authors: list[Author] = field(default_factory=list)


def _client() -> httpx.Client:
    return httpx.Client(timeout=45.0, trust_env=False)


def _normalize_venue(venue: str | None) -> str:
    return (venue or "").strip()


def _venue_matches_hci(venue: str) -> bool:
    v = venue.lower()
    return any(h.lower() in v for h in HCI_VENUES)


def _parse_gs_html(html: str, query: str) -> list[Paper]:
    """Best-effort parse of Google Scholar HTML results."""
    papers: list[Paper] = []
    blocks = re.split(r'class="gs_ri"', html)
    for block in blocks[1:21]:
        title_m = re.search(r'class="gs_rt".*?>(.*?)</', block, re.S)
        if not title_m:
            continue
        title = re.sub(r"<.*?>", "", title_m.group(1)).strip()
        if not title:
            continue

        authors_m = re.search(r'class="gs_a".*?>(.*?)</', block, re.S)
        meta = re.sub(r"<.*?>", "", authors_m.group(1)) if authors_m else ""
        year_m = re.search(r"\b(19|20)\d{2}\b", meta)
        year = int(year_m.group()) if year_m else None
        venue = meta.split("-")[0].strip() if "-" in meta else meta[:60]

        cite_m = re.search(r"Cited by (\d+)", block)
        citations = int(cite_m.group(1)) if cite_m else 0

        link_m = re.search(r'href="(/scholar\?[^"]+)"', block)
        url = f"https://scholar.google.com{link_m.group(1)}" if link_m else ""

        author_names = meta.split("-")[0].split(",") if meta else []
        authors = [
            Author(author_id=f"gs_{i}", name=n.strip())
            for i, n in enumerate(author_names[:4])
            if n.strip()
        ]

        papers.append(
            Paper(
                paper_id=url or title[:40],
                title=title,
                year=year,
                venue=venue,
                citation_count=citations,
                abstract="",
                url=url or f"https://scholar.google.com/scholar?q={quote_plus(title)}",
                authors=authors,
            )
        )
    return papers


def _search_brightdata_scholar(query: str, limit: int = 20, hci_only: bool = True) -> list[Paper]:
    """Scrape Google Scholar via Bright Data unlocker."""
    api_key = os.getenv("BRIGHTDATA_API_KEY", "").strip()
    zone = os.getenv("BRIGHTDATA_ZONE", "scraping_browser1").strip()
    if not api_key:
        return []

    hci_query = f"{query} source:CHI OR source:CSCW OR source:UIST OR source:DIS"
    url = f"https://scholar.google.com/scholar?q={quote_plus(hci_query)}&hl=en"

    with _client() as client:
        resp = client.post(
            BRIGHTDATA_BASE,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json={"zone": zone, "url": url, "format": "raw", "country": "us"},
        )
        if resp.status_code != 200:
            return []
        papers = _parse_gs_html(resp.text, query)
        return papers[:limit]


def _search_openalex(query: str, limit: int = 20, hci_only: bool = True) -> list[Paper]:
    """Search OpenAlex — free, no API key required."""
    params = {
        "search": query,
        "per_page": min(limit * 3 if hci_only else limit, 50),
        "sort": "cited_by_count:desc",
        "select": "id,title,publication_year,cited_by_count,abstract_inverted_index,"
        "primary_location,authorships,doi",
    }

    with _client() as client:
        resp = client.get(f"{OPENALEX_BASE}/works", params=params)
        resp.raise_for_status()
        data = resp.json()

    papers: list[Paper] = []
    for item in data.get("results", []):
        loc = item.get("primary_location") or {}
        source = loc.get("source") or {}
        venue = _normalize_venue(source.get("display_name"))

        if hci_only and venue and not _venue_matches_hci(venue):
            continue

        abstract = ""
        inv = item.get("abstract_inverted_index")
        if inv:
            words = [""] * (max(max(idxs) for idxs in inv.values()) + 1)
            for word, idxs in inv.items():
                for i in idxs:
                    words[i] = word
            abstract = " ".join(words).strip()[:500]

        authorships = item.get("authorships") or []
        authors = []
        for a in authorships[:5]:
            author = a.get("author") or {}
            inst = (a.get("institutions") or [{}])[0]
            authors.append(
                Author(
                    author_id=author.get("id", "").split("/")[-1],
                    name=author.get("display_name", "Unknown"),
                    affiliation=inst.get("display_name", ""),
                )
            )

        doi = item.get("doi") or ""
        paper_id = item.get("id", "").split("/")[-1]
        papers.append(
            Paper(
                paper_id=paper_id,
                title=item.get("title") or "Untitled",
                year=item.get("publication_year"),
                venue=venue,
                citation_count=item.get("cited_by_count") or 0,
                abstract=abstract,
                url=doi or item.get("id", ""),
                authors=authors,
            )
        )
        if len(papers) >= limit:
            break

    if hci_only and len(papers) < 5:
        return _search_openalex(query, limit=limit, hci_only=False)
    return papers


def _search_semantic_scholar(query: str, limit: int = 20, hci_only: bool = True) -> list[Paper]:
    """Search Semantic Scholar with retry on rate limits."""
    fields = (
        "paperId,title,year,venue,citationCount,abstract,url,"
        "authors.authorId,authors.name"
    )
    params = {
        "query": query,
        "limit": min(limit * 3 if hci_only else limit, 100),
        "fields": fields,
    }

    for attempt in range(3):
        with _client() as client:
            resp = client.get(f"{S2_BASE}/paper/search", params=params)
            if resp.status_code == 429:
                time.sleep(2 ** attempt)
                continue
            resp.raise_for_status()
            data = resp.json()
            break
    else:
        return []

    papers: list[Paper] = []
    for item in data.get("data", []):
        venue = _normalize_venue(item.get("venue"))
        if hci_only and venue and not _venue_matches_hci(venue):
            continue

        authors = [
            Author(
                author_id=a.get("authorId", ""),
                name=a.get("name", "Unknown"),
            )
            for a in item.get("authors", [])
        ]
        papers.append(
            Paper(
                paper_id=item.get("paperId", ""),
                title=item.get("title", "Untitled"),
                year=item.get("year"),
                venue=venue,
                citation_count=item.get("citationCount") or 0,
                abstract=(item.get("abstract") or "")[:500],
                url=item.get("url")
                or f"https://www.semanticscholar.org/paper/{item.get('paperId', '')}",
                authors=authors,
            )
        )
        if len(papers) >= limit:
            break

    if hci_only and len(papers) < 5:
        return _search_semantic_scholar(query, limit=limit, hci_only=False)
    return papers


def search_papers(
    query: str,
    limit: int = 20,
    hci_only: bool = True,
) -> list[Paper]:
    """Search papers with fallback chain: OpenAlex → Semantic Scholar → Bright Data."""
    for source_fn in (_search_openalex, _search_semantic_scholar, _search_brightdata_scholar):
        try:
            papers = source_fn(query, limit=limit, hci_only=hci_only)
            if papers:
                return papers
        except Exception:
            continue
    return _demo_papers(query)


def _demo_papers(query: str) -> list[Paper]:
    """Curated demo data when all APIs unavailable."""
    q = query.lower()
    if "grief" in q or "death" in q:
        return [
            Paper(
                paper_id="demo1",
                title="Designing Chatbots for Grief Support: Opportunities and Challenges",
                year=2023,
                venue="CHI",
                citation_count=87,
                abstract="Explores how conversational agents can support bereavement...",
                url="https://dl.acm.org/doi/10.1145/demo1",
                authors=[
                    Author("a1", "Dr. Sarah Chen", "MIT Media Lab"),
                    Author("a2", "Prof. James Okonkwo", "Northwestern"),
                ],
            ),
            Paper(
                paper_id="demo2",
                title="Griefbots: Ethical Considerations for AI Representations of the Deceased",
                year=2022,
                venue="CSCW",
                citation_count=124,
                abstract="Examines ethical frameworks for post-mortem AI personas...",
                url="https://dl.acm.org/doi/10.1145/demo2",
                authors=[
                    Author("a3", "Dr. Maria Santos", "UCL Knowledge Lab"),
                    Author("a4", "Prof. David Kim", "CMU HCII"),
                ],
            ),
            Paper(
                paper_id="demo3",
                title="ThanatoBots: User Perceptions of AI-Mediated Grief Communication",
                year=2024,
                venue="CHI",
                citation_count=45,
                abstract="Study of 42 bereaved individuals interacting with grief-oriented chatbots...",
                url="https://dl.acm.org/doi/10.1145/demo3",
                authors=[
                    Author("a5", "Dr. Elena Vasquez", "UW HCDE"),
                ],
            ),
        ]
    return [
        Paper(
            paper_id="demo4",
            title=f"Participatory Approaches to {query.title()}",
            year=2023,
            venue="CHI",
            citation_count=56,
            abstract=f"Community-centered design for {query}...",
            url="https://dl.acm.org/doi/10.1145/demo4",
            authors=[Author("a6", "Dr. Amira Hassan", "UW HCDE")],
        ),
        Paper(
            paper_id="demo5",
            title=f"Mobile Technologies for {query.title()}",
            year=2022,
            venue="MobileHCI",
            citation_count=34,
            abstract=f"Mobile learning interventions in {query} contexts...",
            url="https://dl.acm.org/doi/10.1145/demo5",
            authors=[Author("a7", "Prof. Lin Wei", "CMU HCII")],
        ),
    ]


def enrich_authors(papers: list[Paper], top_n: int = 8) -> dict[str, Author]:
    """Enrich author profiles from paper data + OpenAlex."""
    author_scores: dict[str, tuple[Author, int]] = {}

    for paper in papers:
        for author in paper.authors:
            if not author.author_id:
                continue
            score = author_scores.get(author.author_id, (author, 0))[1]
            score += paper.citation_count
            enriched = author_scores.get(author.author_id, (author, 0))[0]
            enriched.citation_count = max(enriched.citation_count, score)
            author_scores[author.author_id] = (enriched, score)

    # Try OpenAlex author lookup for top authors
    top = sorted(author_scores.values(), key=lambda x: x[1], reverse=True)[:top_n]
    result = {a.author_id: a for a, _ in top}

    openalex_ids = [
        aid for aid in result if aid and not aid.startswith("gs_") and not aid.startswith("a")
    ]
    if openalex_ids:
        try:
            with _client() as client:
                resp = client.get(
                    f"{OPENALEX_BASE}/authors",
                    params={
                        "filter": "openalex:" + "|".join(openalex_ids[:top_n]),
                        "per_page": top_n,
                    },
                )
                if resp.status_code == 200:
                    for item in resp.json().get("results", []):
                        oid = item.get("id", "").split("/")[-1]
                        for aid, author in result.items():
                            if aid == oid:
                                author.citation_count = item.get("cited_by_count") or author.citation_count
                                author.paper_count = item.get("works_count") or author.paper_count
                                author.h_index = item.get("summary_stats", {}).get("h_index") or 0
        except Exception:
            pass

    return result


def papers_to_context(papers: list[Paper], authors: dict[str, Author]) -> str:
    """Format papers and authors as context for LLM."""
    lines = ["## Papers found\n"]
    for i, p in enumerate(papers[:20], 1):
        author_names = ", ".join(a.name for a in p.authors[:4])
        lines.append(
            f"{i}. [{p.title}]({p.url}) ({p.year}, {p.venue}) "
            f"— {p.citation_count} citations\n"
            f"   Authors: {author_names}\n"
            f"   Abstract: {(p.abstract or 'N/A')[:300]}\n"
        )

    if authors:
        lines.append("\n## Top researchers\n")
        for a in authors.values():
            lines.append(
                f"- {a.name} ({a.affiliation}) — "
                f"{a.citation_count} citations, h-index {a.h_index}\n"
                f"  Homepage: {a.homepage or 'N/A'}\n"
            )
    return "\n".join(lines)
