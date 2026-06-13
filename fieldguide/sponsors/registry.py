"""Sponsor registry — each sponsor maps to one pipeline stage."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Sponsor:
    id: str
    name: str
    role: str
    tagline: str
    color: str
    icon: str


SPONSORS: dict[str, Sponsor] = {
    "brightdata": Sponsor(
        id="brightdata",
        name="Bright Data",
        role="Live Academic Web Layer",
        tagline="Continuously pulls live academic data across the web",
        color="#ff6b35",
        icon="🕸",
    ),
    "kimi": Sponsor(
        id="kimi",
        name="Kimi",
        role="Field Intelligence Engine",
        tagline="Transforms raw papers into structured field understanding",
        color="#6366f1",
        icon="🧠",
    ),
    "tokenrouter": Sponsor(
        id="tokenrouter",
        name="TokenRouter",
        role="Model Orchestration Layer",
        tagline="Dynamically selects the best model for each pipeline stage",
        color="#22c55e",
        icon="⚡",
    ),
    "nosana": Sponsor(
        id="nosana",
        name="Nosana",
        role="Embedding + Graph Compute",
        tagline="Distributed embedding computation for large-scale graph construction",
        color="#06b6d4",
        icon="🧬",
    ),
    "daytona": Sponsor(
        id="daytona",
        name="Daytona",
        role="Secure Agent Runtime",
        tagline="Executes research agents in isolated environments for safety",
        color="#f59e0b",
        icon="🧪",
    ),
    "sensenova": Sponsor(
        id="sensenova",
        name="SenseNova U1",
        role="Multimodal Insight Layer",
        tagline="U1 image generation for structured visual field maps",
        color="#ec4899",
        icon="🎨",
    ),
    "videodb": Sponsor(
        id="videodb",
        name="VideoDB",
        role="Academic Talk Intelligence",
        tagline="Converts conference talks into structured research signals",
        color="#8b5cf6",
        icon="🎥",
    ),
    "terminal3": Sponsor(
        id="terminal3",
        name="Terminal 3",
        role="Verifiable Agent Identity",
        tagline="Cryptographic agent DID attestation for break-in outputs",
        color="#0ea5e9",
        icon="🔐",
    ),
}

PIPELINE_STAGES = [
    ("ingest", "brightdata", "Live research ingestion"),
    ("analyze", "kimi", "Field reasoning & synthesis"),
    ("route", "tokenrouter", "Model orchestration"),
    ("embed", "nosana", "Embedding computation"),
    ("graph", "nosana", "Graph construction"),
    ("visual", "sensenova", "Visual field mapping"),
    ("talks", "videodb", "Conference talk intelligence"),
    ("agent", "daytona", "Secure agent execution"),
    ("identity", "terminal3", "Verifiable agent identity"),
]


@dataclass
class StageResult:
    stage: str
    sponsor_id: str
    status: str  # ok | fallback | skipped
    detail: str = ""


@dataclass
class PipelineProvenance:
    stages: list[StageResult] = field(default_factory=list)

    def record(self, stage: str, sponsor_id: str, status: str = "ok", detail: str = ""):
        self.stages.append(StageResult(stage, sponsor_id, status, detail))

    def by_sponsor(self) -> dict[str, list[StageResult]]:
        out: dict[str, list[StageResult]] = {}
        for s in self.stages:
            out.setdefault(s.sponsor_id, []).append(s)
        return out
