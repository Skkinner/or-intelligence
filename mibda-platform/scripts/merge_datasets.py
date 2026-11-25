"""Merge YOLO datasets prepared by the other scripts (same task type: all detection or all segmentation).

  python scripts/merge_datasets.py --src chole=datasets/or_yolo --src hyst=datasets/autolaparo_yolo \
      --out datasets/merged --rename "Grasper=grasper" --rename "Needle=None"

--rename OLD=NEW maps a source class name; NEW of "None" drops that class.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from or_intelligence.data import merge  # noqa: E402


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--src", action="append", required=True, help="TAG=DIR (repeat)")
    ap.add_argument("--out", required=True)
    ap.add_argument("--rename", action="append", default=[], help="OLD=NEW or OLD=None (repeat)")
    a = ap.parse_args()
    sources = dict(s.split("=", 1) for s in a.src)
    rename = {k: (None if v == "None" else v) for k, v in (r.split("=", 1) for r in a.rename)}
    stats = merge.merge(sources, a.out, rename)
    print(f"classes: {stats['classes']}")
    print(f"images : {dict(stats['images'])}")
    print(f"boxes  : {dict(stats['instances'])}  dropped: {stats['dropped_instances']}")


if __name__ == "__main__":
    main()
