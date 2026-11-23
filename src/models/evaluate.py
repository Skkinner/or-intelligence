"""One-time held-out test evaluation of the final detector.

WBS 3.2.1 · Owner: Member B · Branch: feature/member-b-3.2.1-eval
Depends on: 3.1.2 (best.pt) · Hands off to: Member D (7.2.1), recommended conf threshold to Member C.

Usage:
    python -m src.models.evaluate --weights models/weights/best.pt --data data/processed/dataset.yaml

Outputs:
    docs/model/test_metrics.json   mAP@0.5, mAP@0.5:0.95, per-class precision/recall at the chosen conf
    docs/model/figures/            PR curves, confusion matrix, failures/ (20 FN/FP examples)
    docs/model/EVALUATION.md       written by hand from the above

Acceptance:
    - mAP@0.5 and P/R for all 6 instruments on the **test** split.
    - Test split evaluated exactly once (state it in the report).
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

METRICS_PATH = Path("docs/model/test_metrics.json")


def evaluate(weights: str, data: str, conf: float) -> dict:
    """Run ultralytics val on split='test' and return a metrics dict.

    Expected keys: {"map50", "map50_95", "conf", "per_class": {name: {"precision", "recall", "ap50"}},
                    "evaluated_at", "weights_sha256"}

    TODO(B, 3.2.1): YOLO(weights).val(data=data, split="test", conf=conf, plots=True)
    """
    raise NotImplementedError("WBS 3.2.1 (Member B)")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--weights", default="models/weights/best.pt")
    parser.add_argument("--data", default="data/processed/dataset.yaml")
    parser.add_argument("--conf", type=float, default=0.25)
    args = parser.parse_args()
    if METRICS_PATH.exists():
        raise SystemExit(f"{METRICS_PATH} exists: the test split must be evaluated exactly once.")
    metrics = evaluate(args.weights, args.data, args.conf)
    METRICS_PATH.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    print(f"wrote {METRICS_PATH}")


if __name__ == "__main__":
    main()
