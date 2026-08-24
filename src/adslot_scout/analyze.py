from __future__ import annotations

from adslot_scout.fetch import domain_of, fetch_site, normalize_url
from adslot_scout.keywords import extract_keywords
from adslot_scout.models import Analysis
from adslot_scout.placements import detect_ad_tech, infer_layout, recommend_placements


def analyze_site(url: str, max_pages: int = 5) -> Analysis:
    seed = normalize_url(url)
    pages = fetch_site(seed, max_pages=max(1, max_pages))
    layout = infer_layout(pages)
    ad_tech = detect_ad_tech(pages)
    placements = recommend_placements(layout, ad_tech)
    keywords = extract_keywords(pages)
    domain = domain_of(seed)
    top = placements[:3]
    names = ", ".join(p.name for p in top)
    tech = ", ".join(h.name for h in ad_tech) or "no obvious ad stack in the raw HTML"
    summary = (
        f"{domain} looks like a **{layout.likely_page_type}** property with **{layout.content_depth}** copy. "
        f"Highest-value slots on this layout: {names}. Detected stack: {tech}."
    )
    return Analysis(
        seed_url=seed,
        domain=domain,
        pages=pages,
        layout=layout,
        ad_tech=ad_tech,
        placements=placements,
        keywords=keywords,
        summary=summary,
    )
