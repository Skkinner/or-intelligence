"""Build 1 fps timeline ground truth CSVs (contract C3) from tool-presence annotations.

WBS 2.3.1 · Owner: Member A · Branch: feature/member-a-2.3.1-presence-gt
Depends on: 2.1.1 · Hands off to: Member C (4.1.3) — tag C in the PR.

Usage:
    python -m src.data.presence_labels --src data/raw/cholec80/tool_annotations --videos video41 video42 video43 \
        --out data/processed/presence

Output: data/processed/presence/<video_id>.csv with header
    t_sec,grasper,bipolar,hook,scissors,clipper,irrigator

Acceptance:
    - Each CSV matches contract C3 (header + 0/1 values).
    - Row count within +-2 s of the video length.
    - Overlap check with training videos documented in docs/data/timeline_eval_set.md.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from src.common.contracts import class_names

HEADER = ["t_sec", *class_names()]


def read_annotation(path: Path) -> list[dict[str, int]]:
    """Read one source annotation file into per-frame dicts.

    TODO(A, 2.3.1): Cholec80 tool annotations are tab-separated at 25 fps with a frame column and one
    column per tool (check the column names; Cholec80 also lists SpecimenBag, which is dropped).
    Map source tool names to the 6 contract classes.
    """
    raise NotImplementedError("WBS 2.3.1 (Member A)")


def to_one_fps(rows: list[dict[str, int]], source_fps: float) -> list[list[int]]:
    """Resample to one row per second: [t_sec, grasper, ..., irrigator].

    TODO(A, 2.3.1): choose and document the rule (e.g. tool present if present in the frame at t_sec).
    """
    raise NotImplementedError("WBS 2.3.1 (Member A)")


def write_csv(rows: list[list[int]], out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8", newline="") as fh:
        fh.write(",".join(HEADER) + "\n")
        for r in rows:
            fh.write(",".join(str(v) for v in r) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--src", type=Path, required=True)
    parser.add_argument("--videos", nargs="+", required=True)
    parser.add_argument("--source-fps", type=float, default=25.0)
    parser.add_argument("--out", type=Path, default=Path("data/processed/presence"))
    parser.parse_args()
    raise NotImplementedError("WBS 2.3.1 (Member A): read -> to_one_fps -> write_csv for each video")


if __name__ == "__main__":
    main()
