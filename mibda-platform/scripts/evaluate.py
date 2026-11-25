"""Evaluate weights on the held-out split and write models/metrics.json (shown in the app's Model page).

  python scripts/evaluate.py --data datasets/or_yolo/data.yaml --split test
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from or_intelligence.constants import INSTRUMENTS  # noqa: E402


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--data", required=True)
    ap.add_argument("--weights", default=str(ROOT / "models" / "best.pt"))
    ap.add_argument("--split", default="test", choices=["val", "test"])
    ap.add_argument("--imgsz", type=int, default=640)
    ap.add_argument("--device", default=None)
    a = ap.parse_args()

    from ultralytics import YOLO

    res = YOLO(a.weights).val(data=a.data, split=a.split, imgsz=a.imgsz, device=a.device, plots=True,
                              project=str(ROOT / "runs"), name=f"eval_{a.split}", exist_ok=True)
    b = res.box
    per_class = {}
    for pos, cls_idx in enumerate(b.ap_class_index):
        per_class[INSTRUMENTS[int(cls_idx)]] = {
            "precision": float(b.p[pos]), "recall": float(b.r[pos]),
            "map50": float(b.ap50[pos]), "map50_95": float(b.ap[pos]),
        }
    out = {
        "split": a.split, "weights": Path(a.weights).name, "data": a.data,
        "overall": {"precision": float(b.mp), "recall": float(b.mr), "map50": float(b.map50), "map50_95": float(b.map)},
        "per_class": per_class,
        "classes_missing_from_split": [n for n in INSTRUMENTS if n not in per_class],
        "evaluated_at": time.strftime("%Y-%m-%d %H:%M"),
    }
    (ROOT / "models").mkdir(exist_ok=True)
    (ROOT / "models" / "metrics.json").write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
