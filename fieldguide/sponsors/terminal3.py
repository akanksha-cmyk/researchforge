"""Terminal 3 — verifiable agent identity for break-in outputs."""

from __future__ import annotations

import asyncio
import hashlib
import json
import os
from typing import Any

import httpx

T3N_API_BASE = os.getenv("T3N_API_URL", "https://api.terminal3.io").rstrip("/")


def _t3n_ping(api_key: str) -> dict[str, str]:
    """Verify T3N API connectivity (Agent Dev Kit network)."""
    headers = {"X-API-Token": api_key, "Content-Type": "application/json"}
    for path in ("/v1/usage", "/v1/me", "/v1/agent"):
        try:
            with httpx.Client(timeout=20.0, trust_env=False) as client:
                resp = client.get(f"{T3N_API_BASE}{path}", headers=headers)
                if resp.status_code == 200:
                    data = resp.json() if resp.headers.get("content-type", "").startswith("application/json") else {}
                    return {"status": "connected", "endpoint": path, "detail": str(data)[:120]}
        except Exception:
            continue
    return {"status": "key-configured", "endpoint": "t3n-adk", "detail": "T3N API key present"}


def _create_and_sign_agent(
    agent_name: str,
    topic: str,
    payload: str,
) -> dict[str, str]:
    from agent_did_sdk import AgentIdentity, AgentIdentityConfig, CreateAgentParams

    signer_seed = os.getenv("TERMINAL3_SIGNER_ADDRESS", "").strip()
    if not signer_seed.startswith("0x"):
        signer_seed = "0x" + hashlib.sha256(b"fieldguide-break-in").hexdigest()[:40]

    async def _run() -> dict[str, str]:
        identity = AgentIdentity(AgentIdentityConfig(signer_address=signer_seed))
        result = await identity.create(
            CreateAgentParams(
                name=agent_name,
                core_model="kimi-k2.6",
                system_prompt=f"FieldGuide break-in agent for research field: {topic}",
                capabilities=["field-synthesis", "email-generation", "verifiable-identity"],
            )
        )
        signature = await identity.sign_message(payload, result.agent_private_key)
        return {"did": result.document.id, "signature": signature}

    return asyncio.run(_run())


def attest_break_in_plan(
    topic: str,
    plan: dict[str, Any],
    agent_name: str = "fieldguide-break-in-agent",
) -> tuple[dict[str, Any], str]:
    """
    Attach verifiable agent identity to break-in plan outputs.
    Returns (attestation_metadata, source_label).
    """
    t3n_key = os.getenv("T3N_API_KEY", "").strip() or os.getenv("TERMINAL3_API_KEY", "").strip()
    attestation: dict[str, Any] = {"agent": agent_name, "topic": topic}
    source = "terminal3-agent-did"

    if t3n_key:
        attestation["t3n"] = _t3n_ping(t3n_key)
        source = "terminal3-t3n+agent-did"

    try:
        payload = json.dumps(
            {
                "topic": topic,
                "emails": len(plan.get("cold_emails", [])),
                "collaborators": len(plan.get("potential_collaborators", [])),
                "steps": len(plan.get("action_plan", [])),
            },
            sort_keys=True,
        )
        signed = _create_and_sign_agent(agent_name, topic, payload)
        attestation.update(
            {
                "agent_did": signed["did"],
                "payload_hash": hashlib.sha256(payload.encode()).hexdigest(),
                "signature": signed["signature"],
                "verified": True,
            }
        )
    except Exception as exc:
        attestation["verified"] = False
        attestation["error"] = str(exc)[:120]
        source = "terminal3-fallback"

    return attestation, source
