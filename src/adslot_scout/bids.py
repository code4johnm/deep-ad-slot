from __future__ import annotations

import csv
import math
from collections import defaultdict
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable


@dataclass
class BidRow:
    bidder: str
    cpm: float
    tracker_flags: dict[str, int]
    persona: str = ""
    site: str = ""

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class BidBandStats:
    mean: float
    stdev: float
    zero_rate: float
    n: int

    def classify(self, cpm: float) -> str:
        if self.stdev <= 0:
            return "medium"
        if cpm >= self.mean + self.stdev:
            return "high"
        if cpm <= max(0.0, self.mean - self.stdev):
            return "low"
        return "medium"


def band_stats(cpms: Iterable[float]) -> BidBandStats:
    values = list(cpms)
    n = len(values)
    if n == 0:
        return BidBandStats(0.0, 0.0, 0.0, 0)
    mean = sum(values) / n
    var = sum((v - mean) ** 2 for v in values) / n
    zeros = sum(1 for v in values if v <= 0)
    return BidBandStats(mean=mean, stdev=math.sqrt(var), zero_rate=zeros / n, n=n)


def load_bid_csv(path: Path) -> list[BidRow]:
    """CSV columns: bidder,cpm,persona,site plus optional tracker_* flags (0/1)."""
    rows: list[BidRow] = []
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        for raw in reader:
            flags = {k[8:]: int(v or 0) for k, v in raw.items() if k.startswith("tracker_")}
            rows.append(
                BidRow(
                    bidder=raw.get("bidder", "unknown"),
                    cpm=float(raw.get("cpm") or 0),
                    tracker_flags=flags,
                    persona=raw.get("persona", ""),
                    site=raw.get("site", ""),
                )
            )
    return rows


def influence_table(rows: list[BidRow], top_k: int = 3) -> dict[str, list[dict]]:
    """Rank trackers by how much mean CPM moves when the tracker flag flips."""
    by_bidder: dict[str, list[BidRow]] = defaultdict(list)
    for row in rows:
        by_bidder[row.bidder].append(row)

    out: dict[str, list[dict]] = {}
    for bidder, group in by_bidder.items():
        trackers = sorted({name for row in group for name in row.tracker_flags})
        ranked = []
        for tracker in trackers:
            on = [r.cpm for r in group if r.tracker_flags.get(tracker, 0) == 1]
            off = [r.cpm for r in group if r.tracker_flags.get(tracker, 0) == 0]
            if not on or not off:
                continue
            delta = (sum(on) / len(on)) - (sum(off) / len(off))
            ranked.append(
                {
                    "tracker": tracker,
                    "delta_cpm": round(delta, 4),
                    "n_on": len(on),
                    "n_off": len(off),
                    "channel": "client-or-server",
                }
            )
        ranked.sort(key=lambda item: abs(item["delta_cpm"]), reverse=True)
        out[bidder] = ranked[:top_k]
    return out


def try_forest_importance(rows: list[BidRow]) -> dict[str, list[dict]] | None:
    try:
        from sklearn.ensemble import RandomForestClassifier  # type: ignore
        import numpy as np  # type: ignore
    except Exception:
        return None

    by_bidder: dict[str, list[BidRow]] = defaultdict(list)
    for row in rows:
        by_bidder[row.bidder].append(row)
    result: dict[str, list[dict]] = {}
    for bidder, group in by_bidder.items():
        trackers = sorted({name for row in group for name in row.tracker_flags})
        if len(group) < 20 or not trackers:
            continue
        stats = band_stats(r.cpm for r in group)
        X = np.array([[r.tracker_flags.get(t, 0) for t in trackers] for r in group])
        y = np.array([stats.classify(r.cpm) for r in group])
        if len(set(y)) < 2:
            continue
        model = RandomForestClassifier(n_estimators=200, random_state=7)
        model.fit(X, y)
        ranked = sorted(
            ({"tracker": t, "importance": round(float(i), 4)} for t, i in zip(trackers, model.feature_importances_)),
            key=lambda item: item["importance"],
            reverse=True,
        )
        result[bidder] = ranked[:5]
    return result
