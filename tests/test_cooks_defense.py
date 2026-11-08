"""The Cooks Defense package has one live unit and matching notes."""

import re
from html.parser import HTMLParser
from pathlib import Path

from deep_ad_slot.cooks_defense import (
    CLIENT_ID,
    DOMAIN,
    HOUSE_SLOTS,
    LIVE_SLOTS,
    PUBLISHER_ID,
    SLOTS,
    apply_cooks_review_package,
    package_rows,
)
from deep_ad_slot.models import Analysis, LayoutSignals, Placement
from deep_ad_slot.report import render_markdown
from deep_ad_slot.weekly import build_message

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "examples" / "cooksdefensellc"


def _slot(slot_id: str, rank: int, score: float) -> Placement:
    return Placement(
        rank=rank,
        slot_id=slot_id,
        name=slot_id,
        score=score,
        estimated_value="high",
        devices=["desktop"],
        formats=["display"],
        where="after the nav",
        why="",
        viewability="",
        implementation="Load AdSense after the nav.",
        caveats="",
        fit="",
    )


def _analysis() -> Analysis:
    return Analysis(
        seed_url=f"https://{DOMAIN}/",
        domain=DOMAIN,
        pages=[],
        layout=LayoutSignals(),
        ad_tech=[],
        placements=[
            _slot("atf-leaderboard", 1, 91),
            _slot("mobile-sticky-footer", 2, 91),
            _slot("in-feed-home", 3, 82),
            _slot("incontent-p2", 4, 72),
            _slot("end-of-article", 5, 48),
        ],
        keywords=[],
        summary="Highest-value slots: above the fold.",
    )


class _SlotParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.stack: list[str | None] = []
        self.slots: list[str] = []
        self.ins: list[tuple[str | None, dict[str, str]]] = []
        self.bad_attrs: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        data = {key: value or "" for key, value in attrs}
        if "data-ad-slot" in data:
            self.bad_attrs.append(tag)
        if tag == "div":
            slot_id = data.get("id")
            self.stack.append(slot_id)
            if slot_id and slot_id.startswith("cd-ad-") and not slot_id.endswith("-close"):
                self.slots.append(slot_id)
        if tag == "ins" and "adsbygoogle" in data.get("class", "").split():
            owner = next(
                (item for item in reversed(self.stack) if item and item.startswith("cd-ad-")),
                None,
            )
            self.ins.append((owner, data))

    def handle_endtag(self, tag: str) -> None:
        if tag == "div" and self.stack:
            self.stack.pop()


def _comments_for_slots(html: str) -> dict[str, str]:
    found: dict[str, str] = {}
    pattern = re.compile(r"<!--(.*?)-->\s*<div\b[^>]*\bid=\"(cd-ad-[^\"]+)\"", re.S)
    for comment, slot_id in pattern.findall(html):
        found[slot_id] = comment
    return found


def test_slots_markup_has_one_live_unit() -> None:
    html = (PACKAGE / "slots.html").read_text(encoding="utf-8")
    parser = _SlotParser()
    parser.feed(html)
    assert parser.bad_attrs == []
    assert parser.slots == [slot for slot, _action in SLOTS]
    assert [owner for owner, _attrs in parser.ins] == list(LIVE_SLOTS)
    blob = "\n".join(path.read_text(encoding="utf-8") for path in PACKAGE.iterdir() if path.is_file())
    assert set(re.findall(r"ca-pub-\d+|pub-\d+", blob)) == {CLIENT_ID, PUBLISHER_ID}
    _owner, attrs = parser.ins[0]
    assert attrs["data-ad-client"] == CLIENT_ID
    assert "data-ad-slot" not in attrs
    assert "enable_page_level_ads" not in html
    assert html.count("<ins") == 1

    comments = _comments_for_slots(html)
    for slot_id in HOUSE_SLOTS:
        text = comments[slot_id].lower()
        assert "house/sponsor only" in text
        assert "no adsbygoogle" in text
    live = comments["cd-ad-mid"].lower()
    assert "single live adsense review unit" in live
    assert "house/sponsor only" not in live
    assert CLIENT_ID in comments["cd-ad-mid"]


def test_push_targets_only_the_review_unit() -> None:
    script = (PACKAGE / "page-ads.js").read_text(encoding="utf-8")
    head = (PACKAGE / "index-head.html").read_text(encoding="utf-8")
    assert script.count(".push({})") == 1
    assert "querySelectorAll('#cd-ad-mid ins.adsbygoogle')" in script
    for banned in ("#cd-ad-nav", "#cd-ad-footer", "#cd-ad-mobile"):
        assert f"querySelectorAll('{banned}" not in script
        assert f"querySelector('{banned} ins" not in script
    assert "ins.adsbygoogle" not in script.split("#cd-ad-mid ins.adsbygoogle", 1)[-1]
    assert re.search(r"enable_page_level_ads\s*[:=]", script) is None
    assert re.search(r"enable_page_level_ads\s*[:=]", head) is None
    assert "Auto ads stay off" in script
    assert "Auto ads stay off" in head
    assert f"client={CLIENT_ID}" in head
    assert "<ins" not in head
    for page in ("privacy.html", "terms.html", "about.html", "contact.html"):
        assert page in head


def test_docs_match_the_single_live_unit() -> None:
    readme = (PACKAGE / "README.md").read_text(encoding="utf-8")
    assert PUBLISHER_ID in readme
    assert CLIENT_ID in readme
    assert "Auto ads stay off" in readme
    assert "data-ad-slot" in readme
    for slot_id in (*HOUSE_SLOTS, *LIVE_SLOTS):
        assert f"#{slot_id}" in readme
    for page in ("privacy.html", "terms.html", "about.html", "contact.html"):
        assert page in readme
    assert "house/sponsor" in readme.lower()
    assert "only live AdSense unit" in readme or "only live unit" in readme or "Only `#cd-ad-mid`" in readme


def test_weekly_note_uses_the_review_package() -> None:
    message = build_message([_analysis()], stamp="20261108T000000Z")
    text = message["text"]
    assert "atf-leaderboard" not in text
    assert "mobile-sticky-footer" not in text
    for row in package_rows():
        assert f"{DOMAIN} {row['slot']} score n/a action {row['action']}" in text
    assert "only #cd-ad-mid is a live AdSense unit" in text
    assert "Auto ads stay off" in text
    assert PUBLISHER_ID in text
    assert "2FA" in text
    assert len(text) < 4000


def test_analyze_notes_do_not_tell_cooks_to_tag_the_nav() -> None:
    analysis = _analysis()
    apply_cooks_review_package(analysis)
    report = render_markdown(analysis)
    assert "Load AdSense after the nav." not in report
    assert "House/sponsor placeholder #cd-ad-nav only." in report
    assert "House/sponsor placeholder #cd-ad-mobile only." in report
    assert "House/sponsor placeholder #cd-ad-footer only." in report
    assert f"Client {CLIENT_ID}" in report
    assert "only #cd-ad-mid is a live AdSense unit" in report
    other = _analysis()
    other.domain = "example.com"
    apply_cooks_review_package(other)
    assert other.placements[0].implementation == "Load AdSense after the nav."
