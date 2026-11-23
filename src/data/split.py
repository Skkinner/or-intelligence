"""Video-level train/val/test split (never by frame).  ⚠ critical integration point

WBS 2.2.2 · Owner: Member A · Branch: feature/member-a-2.2.2-split
Depends on: 2.2.1 · Hands off to: Member B (3.1.1) — tag B in the PR with the split summary table.

Usage:
    python -m src.data.split --yolo data/processed/yolo --seed 42

Outputs (contract C2):
    data/splits/splits.json            {"train": [video ids], "val": [...], "test": [...]}   (tracked in Git)
    data/processed/yolo/{images,labels}/{train,val,test}/
    data/processed/dataset.yaml        Ultralytics format; names from contracts/classes.json

Acceptance:
    - No video ID in more than one split (leakage test in tests/unit/data/test_split.py).
    - Each split contains every class at least 20 times.
    - `yolo detect val data=data/processed/dataset.yaml` loads without errors.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

SPLITS_PATH = Path("data/splits/splits.json")
RATIOS = {"train": 0.70, "val": 0.15, "test": 0.15}


def video_id_from_stem(stem: str) -> str:
    """Return the source video id of a frame file stem ``<video>_<frame>``.

    TODO(A, 2.2.2): confirm the m2cai16 naming pattern and handle it here (e.g. split on the last "_").
    """
    raise NotImplementedError("WBS 2.2.2 (Member A)")


def make_split(video_class_counts: dict[str, dict[int, int]], seed: int = 42) -> dict[str, list[str]]:
    """Deterministically assign whole videos to train/val/test (~70/15/15), stratified so every
    split contains all 6 classes.

    TODO(A, 2.2.2): seeded shuffle + greedy assignment that checks per-class minimums.
    """
    raise NotImplementedError("WBS 2.2.2 (Member A)")


def assert_no_leakage(splits: dict[str, list[str]]) -> None:
    """Raise AssertionError if any video id appears in more than one split."""
    seen: dict[str, str] = {}
    for split_name, videos in splits.items():
        for vid in videos:
            assert vid not in seen, f"video {vid} in both {seen[vid]} and {split_name}"
            seen[vid] = split_name


def write_dataset_yaml(out_path: Path, yolo_root: Path) -> None:
    """Write Ultralytics dataset.yaml with names from contracts/classes.json.

    TODO(A, 2.2.2): use src.common.contracts.class_names().
    """
    raise NotImplementedError("WBS 2.2.2 (Member A)")


def save_splits(splits: dict[str, list[str]], path: Path = SPLITS_PATH) -> None:
    assert_no_leakage(splits)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(splits, indent=2), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--yolo", type=Path, default=Path("data/processed/yolo"))
    parser.add_argument("--seed", type=int, default=42)
    parser.parse_args()
    raise NotImplementedError("WBS 2.2.2 (Member A): wire up make_split -> move files -> save_splits")


if __name__ == "__main__":
    main()
