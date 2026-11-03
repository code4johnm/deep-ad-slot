"""The weekly note is short, local, and does not call a model."""

from deep_ad_slot.models import Analysis, LayoutSignals, Placement
from deep_ad_slot.weekly import build_message, decide


def _slot(slot_id: str, rank: int, score: float) -> Placement:
    return Placement(
        rank=rank,
        slot_id=slot_id,
        name=slot_id,
        score=score,
        estimated_value="",
        devices=["desktop"],
        formats=["display"],
        where="",
        why="",
        viewability="",
        implementation="",
        caveats="",
        fit="",
    )


def _analysis() -> Analysis:
    return Analysis(
        seed_url="https://example.com",
        domain="example.com",
        pages=[],
        layout=LayoutSignals(),
        ad_tech=[],
        placements=[
            _slot("nav-leaderboard", 1, 91),
            _slot("in-content-outstream", 2, 95),
            _slot("mid-native", 3, 88),
        ],
        keywords=[],
        summary="",
    )


def test_low_viewability_moves_a_high_layout_score() -> None:
    assert decide(91, {"impressions": 80, "viewable_rate": 0.1}) == "move"
    assert decide(91, {}) == "keep"


def test_message_skips_video_and_stays_short() -> None:
    message = build_message([_analysis()], stamp="20261103T000000Z")
    assert message["to"] == "grok-bot"
    assert "in-content-outstream" not in message["text"]
    assert "nav-leaderboard" in message["text"]
    assert "2FA" in message["text"]
    assert len(message["text"]) < 4000
    assert "http" not in message["text"].split("Use ")[-1]
