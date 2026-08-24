from __future__ import annotations

import re
from typing import Iterable

from deep_ad_slot.models import AdTechHit, LayoutSignals, PageSnapshot, Placement

AD_TECH = [
    ("Google AdSense", r"adsbygoogle|googlesyndication\.com/pagead", "network"),
    ("Google Ad Manager / GPT", r"gpt\.js|securepubads\.g\.doubleclick\.net|googletag", "exchange"),
    ("Prebid", r"prebid\.js|pbjs\.", "header-bidding"),
    ("Amazon TAM / APS", r"amazon-adsystem\.com|apstag", "header-bidding"),
    ("Index Exchange", r"casalemedia\.com|indexww", "exchange"),
    ("OpenX", r"openx\.net", "exchange"),
    ("PubMatic", r"pubmatic\.com", "exchange"),
    ("Rubicon / Magnite", r"rubiconproject\.com|magnite", "exchange"),
    ("Taboola", r"taboola\.com|tbla", "native"),
    ("Outbrain", r"outbrain\.com", "native"),
    ("Criteo", r"criteo\.com|criteo\.net", "retargeting"),
    ("Media.net", r"media\.net", "network"),
    ("Ezoic", r"ezoic\.net|ezstandalone", "optimization"),
    ("Mediavine", r"mediavine\.com", "network"),
    ("Raptive / AdThrive", r"adthrive|raptive", "network"),
    ("Playwire", r"playwire\.com", "network"),
    ("Snigel", r"snigelweb\.com", "network"),
    ("Carbon Ads", r"carbonads\.net", "network"),
    ("Meta Pixel", r"connect\.facebook\.net|fbq\(", "tracking"),
    ("Google Analytics / gtag", r"gtag\(|googletagmanager\.com", "tracking"),
]


def detect_ad_tech(pages: Iterable[PageSnapshot]) -> list[AdTechHit]:
    blob = "\n".join((p.html or "") + " " + (p.text or "") for p in pages)
    hits: list[AdTechHit] = []
    for name, pattern, category in AD_TECH:
        match = re.search(pattern, blob, flags=re.I)
        if match:
            hits.append(AdTechHit(name=name, evidence=match.group(0)[:80], category=category))
    return hits


def infer_layout(pages: list[PageSnapshot]) -> LayoutSignals:
    primary = next((p for p in pages if p.html and not p.error), pages[0] if pages else None)
    if not primary or not primary.html:
        return LayoutSignals()
    html = primary.html.lower()
    text = primary.text.lower()
    para_count = len(re.findall(r"<p[\s>]", html))
    image_count = len(re.findall(r"<img[\s>]", html))
    has_article = bool(re.search(r"<article[\s>]|itemprop=[\"']articlebody", html))
    has_sidebar = bool(re.search(r"aside|sidebar|rail", html))
    has_header = bool(re.search(r"<header[\s>]", html))
    has_nav = bool(re.search(r"<nav[\s>]", html))
    has_footer = bool(re.search(r"<footer[\s>]", html))
    viewport = ""
    vm = re.search(r"<meta[^>]+name=[\"']viewport[\"'][^>]*>", html)
    if vm:
        viewport = vm.group(0)[:180]

    words = primary.word_count
    if words > 1200 or para_count >= 8:
        depth = "long-form"
    elif words > 400 or para_count >= 4:
        depth = "standard"
    else:
        depth = "thin"

    page_type = "marketing"
    clues = " ".join([primary.title, text[:1500], " ".join(primary.headings)])
    if re.search(r"add to cart|buy now|sku|product", clues):
        page_type = "ecommerce"
    elif has_article or re.search(r"posted|comments|min read|blog", clues):
        page_type = "article"
    elif re.search(r"breaking|latest news|world|politics", clues):
        page_type = "news"
    elif depth == "thin" and (has_nav or has_header):
        page_type = "homepage"

    return LayoutSignals(
        has_header=has_header,
        has_nav=has_nav,
        has_article=has_article,
        has_sidebar=has_sidebar,
        has_footer=has_footer,
        paragraph_count=para_count,
        image_count=image_count,
        viewport=viewport,
        likely_page_type=page_type,
        content_depth=depth,
    )


