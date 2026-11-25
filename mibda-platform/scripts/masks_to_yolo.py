"""Folder of images + folder of binary masks -> YOLO segmentation dataset (generic adapter).

  python scripts/masks_to_yolo.py --images <dir> --masks <dir> --out datasets/kvasir --class-name tool
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from or_intelligence.data import masks  # noqa: E402


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--images", required=True)
    ap.add_argument("--masks", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--class-name", default="tool")
    ap.add_argument("--val", type=float, default=0.1)
    ap.add_argument("--test", type=float, default=0.1)
    a = ap.parse_args()
    print(masks.export_yolo_seg(a.images, a.masks, a.out, a.class_name, 0, a.val, a.test))


if __name__ == "__main__":
    main()
