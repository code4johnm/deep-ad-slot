from __future__ import annotations

from urllib.parse import urlparse

import httpx

from deep_ad_slot.fetch import USER_AGENT, domain_of, normalize_url


def fetch_ads_txt(site: str, timeout: float = 15.0) -> list[str]:
    url = normalize_url(site)
    parsed = urlparse(url)
    ads = f"{parsed.scheme}://{parsed.netloc}/ads.txt"
    with httpx.Client(follow_redirects=True, timeout=timeout, headers={"User-Agent": USER_AGENT}) as client:
        response = client.get(ads)
        if response.status_code >= 400:
            return []
        return [line.strip() for line in response.text.splitlines() if line.strip() and not line.startswith("#")]


def summarize_ads_txt(lines: list[str]) -> dict:
    rows = []
    for line in lines:
        parts = [p.strip() for p in line.split(",")]
        if len(parts) < 3:
            continue
        rows.append(
            {
                "exchange": parts[0],
                "publisher_id": parts[1],
                "type": parts[2].lower(),
                "authority": parts[3] if len(parts) > 3 else "",
            }
        )
    return {"domain": domain_of(lines[0]) if False else None, "entries": rows, "count": len(rows)}
