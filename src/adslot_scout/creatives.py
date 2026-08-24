from __future__ import annotations

from collections import Counter
from dataclasses import asdict, dataclass


@dataclass
class CreativeShift:
    advertiser: str
    blocked_tracker: str
    baseline_topics: list[str]
    blocked_topics: list[str]
    jaccard: float
    inferred_share: bool

    def to_dict(self) -> dict:
        return asdict(self)


def _jaccard(a: set[str], b: set[str]) -> float:
    if not a and not b:
        return 1.0
    return len(a & b) / max(1, len(a | b))


def infer_from_creatives(
    baseline: dict[str, list[str]],
    blocked: dict[str, dict[str, list[str]]],
    threshold: float = 0.45,
) -> list[CreativeShift]:
    """Compare topic/brand bags when a tracker org is blocked.

    baseline[advertiser] = topics
    blocked[tracker][advertiser] = topics after that tracker is removed
    A sharp drop in overlap is treated as evidence the advertiser used that tracker.
    """
    shifts: list[CreativeShift] = []
    for tracker, advertisers in blocked.items():
        for advertiser, topics in advertisers.items():
            base = set(t.lower() for t in baseline.get(advertiser, []))
            now = set(t.lower() for t in topics)
            score = _jaccard(base, now)
            shifts.append(
                CreativeShift(
                    advertiser=advertiser,
                    blocked_tracker=tracker,
                    baseline_topics=sorted(base),
                    blocked_topics=sorted(now),
                    jaccard=round(score, 3),
                    inferred_share=score < threshold and bool(base),
                )
            )
    shifts.sort(key=lambda s: s.jaccard)
    return shifts


def topic_histogram(topics: list[str]) -> dict[str, int]:
    return dict(Counter(t.lower() for t in topics))
