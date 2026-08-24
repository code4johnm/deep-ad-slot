from __future__ import annotations

from deep_ad_slot.fetch import domain_of, fetch_site, normalize_url
from deep_ad_slot.header_bidding import inspect_header_auction, parties_on_page
from deep_ad_slot.keywords import extract_keywords
from deep_ad_slot.models import Analysis
from deep_ad_slot.placements import detect_ad_tech, infer_layout, recommend_placements
from deep_ad_slot.sync import detect_cookie_syncs


def analyze_site(url: str, max_pages: int = 5) -> Analysis:
    seed = normalize_url(url)
    pages = fetch_site(seed, max_pages=max(1, max_pages))
    layout = infer_layout(pages)
    ad_tech = detect_ad_tech(pages)
    placements = recommend_placements(layout, ad_tech)
    keywords = extract_keywords(pages)
    domain = domain_of(seed)

    html = next((p.html for p in pages if p.html), "")
    auction = inspect_header_auction(html)
    parties = parties_on_page(html)
    syncs = [ev.to_dict() for ev in detect_cookie_syncs(html)]

    notes: list[str] = []
    if auction.detected:
        notes.append(
            "Client auction wrapper found. Bid values from multiple demand partners can be read in page JS."
        )
    else:
        notes.append(
            "No client auction wrapper. Demand may still run server-side; client cookie matching will under-count partners."
        )
    if syncs:
        notes.append(
            f"{len(syncs)} client identifier-match URLs found. These are only the browser-visible edges."
        )
    else:
        notes.append(
            "No client identifier-match URLs in the HTML. Sharing, if any, is likely server-side or loaded after consent."
        )
    bidder_names = ", ".join(auction.bidder_orgs) or "none named in markup"
    notes.append(f"Named demand / adapters: {bidder_names}.")

    top = placements[:3]
    names = ", ".join(p.name for p in top)
    tech = ", ".join(h.name for h in ad_tech) or "no obvious ad stack in the raw HTML"
    summary = (
        f"{domain} looks like a **{layout.likely_page_type}** property with **{layout.content_depth}** copy. "
        f"Highest-value slots: {names}. Stack: {tech}. "
        f"Auction wrapper: {auction.wrapper if auction.detected else 'not in HTML'}."
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
        header_auction=auction.to_dict(),
        parties=parties,
        cookie_syncs=syncs,
        sharing_notes=notes,
    )
