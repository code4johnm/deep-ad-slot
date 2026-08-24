from __future__ import annotations

import re
from dataclasses import asdict, dataclass
from urllib.parse import parse_qs, urlparse

from adslot_scout.orgs import org_for_host

SYNC_PARAMS = {
    "userid",
    "user_id",
    "uid",
    "uuid",
    "partnerid",
    "partner_id",
    "partneruid",
    "buyeruid",
    "google_gid",
    "google_nid",
    "id",
    "external_user_id",
    "uid2",
}

SYNC_PATH_HINTS = ("/setuid", "/sync", "/pixel", "/match", "/usersync", "/getuid", "/cookie_sync")


@dataclass
class SyncEvent:
    url: str
    source_org: str | None
    dest_host: str
    dest_org: str | None
    param: str
    kind: str

    def to_dict(self) -> dict:
        return asdict(self)


def extract_urls(html: str) -> list[str]:
    return re.findall(r"https?://[^\"'\s<>]+", html or "", flags=re.I)


def detect_cookie_syncs(html: str) -> list[SyncEvent]:
    events: list[SyncEvent] = []
    for raw in extract_urls(html):
        parsed = urlparse(raw)
        host = parsed.netloc.lower()
        path = parsed.path.lower()
        qs = {k.lower(): v for k, v in parse_qs(parsed.query).items()}
        dest = org_for_host(host)
        hit_param = next((p for p in SYNC_PARAMS if p in qs), None)
        path_hit = any(h in path for h in SYNC_PATH_HINTS)
        if not hit_param and not path_hit:
            continue
        events.append(
            SyncEvent(
                url=raw[:240],
                source_org=None,
                dest_host=host,
                dest_org=dest.name if dest else None,
                param=hit_param or path,
                kind="query-id" if hit_param else "sync-path",
            )
        )
    # Dedup by dest + param
    uniq: dict[tuple[str, str], SyncEvent] = {}
    for ev in events:
        uniq[(ev.dest_host, ev.param)] = ev
    return list(uniq.values())
