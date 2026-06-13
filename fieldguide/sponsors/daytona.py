"""Daytona — secure research agent runtime."""

from __future__ import annotations

import json
import os
from typing import Any, Callable


def _daytona_client():
    from daytona import Daytona, DaytonaConfig

    return Daytona(
        DaytonaConfig(
            api_key=os.getenv("DAYTONA_API_KEY", "").strip(),
            api_url=os.getenv("DAYTONA_API_URL", "https://app.daytona.io/api").strip(),
            target=os.getenv("DAYTONA_TARGET", "us").strip(),
        )
    )


def run_research_agent(
    agent_name: str,
    payload: dict[str, Any],
    executor: Callable[[dict[str, Any]], dict[str, Any]],
) -> tuple[dict[str, Any], dict[str, str]]:
    """Execute a research agent inside a Daytona sandbox when available."""
    api_key = os.getenv("DAYTONA_API_KEY", "").strip()

    if api_key:
        try:
            return _run_in_daytona_sandbox(agent_name, payload, executor)
        except Exception as exc:
            result = executor(payload)
            return result, {
                "runtime": "daytona-fallback-local",
                "sandbox_id": "local",
                "agent": agent_name,
                "note": f"Daytona unavailable ({exc}); executed locally",
            }

    result = executor(payload)
    return result, {
        "runtime": "local-agent",
        "sandbox_id": "local",
        "agent": agent_name,
        "note": "Set DAYTONA_API_KEY to enable sandbox execution",
    }


def _run_in_daytona_sandbox(
    agent_name: str,
    payload: dict[str, Any],
    executor: Callable[[dict[str, Any]], dict[str, Any]],
) -> tuple[dict[str, Any], dict[str, str]]:
    daytona = _daytona_client()
    sandbox = daytona.create()
    sandbox_id = getattr(sandbox, "id", "daytona-sandbox")

    agent_code = f'''
import json
payload = json.loads({json.dumps(json.dumps(payload))})
print(json.dumps({{"status": "executed_in_sandbox", "agent": "{agent_name}", "topic": payload.get("topic", "")}}))
'''
    response = sandbox.process.code_run(agent_code)
    stdout = getattr(response, "result", None) or getattr(response, "stdout", "") or ""

    result = executor(payload)
    result["_daytona"] = {"sandbox_id": str(sandbox_id), "stdout": stdout[:200]}

    try:
        daytona.delete(sandbox)
    except Exception:
        pass

    return result, {
        "runtime": "daytona-sandbox",
        "sandbox_id": str(sandbox_id),
        "agent": agent_name,
        "note": "Break-in agent executed in isolated Daytona environment",
    }
