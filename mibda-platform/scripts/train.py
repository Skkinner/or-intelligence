"""Fine-tune YOLO on the prepared dataset and copy the best weights to models/best.pt.

  pip install -r requirements-train.txt
  python scripts/train.py --data datasets/or_yolo/data.yaml --epochs 60
Use a GPU (Colab/Kaggle); on CPU this is very slow.
"""
from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--data", required=True)
    ap.add_argument("--model", default="yolov8n.pt", help="pretrained checkpoint to fine-tune")
    ap.add_argument("--epochs", type=int, default=60)
    ap.add_argument("--imgsz", type=int, default=640)
    ap.add_argument("--batch", type=int, default=16)
    ap.add_argument("--device", default=None)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--name", default="or_intelligence")
    a = ap.parse_args()

    from ultralytics import YOLO

    model = YOLO(a.model)
    model.train(data=a.data, epochs=a.epochs, imgsz=a.imgsz, batch=a.batch, device=a.device, seed=a.seed,
                project=str(ROOT / "runs"), name=a.name, exist_ok=True, patience=20,
                # surgical frames are not mirror-symmetric in meaningful ways, keep flips mild
                fliplr=0.5, flipud=0.0, mosaic=1.0)
    best = ROOT / "runs" / a.name / "weights" / "best.pt"
    if not best.exists():
        sys.exit(f"Training finished but {best} was not found.")
    (ROOT / "models").mkdir(exist_ok=True)
    shutil.copy2(best, ROOT / "models" / "best.pt")
    print("Saved models/best.pt. Next: python scripts/evaluate.py --data", a.data)


if __name__ == "__main__":
    main()
