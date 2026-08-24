from __future__ import annotations

import math
import re
from collections import Counter
from urllib.parse import urlparse

from deep_ad_slot.models import Keyword, PageSnapshot

STOP = {
    "a", "an", "the", "and", "or", "but", "if", "in", "on", "at", "to", "for", "of", "from",
    "by", "with", "as", "is", "are", "was", "were", "be", "been", "being", "it", "its",
    "this", "that", "these", "those", "you", "your", "we", "our", "they", "their", "he",
    "she", "his", "her", "not", "no", "yes", "can", "will", "just", "about", "into",
    "over", "after", "before", "than", "then", "so", "too", "very", "more", "most",
    "other", "some", "any", "all", "also", "only", "using", "use", "used", "via",
    "home", "page", "click", "here", "privacy", "cookie", "cookies", "terms",
    "contact", "login", "signup", "menu", "search", "skip", "content", "read",
    "more", "share", "follow", "subscribe", "newsletter",
}

COMMERCIAL_MODIFIERS = [
    "best",
    "buy",
    "price",
    "pricing",
    "cost",
    "review",
    "reviews",
    "vs",
    "alternative",
    "near me",
    "software",
    "service",
    "agency",
    "template",
    "examples",
    "guide",
]

TOKEN_RE = re.compile(r"[a-z0-9][a-z0-9'&-]{1,}", re.I)


def tokenize(text: str) -> list[str]:
    return [t.lower() for t in TOKEN_RE.findall(text or "") if t.lower() not in STOP and len(t) > 2]


def ngrams(tokens: list[str], n: int) -> list[str]:
    return [" ".join(tokens[i : i + n]) for i in range(len(tokens) - n + 1)]


def intent_for(phrase: str) -> str:
    if any(m in phrase for m in ("buy", "price", "pricing", "cost", "cheap", "deal")):
        return "transactional"
    if any(m in phrase for m in ("best", "review", "vs", "alternative", "compare")):
        return "commercial"
    if any(m in phrase for m in ("how", "what", "guide", "examples", "tutorial")):
        return "informational"
    return "core"


def extract_keywords(pages: list[PageSnapshot], limit: int = 40) -> list[Keyword]:
    if not pages:
        return []
    weighted: Counter[str] = Counter()
    source_map: dict[str, str] = {}

    def add(phrase: str, weight: float, source: str) -> None:
        phrase = re.sub(r"\s+", " ", phrase.strip().lower())
        if not phrase or len(phrase) < 3:
            return
        tokens = phrase.split()
        if all(t in STOP for t in tokens):
            return
        weighted[phrase] += weight
        source_map.setdefault(phrase, source)

    for page in pages:
        add(page.title, 8, "title")
        add(page.description, 5, "meta")
        host = urlparse(page.url).path.replace("/", " ").replace("-", " ").replace("_", " ")
        for tok in tokenize(host):
            add(tok, 3, "url")
        for heading in page.headings:
            add(heading, 4, "heading")
            for gram in ngrams(tokenize(heading), 2):
                add(gram, 3.5, "heading")
        tokens = tokenize(page.text)
        for n, w in ((1, 1.0), (2, 2.2), (3, 2.8)):
            counts = Counter(ngrams(tokens, n))
            for phrase, count in counts.most_common(80):
                add(phrase, w * math.log(count + 1, 2), "body")

    core = [phrase for phrase, _ in weighted.most_common(18) if 1 <= len(phrase.split()) <= 3]
    for seed in core[:8]:
        if intent_for(seed) == "core":
            for mod in COMMERCIAL_MODIFIERS[:8]:
                if mod not in seed:
                    add(f"{mod} {seed}", 1.6, "expanded")

    ranked: list[Keyword] = []
    for phrase, raw in weighted.most_common(limit * 2):
        n = len(phrase.split())
        if n > 4:
            continue
        ranked.append(
            Keyword(
                phrase=phrase,
                source=source_map.get(phrase, "body"),
                score=round(float(raw), 2),
                intent=intent_for(phrase),
                ngram=n,
            )
        )
        if len(ranked) >= limit:
            break
    return ranked
