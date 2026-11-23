"""Launch a named experiment from an override file in configs/experiments/.

WBS 3.1.2 · Owner: Member B · Branch: feature/member-b-3.1.2-tuning
Depends on: 3.1.1 (baseline), 2.4.1 (EDA recommendations from Member A)

Usage:
    python -m src.models.tune configs/experiments/exp01_imgsz832.yaml

Rules (from the WBS): select the final model on the **validation** split only; never look at test.
Tie-break: per-class min AP, then speed. Export models/weights/best.pt (+ optional best.onnx) by Tue 23:00 (M4).
"""

from __future__ import annotations

import argparse
from pathlib import Path

import yaml

from src.models.train import config_hash, load_train_config, train


def run_experiment(override_file: Path, base_config: str = "configs/train.yaml") -> Path:
    with open(override_file, encoding="utf-8") as fh:
        override = yaml.safe_load(fh) or {}
    name = override.pop("name", override_file.stem)
    cfg = load_train_config(base_config, override)
    print(f"experiment {name} config hash {config_hash(cfg)}")
    # TODO(B, 3.1.2): after training, record val mAP@0.5 and per-class AP in docs/model/experiments.md
    return train(cfg, name)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("override", type=Path)
    parser.add_argument("--base", default="configs/train.yaml")
    args = parser.parse_args()
    print(run_experiment(args.override, args.base))


if __name__ == "__main__":
    main()
