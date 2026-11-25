"""CholecT50 challenge-validation folder -> YOLO detection dataset (split by video).

  python scripts/prepare_yolo.py --src <.../cholect50-challenge-val> --out datasets/or_yolo
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from or_intelligence.constants import INSTRUMENTS  # noqa: E402
from or_intelligence.data import cholect50  # noqa: E402


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--src", required=True, help="folder that contains labels/ and videos/")
    ap.add_argument("--out", default="datasets/or_yolo")
    ap.add_argument("--val", type=int, default=1, help="number of validation videos")
    ap.add_argument("--test", type=int, default=1, help="number of test videos")
    ap.add_argument("--seed", type=int, default=0)
    a = ap.parse_args()

    cases = cholect50.load_root(a.src)
    if not cases:
        sys.exit(f"No labels/VID*.json with matching videos/ folders under {a.src}")
    split = cholect50.assign_splits(list(cases), a.val, a.test, a.seed)
    stats = cholect50.export_yolo(a.src, a.out, split)

    print(f"Wrote {a.out}/data.yaml")
    print(f"{'split':<7}{'videos':<22}{'images':>7}  " + "  ".join(f"{n[:6]:>6}" for n in INSTRUMENTS))
    for sp in ("train", "val", "test"):
        s = stats[sp]
        print(f"{sp:<7}{','.join(s['videos']):<22}{s['images']:>7}  " + "  ".join(f"{s['boxes'][n]:>6}" for n in INSTRUMENTS))
    print("\nSplit is by video on purpose (neighbouring frames are near-duplicates). "
          "Classes with very few boxes (hook, scissors, clipper) will have weak metrics; report that honestly.")


if __name__ == "__main__":
    main()
