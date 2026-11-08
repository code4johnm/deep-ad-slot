"""Approval-safe AdSense package for the Cooks Defense brochure site.

The homepage keeps four reserved slots. Only ``#cd-ad-mid`` is a live unit
while the site is thin and under AdSense review. This repo has no numeric
AdSense slot id, so snippets omit ``data-ad-slot``.
"""

from __future__ import annotations

from deep_ad_slot.models import Analysis

DOMAIN = "cooksdefensellc.com"
PUBLISHER_ID = "pub-6397321536815225"
CLIENT_ID = "ca-pub-6397321536815225"
ADS_TXT_LINE = f"google.com, {PUBLISHER_ID}, DIRECT, f08c47fec0942fa0"

# Homepage order. Actions are what the weekly note tells a person to apply.
SLOTS = (
    ("cd-ad-nav", "placeholder"),
    ("cd-ad-mid", "live"),
    ("cd-ad-footer", "placeholder"),
    ("cd-ad-mobile", "placeholder"),
)
LIVE_SLOTS = tuple(slot for slot, action in SLOTS if action == "live")
HOUSE_SLOTS = tuple(slot for slot, action in SLOTS if action == "placeholder")

AD_FREE_SURFACES = (
    "logo",
    "nav",
    "ticker",
    "hero CTAs",
    ".alert-bar",
    "911 / National Human Trafficking Hotline / text 233733",
    "contact form",
    "privacy.html",
    "terms.html",
    "about.html",
    "contact.html",
)

_REVIEW_MARKER = "only #cd-ad-mid is a live AdSense unit"

# Catalog slot_id -> implementation text emitted for this domain.
_IMPLEMENTATION = {
    "atf-leaderboard": (
        "House/sponsor placeholder #cd-ad-nav only. No adsbygoogle tag and no push."
    ),
    "mobile-sticky-footer": (
        "House/sponsor placeholder #cd-ad-mobile only. No adsbygoogle tag and no push."
    ),
    "end-of-article": (
        "House/sponsor placeholder #cd-ad-footer only. No adsbygoogle tag and no push."
    ),
    "in-feed-home": "Do not add an in-feed unit. No fifth placement.",
    "sticky-sidebar": "Do not add a rail unit. No fifth placement.",
    "outstream-video": "Do not add a video unit. No fifth placement.",
    "mid-article": "Do not add a second live unit. #cd-ad-mid is the only AdSense tag.",
    "incontent-p2": (
        "Only live unit is #cd-ad-mid, a 300x250 rectangle after the services section "
        f"and before values. Client {CLIENT_ID}. Omit data-ad-slot. Auto ads stay off."
    ),
}
_DEFAULT_IMPLEMENTATION = (
    "Do not add another live unit. The only AdSense tag is #cd-ad-mid."
)
_CAVEAT = (
    "Thin brochure under AdSense review. Do not add units and do not invent a "
    "numeric data-ad-slot. Auto ads stay off. No ads on "
    + ", ".join(AD_FREE_SURFACES)
    + "."
)


def policy_lines() -> list[str]:
    pages = "privacy.html, terms.html, about.html, contact.html"
    return [
        "Do not invent numeric ad-unit ids. Auto ads stay off.",
        (
            "Cooks Defense review package: only #cd-ad-mid is a live AdSense unit, "
            "after services. #cd-ad-nav, #cd-ad-footer, and #cd-ad-mobile are "
            "house/sponsor placeholders with no adsbygoogle tag."
        ),
        (
            "Do not place ads on the logo, nav, ticker, hero CTAs, .alert-bar, "
            "911 / National Human Trafficking Hotline / text 233733, the contact form, "
            f"or {pages}."
        ),
        f"ads.txt stays {ADS_TXT_LINE}.",
    ]


def package_rows() -> list[dict[str, str]]:
    return [
        {"domain": DOMAIN, "slot": slot, "score": "n/a", "action": action}
        for slot, action in SLOTS
    ]


def apply_cooks_review_package(analysis: Analysis) -> None:
    """Rewrite emitted implementation notes when the audited site is Cooks Defense."""
    if analysis.domain != DOMAIN:
        return
    for slot in analysis.placements:
        slot.caveats = _CAVEAT
        slot.implementation = _IMPLEMENTATION.get(slot.slot_id, _DEFAULT_IMPLEMENTATION)
    note = policy_lines()[1]
    if note not in analysis.sharing_notes:
        analysis.sharing_notes.append(note)
    if _REVIEW_MARKER not in analysis.summary:
        analysis.summary = (analysis.summary.rstrip() + " " + note).strip()
