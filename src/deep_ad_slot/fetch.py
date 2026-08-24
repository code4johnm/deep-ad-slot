from __future__ import annotations

from collections import deque
from urllib.parse import urljoin, urlparse, urlunparse

import httpx
from bs4 import BeautifulSoup

from deep_ad_slot.models import PageSnapshot

USER_AGENT = (
    "Deep-Ad-Slot/0.1 (+https://github.com/code4johnm/deep-ad-slot; "
    "site-audit; contact via repository issues)"
)

SKIP_PREFIXES = (
    "mailto:",
    "tel:",
    "javascript:",
    "#",
)
SKIP_EXT = (
    ".pdf",
    ".jpg",
    ".jpeg",
    ".png",
    ".gif",
    ".webp",
    ".svg",
    ".zip",
    ".mp4",
    ".mp3",
    ".css",
    ".js",
    ".ico",
    ".woff",
    ".woff2",
)


def normalize_url(url: str) -> str:
    parsed = urlparse(url.strip())
    if not parsed.scheme:
        parsed = urlparse("https://" + url.strip())
    path = parsed.path or "/"
    return urlunparse((parsed.scheme, parsed.netloc.lower(), path, "", parsed.query, ""))


def same_domain(url: str, domain: str) -> bool:
    host = urlparse(url).netloc.lower()
    if host.startswith("www."):
        host = host[4:]
    return host == domain or host.endswith("." + domain)


def domain_of(url: str) -> str:
    host = urlparse(url).netloc.lower()
    return host[4:] if host.startswith("www.") else host


def visible_text(soup: BeautifulSoup) -> str:
    for tag in soup(["script", "style", "noscript", "svg", "iframe"]):
        tag.decompose()
    text = soup.get_text(" ", strip=True)
    return " ".join(text.split())


def parse_page(url: str, status: int, html: str) -> PageSnapshot:
    soup = BeautifulSoup(html, "lxml")
    title = (soup.title.string or "").strip() if soup.title else ""
    desc = ""
    meta = soup.find("meta", attrs={"name": "description"}) or soup.find(
        "meta", attrs={"property": "og:description"}
    )
    if meta and meta.get("content"):
        desc = meta["content"].strip()
    canonical = ""
    link = soup.find("link", rel=lambda v: v and "canonical" in v)
    if link and link.get("href"):
        canonical = urljoin(url, link["href"])
    headings = [
        h.get_text(" ", strip=True)
        for h in soup.find_all(["h1", "h2", "h3"])
        if h.get_text(strip=True)
    ][:40]
    text = visible_text(BeautifulSoup(html, "lxml"))
    links: list[str] = []
    for a in soup.find_all("a", href=True):
        href = a["href"].strip()
        if not href or href.lower().startswith(SKIP_PREFIXES):
            continue
        abs_url = normalize_url(urljoin(url, href))
        path = urlparse(abs_url).path.lower()
        if any(path.endswith(ext) for ext in SKIP_EXT):
            continue
        links.append(abs_url)
    return PageSnapshot(
        url=url,
        status=status,
        title=title,
        description=desc,
        canonical=canonical,
        headings=headings,
        text=text[:20000],
        word_count=len(text.split()),
        links=list(dict.fromkeys(links)),
        html=html,
    )


def fetch_site(seed: str, max_pages: int = 5, timeout: float = 20.0) -> list[PageSnapshot]:
    seed = normalize_url(seed)
    domain = domain_of(seed)
    seen: set[str] = set()
    queue: deque[str] = deque([seed])
    pages: list[PageSnapshot] = []

    headers = {"User-Agent": USER_AGENT, "Accept": "text/html,application/xhtml+xml"}
    with httpx.Client(follow_redirects=True, timeout=timeout, headers=headers) as client:
        while queue and len(pages) < max_pages:
            url = queue.popleft()
            if url in seen:
                continue
            seen.add(url)
            try:
                response = client.get(url)
                content_type = response.headers.get("content-type", "")
                if "html" not in content_type.lower() and not response.text.lstrip().lower().startswith(
                    ("<!doctype", "<html")
                ):
                    pages.append(
                        PageSnapshot(url=str(response.url), status=response.status_code, error="not html")
                    )
                    continue
                snap = parse_page(str(response.url), response.status_code, response.text)
                pages.append(snap)
                for link in snap.links:
                    if same_domain(link, domain) and link not in seen and len(seen) + len(queue) < max_pages * 4:
                        queue.append(link)
            except httpx.HTTPError as exc:
                pages.append(PageSnapshot(url=url, status=0, error=str(exc)))
    return pages
