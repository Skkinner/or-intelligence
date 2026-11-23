"""Timeline evaluation vs ground truth (success measure 2).

WBS 4.1.3 · Owner: Member C · Branch: feature/member-c-4.1.3-timeline-eval
Depends on: 4.1.2, 2.3.1 (Member A's presence CSVs, contract C3), 3.3.1 (Member B's detect_video, unchanged)
Read-only consumer: Member B (6.1.1 benchmark). Signature changes go through Member C.

Usage:
    python -m src.timeline.evaluate --pred storage/timelines/video41.json --gt data/processed/presence/video41.csv

Metrics: per-tool frame-level precision / recall / F1 at 1 fps, segment IoU, overall macro-F1.
Write results + one example timeline plot per video to docs/timeline/TIMELINE_EVAL.md.

Acceptance:
    - Per-tool F1 table for raw vs smoothed on held-out timeline videos.
    - Tuning and reporting videos are disjoint (stated).
    - Smoothed macro-F1 >= raw macro-F1 (report honestly if not).
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np


def timeline_to_presence(timeline: dict, n_seconds: int) -> np.ndarray:
    """Rasterise C5 segments to a [n_seconds, 6] 0/1 array at 1 fps.  TODO(C, 4.1.3)"""
    raise NotImplementedError("WBS 4.1.3 (Member C)")


def load_presence_csv(path: str | Path) -> np.ndarray:
    """Load a C3 CSV into a [n_seconds, 6] 0/1 array.  TODO(C, 4.1.3)"""
    raise NotImplementedError("WBS 4.1.3 (Member C)")


def evaluate_video(timeline: dict, presence_csv: str) -> dict:
    """Return {"per_tool": {name: {"precision", "recall", "f1", "seg_iou"}}, "macro_f1": float}.

    TODO(C, 4.1.3)
    """
    raise NotImplementedError("WBS 4.1.3 (Member C)")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pred", type=Path, required=True)
    parser.add_argument("--gt", type=Path, required=True)
    args = parser.parse_args()
    result = evaluate_video(json.loads(args.pred.read_text()), str(args.gt))
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
