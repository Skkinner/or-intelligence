"""Video inference: sample a video at N fps, run YOLO, write detections.jsonl (contract C4).

WBS 3.3.1 · Owner: Member B   ⚠ critical integration point
Same logic as step 9 of notebooks/02_Model.ipynb. This copy is the one the app uses:
Member C's API (src/api/jobs.py) and timeline evaluation import ``detect_video`` from here.
Signature changes need a contract PR first (contracts/README.md).

CLI:
    python -m src.inference.detect_video in.mp4 out.jsonl --fps 5 [--conf 0.25] [--weights models/weights/best.pt]

Each output line (validates against contracts/detections.schema.json):
    {"video_id": "abc123", "frame": 125, "t": 5.0, "w": 1920, "h": 1080,
     "dets": [{"cls": 2, "name": "hook", "conf": 0.91, "box": [0.41, 0.33, 0.62, 0.71]}]}

Remaining TODO(B, 3.3.1): run it on tests/fixtures/sample_video.mp4 with best.pt (test in tests/unit/inference),
and record the processing time of a 2-min 1080p clip at 5 fps in src/inference/README.md.
"""

from __future__ import annotations

import argparse
import json
from collections.abc import Callable
from pathlib import Path

from src.common.contracts import class_names

DEFAULT_WEIGHTS = "models/weights/best.pt"   # copy weights/best.pt from the team Drive folder here
STAND_IN_WEIGHTS = "yolov8n.pt"              # COCO-pretrained; class ids will NOT match C1 — plumbing tests only


def detect_video(
    video_path: str,
    out_path: str,
    sample_fps: float = 5.0,
    conf: float = 0.25,
    weights: str = DEFAULT_WEIGHTS,
    on_progress: Callable[[float], None] | None = None,
) -> dict:
    """Run detection on ``video_path`` and write one JSON line per sampled frame to ``out_path``.

    Returns ``{"frames": <sampled frames written>, "seconds": <video duration>}``.
    Uses the GPU if available, otherwise the CPU. Accepts ``.pt`` or ``.onnx`` weights.
    """
    # Heavy imports stay inside the function so CI (no torch/opencv) can import this module.
    import cv2
    from ultralytics import YOLO

    names = class_names()
    model = YOLO(weights)
    cap = cv2.VideoCapture(str(video_path))
    if not cap.isOpened():
        raise FileNotFoundError(f"cannot open video: {video_path}")
    fps = cap.get(cv2.CAP_PROP_FPS) or 25.0
    total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    width, height = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    step = max(1, round(fps / sample_fps))
    video_id = Path(video_path).stem

    written, idx = 0, 0
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as fh:
        while cap.grab():
            if idx % step == 0:
                ok, frame = cap.retrieve()
                if not ok:
                    break
                result = model.predict(frame, conf=conf, verbose=False)[0]
                dets = [
                    {
                        "cls": int(c),
                        "name": names[int(c)],
                        "conf": round(float(s), 4),
                        "box": [round(min(max(float(v), 0.0), 1.0), 4) for v in box],
                    }
                    for c, s, box in zip(result.boxes.cls, result.boxes.conf, result.boxes.xyxyn, strict=True)
                    if int(c) < len(names)
                ]
                record = {"video_id": video_id, "frame": idx, "t": round(idx / fps, 3),
                          "w": width, "h": height, "dets": dets}
                fh.write(json.dumps(record) + "\n")
                written += 1
                if on_progress and total:
                    on_progress(min(idx / total, 1.0))
            idx += 1
    cap.release()
    if on_progress:
        on_progress(1.0)
    return {"frames": written, "seconds": (total or idx) / fps}


def main() -> None:
    parser = argparse.ArgumentParser(description="Video -> detections.jsonl (contract C4)")
    parser.add_argument("video", type=Path)
    parser.add_argument("out", type=Path)
    parser.add_argument("--fps", type=float, default=5.0)
    parser.add_argument("--conf", type=float, default=0.25)
    parser.add_argument("--weights", default=DEFAULT_WEIGHTS)
    args = parser.parse_args()
    result = detect_video(str(args.video), str(args.out), args.fps, args.conf, args.weights,
                          on_progress=lambda f: print(f"\r{f:6.1%}", end="", flush=True))
    print(f"\n{result}")


if __name__ == "__main__":
    main()
