"""CholecInstanceSeg annotations (zip + metadata CSV) -> YOLO segmentation labels.

The public release has NO images. Pass --images-root once you have frames from the source
datasets (Cholec80 / CholecT50 / CholecSeg8k), laid out as <root>/<VIDxx>/<frame>.png.

  python scripts/prepare_instance_seg.py --zip cholecinstanceseg.zip --csv cholecinstanceseg_metadata.csv --out datasets/or_seg
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from or_intelligence.data import cholecinstanceseg  # noqa: E402


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--zip", required=True)
    ap.add_argument("--csv", required=True)
    ap.add_argument("--out", default="datasets/or_seg")
    ap.add_argument("--images-root", default=None)
    ap.add_argument("--limit", type=int, default=None, help="only convert the first N rows (quick test)")
    a = ap.parse_args()

    stats = cholecinstanceseg.export_yolo_seg(a.zip, a.csv, a.out, a.images_root, a.limit)
    print(f"labels written : {stats['written']}")
    print(f"per split      : {dict(stats['per_split'])}")
    print(f"instances      : {dict(stats['instances'])}")
    if stats["skipped"]:
        print(f"skipped shapes : {dict(stats['skipped'])}")
    if a.images_root:
        print(f"missing images : {stats['missing_images']}")
    else:
        print("No --images-root given: labels only. Training needs the matching frames.")


if __name__ == "__main__":
    main()
