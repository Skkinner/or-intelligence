"""Draw YOLO labels on random images for manual QA.

WBS 2.2.1 · Owner: Member A

Usage:
    python -m src.data.visualize --yolo data/processed/yolo --n 50 --out data/processed/qa

TODO(A, 2.2.1):
  - Pick N random images (seeded), read their .txt labels, draw boxes with the colours from
    contracts/classes.json (src.common.contracts.class_colors) and the class name.
  - Save PNGs to data/processed/qa/ (gitignored). Record findings in docs/data/qa_notes.md.
"""

from __future__ import annotations

import argparse
from pathlib import Path


def render_samples(yolo_dir: Path, n: int, out_dir: Path, seed: int = 42) -> list[Path]:
    raise NotImplementedError("WBS 2.2.1 (Member A)")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--yolo", type=Path, default=Path("data/processed/yolo"))
    parser.add_argument("--n", type=int, default=50)
    parser.add_argument("--out", type=Path, default=Path("data/processed/qa"))
    args = parser.parse_args()
    for p in render_samples(args.yolo, args.n, args.out):
        print(p)


if __name__ == "__main__":
    main()