def recommend_placements(layout: LayoutSignals, ad_tech: list[AdTechHit]) -> list[Placement]:
    already_monetized = any(h.category in {"network", "exchange", "header-bidding", "native"} for h in ad_tech)
    catalog = [
        {
            "slot_id": "atf-leaderboard",
            "name": "Above-the-fold leaderboard (below nav)",
            "base": 88,
            "devices": ["desktop", "tablet", "mobile"],
            "formats": ["728x90", "970x250", "320x50", "320x100"],
            "where": "Immediately under site navigation, above the H1. Do not place above the logo/nav.",
            "why": "First-view inventory with strong viewability. Advertisers pay a premium for guaranteed first impression.",
            "viewability": "55–75% typical; 80%+ when pinned just under nav",
            "implementation": "Reserve height to avoid CLS. Load GPT/AdSense in <head>, render unit after <nav>.",
            "caveats": "A unit above the nav can trip layout-shift and look like an interstitial.",
            "fit": "homepage" if layout.likely_page_type in {"homepage", "news", "marketing"} else "all templates",
        },
        {
            "slot_id": "incontent-p2",
            "name": "In-content unit after paragraph 2",
            "base": 94,
            "devices": ["desktop", "tablet", "mobile"],
            "formats": ["300x250", "336x280", "fluid native", "outstream video"],
            "where": "After the second paragraph of the article body, before the reader is committed to bounce.",
            "why": "Usually the highest RPM in-article slot. Readers are engaged and the unit sits in the reading path.",
            "viewability": "65–80%",
            "implementation": "Insert server-side or via CMS hook after the 2nd <p>. Prefer lazy-load once 50% in view.",
            "caveats": "Skip on pages with fewer than 3 short paragraphs.",
            "fit": "article templates",
        },
        {
            "slot_id": "sticky-sidebar",
            "name": "Sticky right rail",
            "base": 90,
            "devices": ["desktop"],
            "formats": ["300x600", "160x600", "300x250 stacked"],
            "where": "Right sidebar, sticky within the article column while the user scrolls.",
            "why": "Long time-in-view. Desktop sticky rails often command the highest relative CPM of any display unit.",
            "viewability": "75–85%",
            "implementation": "position:sticky on a 300px rail. Stop before the footer. Cap refresh at 30s in-view.",
            "caveats": "Desktop only. Do not clone onto mobile — it wrecks UX and density.",
            "fit": "desktop article / news",
        },
        {
            "slot_id": "mobile-sticky-footer",
            "name": "Mobile sticky footer",
            "base": 91,
            "devices": ["mobile"],
            "formats": ["320x50", "320x100", "anchor ad"],
            "where": "Pinned to the bottom of the mobile viewport with a visible close control.",
            "why": "Highest mobile viewability after in-content. Strong fill from app-like anchor demand.",
            "viewability": "70–80%",
            "implementation": "Use an anchor format (AdSense anchor / GAM sticky). Keep under 100px tall. Collapsible.",
            "caveats": "Google may treat poorly implemented sticky ads as intrusive interstitials.",
            "fit": "all mobile templates",
        },
        {
            "slot_id": "mid-article",
            "name": "Mid-article in-content",
            "base": 78,
            "devices": ["desktop", "tablet", "mobile"],
            "formats": ["300x250", "fluid", "outstream"],
            "where": "Around 50% scroll / paragraph 5–7 on long-form pages.",
            "why": "Second reading-path impression. Pairs well with P2 without stacking ads on top of each other.",
            "viewability": "55–70%",
            "implementation": "Only render if article word count > 700. Keep 400px+ of content between units.",
            "caveats": "Thin pages should not get this slot.",
            "fit": "long-form article",
        },
        {
            "slot_id": "end-of-article",
            "name": "End of article + recirculation",
            "base": 70,
            "devices": ["desktop", "tablet", "mobile"],
            "formats": ["native 1x3", "300x250", "728x90"],
            "where": "After the last paragraph, before related posts / comments.",
            "why": "Readers who finish are high-intent. Native recommendation widgets work well here.",
            "viewability": "50–70%",
            "implementation": "Native (Taboola-style or first-party related + one display). Avoid dumping 4 rectangles.",
            "caveats": "Low view-time if bounce is high. Do not replace related content entirely.",
            "fit": "article / news",
        },
        {
            "slot_id": "in-feed-home",
            "name": "Homepage / category in-feed native",
            "base": 74,
            "devices": ["desktop", "tablet", "mobile"],
            "formats": ["native in-feed", "fluid"],
            "where": "Every 4–6 cards in a homepage or category grid.",
            "why": "Matches the content rhythm. Better UX than stacking leaderboards on an index page.",
            "viewability": "50–70%",
            "implementation": "Mark as sponsored. Match card typography. Cap density so ads stay under ~30% of viewport.",
            "caveats": "Too many in-feed units trains banner blindness and hurts SEO crawl of real stories.",
            "fit": "homepage / category",
        },
        {
            "slot_id": "outstream-video",
            "name": "In-content outstream video",
            "base": 86,
            "devices": ["desktop", "tablet", "mobile"],
            "formats": ["outstream", "instream companion"],
            "where": "After paragraph 3–4 on articles with images or existing video.",
            "why": "Video CPMs are often several times display. Outstream avoids needing a player inventory.",
            "viewability": "60–75%",
            "implementation": "Initiate only when 50% in view. Mute autoplay. Offer a close button.",
            "caveats": "Can crush Core Web Vitals if the player is heavy. Measure LCP/INP after launch.",
            "fit": "article with media",
        },
    ]

    ranked: list[Placement] = []
    for item in catalog:
        score = float(item["base"])
        if item["slot_id"] == "sticky-sidebar" and not layout.has_sidebar:
            score -= 18
            item = {**item, "caveats": item["caveats"] + " Current HTML does not show a clear sidebar — add a rail first."}
        if item["slot_id"] in {"incontent-p2", "mid-article", "end-of-article", "outstream-video"}:
            if layout.content_depth == "thin":
                score -= 22
            elif layout.content_depth == "long-form":
                score += 6
            if layout.likely_page_type in {"article", "news"}:
                score += 4
        if item["slot_id"] == "in-feed-home" and layout.likely_page_type in {"homepage", "marketing"}:
            score += 8
        if item["slot_id"] == "atf-leaderboard" and (layout.has_nav or layout.has_header):
            score += 3
        if already_monetized and item["slot_id"] == "outstream-video":
            score += 3
        score = max(35.0, min(99.0, score))
        value = "very high" if score >= 88 else "high" if score >= 78 else "medium" if score >= 65 else "situational"
        ranked.append(
            Placement(
                rank=0,
                slot_id=item["slot_id"],
                name=item["name"],
                score=round(score, 1),
                estimated_value=value,
                devices=item["devices"],
                formats=item["formats"],
                where=item["where"],
                why=item["why"],
                viewability=item["viewability"],
                implementation=item["implementation"],
                caveats=item["caveats"],
                fit=item["fit"],
            )
        )

    ranked.sort(key=lambda p: p.score, reverse=True)
    for i, placement in enumerate(ranked, start=1):
        placement.rank = i
    return ranked
