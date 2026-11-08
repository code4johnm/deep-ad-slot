"""Weekly ad loop. CPU only. No language-model call.

Reads layout scores plus an optional analytics file, then writes one short
bus message for grok-bot. Applying the change waits for a human 2FA login.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from deep_ad_slot.cooks_defense import DOMAIN as COOKS_DOMAIN
from deep_ad_slot.cooks_defense import package_rows, policy_lines

# Layout-only slots the pages do not have, or that cover crisis UI.
SKIP_SLOTS = {"in-content-outstream", "sticky-rail"}
KEEP_AT = 70.0

SITES = (
    "https://cooksdefensellc.com",
    "https://quantumresearchlaboratories.com",
    "https://warbotiksllc.com",
)


def load_analytics(path: Path | None) -> dict[str, Any]:
    if path is None or not path.is_file():
        return {}
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("analytics file must be a JSON object")
    return data


def _slot_feedback(analytics: dict[str, Any], domain: str, slot_id: str) -> dict[str, Any]:
    sites = analytics.get("sites") if isinstance(analytics.get("sites"), dict) else {}
    site = sites.get(domain) if isinstance(sites, dict) else None
    slots = site.get("slots") if isinstance(site, dict) else None
    row = slots.get(slot_id) if isinstance(slots, dict) else None
    return row if isinstance(row, dict) else {}


def decide(score: float, feedback: dict[str, Any]) -> str:
    """Combine a layout score with viewability. Arithmetic only."""
    impressions = float(feedback.get("impressions") or 0)
    viewable = feedback.get("viewable_rate")
    if impressions >= 50 and viewable is not None and float(viewable) < 0.3:
        return "move"
    if impressions >= 50 and viewable is not None and float(viewable) >= 0.5:
        return "keep"
    if score >= KEEP_AT:
        return "keep"
    return "hold"


def bus_text(rows: list[dict[str, str]]) -> str:
    lines = [
        "Weekly ad adjustment. CPU layout scores plus analytics. No model call produced this note.",
        "Human step: complete the 2FA login, then apply the keep/move lines and the Cooks Defense live/placeholder lines in the GoDaddy file manager.",
        *policy_lines(),
        "quantumresearchlabs.com does not resolve. Use quantumresearchlaboratories.com.",
        "",
    ]
    for row in rows:
        lines.append(
            f"- {row['domain']} {row['slot']} score {row['score']} action {row['action']}"
        )
    text = "\n".join(lines).strip() + "\n"
    if len(text) > 4000:
        raise ValueError("bus text is too long")
    return text


def build_message(
    analyses: list[Any],
    analytics: dict[str, Any] | None = None,
    stamp: str | None = None,
) -> dict[str, str]:
    analytics = analytics or {}
    stamp = stamp or datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    rows: list[dict[str, str]] = []
    for analysis in analyses:
        domain = str(analysis.domain)
        if domain == COOKS_DOMAIN:
            rows.extend(package_rows())
            continue
        for slot in analysis.placements:
            if slot.slot_id in SKIP_SLOTS:
                continue
            if slot.rank > 4:
                continue
            feedback = _slot_feedback(analytics, domain, slot.slot_id)
            rows.append(
                {
                    "domain": domain,
                    "slot": slot.slot_id,
                    "score": f"{slot.score:.0f}",
                    "action": decide(float(slot.score), feedback),
                }
            )
    ident = f"weekly-ads-{stamp}"
    return {
        "id": ident,
        "from": "deep-ad-slot",
        "to": "grok-bot",
        "text": bus_text(rows),
    }


def write_message(message: dict[str, str], dest: Path) -> Path:
    dest.parent.mkdir(parents=True, exist_ok=True)
    body = (
        f"id: {message['id']}\n"
        f"from: {message['from']}\n"
        f"to: {message['to']}\n"
        "text: |\n"
        + "".join(f"  {line}\n" for line in message["text"].splitlines())
    )
    dest.write_text(body, encoding="utf-8")
    return dest
