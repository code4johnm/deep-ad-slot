from __future__ import annotations

import re
from dataclasses import asdict, dataclass, field

from deep_ad_slot.orgs import org_for_host

PREBID_MARKERS = (
    r"prebid\.js",
    r"pbjs",
    r"pbjs\.que",
    r"window\.pbjs",
    r"\bppa\b",
    r"header.?bidding",
)

ADAPTER_HINTS = {
    "appnexus": "Microsoft / Xandr",
    "adnxs": "Microsoft / Xandr",
    "ix": "Index Exchange",
    "indexExchange": "Index Exchange",
    "rubicon": "Magnite",
    "openx": "OpenX",
    "pubmatic": "PubMatic",
    "amazon": "Amazon",
    "sovrn": "Sovrn",
    "sovrnLite": "Sovrn",
    "triplelift": "TripleLift",
    "sharethrough": "Sharethrough",
    "criteo": "Criteo",
    "ttd": "The Trade Desk",
    "gumgum": "GumGum",
    "medianet": "Media.net",
    "conversant": "Conversant",
    "ogury": "Ogury",
    "unruly": "Unruly",
    "yieldmo": "Yieldmo",
    "kargo": "Kargo",
    "sonobi": "Sonobi",
    "rhythmone": "RhythmOne",
}


@dataclass
class HeaderAuction:
    detected: bool
    wrapper: str
    markers: list[str] = field(default_factory=list)
    adapters: list[str] = field(default_factory=list)
    bidder_orgs: list[str] = field(default_factory=list)
    timeout_ms: int | None = None
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return asdict(self)


def inspect_header_auction(html: str) -> HeaderAuction:
    blob = html or ""
    lower = blob.lower()
    markers = [m for m in ("prebid.js", "pbjs", "pbjs.que", "headerbidding", "apstag", "amazon-adsystem") if m in lower]
    detected = bool(markers) or bool(re.search(r"prebid", lower))

    adapters: list[str] = []
    for hint, org in ADAPTER_HINTS.items():
        if re.search(rf"['\"]{re.escape(hint)}['\"]", blob, flags=re.I) or hint.lower() in lower:
            adapters.append(org)
    adapters = list(dict.fromkeys(adapters))

    timeout = None
    tm = re.search(r"bidderTimeout[\"'\s:]*([0-9]{3,5})", blob, flags=re.I)
    if tm:
        timeout = int(tm.group(1))

    wrapper = "unknown"
    if "prebid" in lower:
        wrapper = "prebid"
    elif "apstag" in lower or "amazon-adsystem" in lower:
        wrapper = "amazon-aps"
    elif "googletag" in lower and detected:
        wrapper = "gpt-plus-auction"

    notes: list[str] = []
    if detected:
        notes.append(
            "Client-side auction scripts are present. Losing bids as well as the winner can be visible to page JS."
        )
    else:
        notes.append(
            "No client wrapper found. Inventory may still sell via GAM waterfall or server-to-server auctions."
        )
    if timeout:
        notes.append(f"Configured bidder timeout looks like {timeout} ms.")

    orgs = list(dict.fromkeys(adapters))
    return HeaderAuction(
        detected=detected,
        wrapper=wrapper,
        markers=markers,
        adapters=adapters,
        bidder_orgs=orgs,
        timeout_ms=timeout,
        notes=notes,
    )


def hosts_from_html(html: str) -> list[str]:
    found = re.findall(r"https?://([^/\"'\s>]+)", html or "", flags=re.I)
    return list(dict.fromkeys(h.lower() for h in found))


def parties_on_page(html: str) -> list[dict]:
    rows = []
    seen = set()
    for host in hosts_from_html(html):
        org = org_for_host(host)
        if not org or org.name in seen:
            continue
        seen.add(org.name)
        rows.append({"org": org.name, "role": org.role, "host": host})
    return rows
