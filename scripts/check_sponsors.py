"""Check all sponsor API keys. Run: python scripts/check_sponsors.py"""

from __future__ import annotations

import os
import sys
from pathlib import Path

import httpx
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env")


def check(name: str, ok: bool, detail: str) -> tuple[str, bool, str]:
    return name, ok, detail


def main() -> int:
    results: list[tuple[str, bool, str]] = []

    # Bright Data
    key = os.getenv("BRIGHTDATA_API_KEY", "").strip()
    if not key:
        results.append(check("Bright Data", False, "BRIGHTDATA_API_KEY missing"))
    else:
        try:
            r = httpx.post(
                "https://api.brightdata.com/request",
                headers={"Authorization": f"Bearer {key}"},
                json={"zone": os.getenv("BRIGHTDATA_ZONE", "scraping_browser1"), "url": "https://example.com", "format": "raw"},
                timeout=25,
                trust_env=False,
            )
            results.append(check("Bright Data", r.status_code == 200, f"HTTP {r.status_code} — {r.text[:100]}"))
        except Exception as e:
            results.append(check("Bright Data", False, str(e)[:100]))

    # Kimi
    key = os.getenv("KIMI_API_KEY", "").strip()
    if not key:
        results.append(check("Kimi", False, "KIMI_API_KEY missing"))
    else:
        ok = False
        detail = "failed all endpoints"
        for base in ("https://api.moonshot.ai/v1", "https://api.moonshot.cn/v1"):
            for model in ("kimi-k2.6", "kimi-k2", "moonshot-v1-8k", "moonshot-v1-32k"):
                try:
                    r = httpx.post(
                        f"{base}/chat/completions",
                        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
                        json={"model": model, "messages": [{"role": "user", "content": "say hi"}]},
                        timeout=25,
                        trust_env=False,
                    )
                    if r.status_code == 200:
                        ok, detail = True, f"{base} model={model}"
                        break
                    detail = f"{base}/{model} HTTP {r.status_code}"
                except Exception as e:
                    detail = str(e)[:100]
            if ok:
                break
        results.append(check("Kimi", ok, detail))

    # TokenRouter
    key = os.getenv("TOKENROUTER_API_KEY", "").strip()
    if not key:
        results.append(check("TokenRouter", False, "TOKENROUTER_API_KEY missing"))
    else:
        ok = False
        detail = "failed"
        for url, body in (
            ("https://api.tokenrouter.io/v1/responses", {"model": "auto:balance", "input": "say hi"}),
            ("https://api.tokenrouter.io/v1/chat/completions", {
                "model": "auto:balance",
                "messages": [{"role": "user", "content": "say hi"}],
            }),
        ):
            try:
                r = httpx.post(
                    url,
                    headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
                    json=body,
                    timeout=25,
                    trust_env=False,
                )
                if r.status_code == 200:
                    ok, detail = True, f"{url.split('/')[-1]} OK"
                    break
                detail = f"{url.split('/')[-1]} HTTP {r.status_code}"
            except Exception as e:
                detail = str(e)[:100]
        results.append(check("TokenRouter", ok, detail))

    # Daytona
    key = os.getenv("DAYTONA_API_KEY", "").strip()
    api_url = os.getenv("DAYTONA_API_URL", "https://app.daytona.io/api").strip()
    if not key:
        results.append(check("Daytona", False, "DAYTONA_API_KEY missing"))
    else:
        try:
            from daytona import Daytona, DaytonaConfig

            Daytona(DaytonaConfig(api_key=key, api_url=api_url, target=os.getenv("DAYTONA_TARGET", "us")))
            results.append(check("Daytona", True, f"SDK OK ({api_url})"))
        except ImportError:
            results.append(check("Daytona", False, "pip install daytona required"))
        except Exception as e:
            results.append(check("Daytona", False, str(e)[:100]))

    # Nosana
    key = os.getenv("NOSANA_API_KEY", "").strip()
    api_base = os.getenv("NOSANA_API_URL", "https://dashboard.k8s.prd.nos.ci/api").rstrip("/")
    url = os.getenv("NOSANA_EMBED_URL", "").strip()
    if not key:
        results.append(check("Nosana", False, "NOSANA_API_KEY missing"))
    else:
        try:
            r = httpx.get(
                f"{api_base}/credits",
                headers={"Authorization": f"Bearer {key}"},
                timeout=25,
                trust_env=False,
            )
            if r.status_code == 200:
                results.append(check("Nosana", True, f"Credits API OK ({api_base})"))
            elif url:
                r2 = httpx.post(url, headers={"Authorization": f"Bearer {key}"}, json={"inputs": ["test"]}, timeout=25, trust_env=False)
                results.append(check("Nosana", r2.status_code == 200, f"Embed endpoint HTTP {r2.status_code}"))
            else:
                results.append(check("Nosana", False, f"Credits HTTP {r.status_code} — set NOSANA_EMBED_URL"))
        except Exception as e:
            results.append(check("Nosana", False, str(e)[:100]))

    # SenseNova
    key = os.getenv("SENSENOVA_API_KEY", "").strip()
    if not key or key.startswith("SN-PLACEHOLDER"):
        results.append(check("SenseNova", False, "Placeholder or missing SENSENOVA_API_KEY"))
    else:
        try:
            ok_sn = False
            detail_sn = "failed"
            for base in ("https://token.sensenova.cn/v1", "https://api.sensenova.cn/v1"):
                for model in ("sensenova-u1-fast", "sensenova-6.7-flash-lite", "sensenova-6.7-flash"):
                    if model == "sensenova-u1-fast":
                        r = httpx.post(
                            f"{base}/images/generations",
                            headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
                            json={"model": model, "prompt": "test field map", "size": "1376x768", "n": 1},
                            timeout=60,
                            trust_env=False,
                        )
                        if r.status_code == 200:
                            ok_sn, detail_sn = True, f"{base} U1 image OK"
                            break
                        detail_sn = f"{base}/U1 HTTP {r.status_code}: {r.text[:60]}"
                        continue
                    r = httpx.post(
                        f"{base}/chat/completions",
                        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
                        json={"model": model, "messages": [{"role": "user", "content": "hi"}]},
                        timeout=25,
                        trust_env=False,
                    )
                    if r.status_code == 200:
                        ok_sn, detail_sn = True, f"{base} model={model}"
                        break
                    detail_sn = f"{base}/{model} HTTP {r.status_code}: {r.text[:60]}"
                if ok_sn:
                    break
            results.append(check(
                "SenseNova", ok_sn,
                detail_sn + " — try https://platform.sensenova.cn/token-plan if console broken",
            ))
        except Exception as e:
            results.append(check("SenseNova", False, str(e)[:100]))

    # VideoDB
    key = os.getenv("VIDEODB_API_KEY", "").strip()
    if not key:
        results.append(check("VideoDB", False, "VIDEODB_API_KEY missing"))
    else:
        try:
            import videodb

            videodb.connect(api_key=key)
            results.append(check("VideoDB", True, "Connected successfully"))
        except Exception as e:
            results.append(check("VideoDB", False, str(e)[:100]))

    # Terminal 3
    key = os.getenv("T3N_API_KEY", "").strip() or os.getenv("TERMINAL3_API_KEY", "").strip()
    try:
        from fieldguide.sponsors.terminal3 import attest_break_in_plan

        att, src = attest_break_in_plan("test", {"cold_emails": [], "potential_collaborators": [], "action_plan": []})
        ok_t3 = bool(att.get("verified"))
        detail_t3 = f"Agent DID attestation ({src})"
        if key:
            detail_t3 += " + T3N key configured"
        results.append(check("Terminal 3", ok_t3, detail_t3))
    except Exception as e:
        results.append(check("Terminal 3", False, str(e)[:100]))

    print("\nSPONSOR API KEY HEALTH CHECK\n" + "=" * 62)
    fails = 0
    for name, ok, detail in results:
        icon = "✓" if ok else "✗"
        if not ok:
            fails += 1
        print(f"  {icon}  {name:<14}  {'OK' if ok else 'FAIL':<5}  {detail}")
    print("=" * 62)
    print(f"  {len(results) - fails}/{len(results)} passing\n")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
