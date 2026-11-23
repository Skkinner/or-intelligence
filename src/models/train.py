"""Baseline YOLO training wrapper around Ultralytics.

WBS 3.1.1 · Owner: Member B · Branch: feature/member-b-3.1.1-baseline
Depends on: 2.2.2 (data/processed/dataset.yaml from Member A)

Usage (Colab/Kaggle GPU — see notebooks/experiments/train_colab.ipynb):
    python -m src.models.train --config configs/train.yaml --name baseline

Outputs:
    runs/detect/<name>/ (gitignored), models/weights/baseline.pt (shared via Release/Drive, never Git),
    a new row in docs/model/experiments.md

Acceptance:
    - Baseline val mAP@0.5 recorded in docs/model/experiments.md.
    - Weights downloadable by the team.
    - Training reproducible from the config with the same seed.
"""

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path

import yaml


def load_train_config(path: str | Path, overrides: dict | None = None) -> dict:
    """Load configs/train.yaml and apply optional overrides (used by tune.py)."""
    with open(path, encoding="utf-8") as fh:
        cfg = yaml.safe_load(fh)
    if overrides:
        cfg = {**cfg, **overrides}
    return cfg


def config_hash(cfg: dict) -> str:
    """Short hash recorded in docs/model/experiments.md for reproducibility."""
    return hashlib.sha1(yaml.safe_dump(cfg, sort_keys=True).encode()).hexdigest()[:8]


def train(cfg: dict, name: str) -> Path:
    """Train and return the path of the best weights.

    TODO(B, 3.1.1):
      from ultralytics import YOLO
      model = YOLO(cfg["model"]); model.train(data=cfg["data"], imgsz=..., epochs=..., batch=..., patience=...,
                                              seed=cfg["seed"], name=name, save_period=1)
      Copy runs/detect/<name>/weights/best.pt -> models/weights/<name>.pt and print val mAP@0.5 / mAP@0.5:0.95.
    """
    raise NotImplementedError("WBS 3.1.1 (Member B)")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="configs/train.yaml")
    parser.add_argument("--name", default="baseline")
    args = parser.parse_args()
    cfg = load_train_config(args.config)
    print(f"config hash {config_hash(cfg)}")
    print(train(cfg, args.name))


if __name__ == "__main__":
    main()
