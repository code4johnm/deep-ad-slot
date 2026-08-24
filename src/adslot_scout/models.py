from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass
class PageSnapshot:
    url: str
    status: int
    title: str = ""
    description: str = ""
    canonical: str = ""
    headings: list[str] = field(default_factory=list)
    text: str = ""
    word_count: int = 0
    links: list[str] = field(default_factory=list)
    html: str = ""
    error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data.pop("html", None)
        return data


@dataclass
class LayoutSignals:
    has_header: bool = False
    has_nav: bool = False
    has_article: bool = False
    has_sidebar: bool = False
    has_footer: bool = False
    paragraph_count: int = 0
    image_count: int = 0
    viewport: str = ""
    likely_page_type: str = "unknown"
    content_depth: str = "thin"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class AdTechHit:
    name: str
    evidence: str
    category: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class Placement:
    rank: int
    slot_id: str
    name: str
    score: float
    estimated_value: str
    devices: list[str]
    formats: list[str]
    where: str
    why: str
    viewability: str
    implementation: str
    caveats: str
    fit: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class Keyword:
    phrase: str
    source: str
    score: float
    intent: str
    ngram: int

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class Analysis:
    seed_url: str
    domain: str
    pages: list[PageSnapshot]
    layout: LayoutSignals
    ad_tech: list[AdTechHit]
    placements: list[Placement]
    keywords: list[Keyword]
    summary: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "seed_url": self.seed_url,
            "domain": self.domain,
            "summary": self.summary,
            "layout": self.layout.to_dict(),
            "ad_tech": [hit.to_dict() for hit in self.ad_tech],
            "placements": [p.to_dict() for p in self.placements],
            "keywords": [k.to_dict() for k in self.keywords],
            "pages": [p.to_dict() for p in self.pages],
        }
