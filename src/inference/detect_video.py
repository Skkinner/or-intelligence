"""Video inference: sample a video at N fps, run YOLO, stream detections.jsonl (contract C4).

WBS 3.3.1 · Owner: Member B · Branch: feature/member-b-3.3.1-inference   ⚠ critical integration point
Depends on: 1.2.2 (contracts) only. Build it Monday night with COCO-pretrained ``yolov8n.pt`` as a
stand-in, then swap to models/weights/baseline.pt / best.pt.
Hands off to: Member C (4.1.3, 4.2.1 imports ``detect_video``). Signature changes need a contract PR first.

CLI:
    python -m src.inference.detect_video in.mp4 out.jsonl --fps 5 [--conf 0.25] [--weights models/weights/best.pt]

Each output line (validates against contracts/detections.schema.json):
    {"video_id": "abc123", "frame": 125, "t": 5.0, "w": 1920, "h": 1080,
     "dets": [{"cls": 2, "name": "hook", "conf": 0.91, "box": [0.41, 0.33, 0.62, 0.71]}]}

Acceptance:
    - Output for tests/fixtures/sample_video.mp4 validates against the schema.
    - Progress callback reaches 1.0.
    - 2-min 1080p clip at 5 fps processes in < 2 min on the target GPU (documented in README.md).
"""

from __future__ import annotations

import argparse
from collections.abc import Callable
from pathlib import Path

DEFAULT_WEIGHTS = "models/weights/best.pt"
STAND_IN_WEIGHTS = "yolov8n.pt"   # COCO-pretrained; class ids will NOT match C1 — for plumbing only


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

    TODO(B, 3.3.1):
      1. Open the video with cv2.VideoCapture; read native fps, frame count, w, h.
      2. Keep every round(native_fps / sample_fps)-th frame; t = frame_index / native_fps.
      3. Batch frames (e.g. 16) through ultralytics.YOLO(weights).predict(conf=conf, device=auto: GPU else CPU).
      4. Convert boxes to normalised [x1, y1, x2, y2]; names via src.common.contracts.class_names().
      5. video_id = Path(video_path).stem unless the caller passes one (keep the signature stable).
      6. Write lines incrementally; call on_progress(fraction) after each batch and on_progress(1.0) at the end.
      7. Accept .onnx weights too (ultralytics handles both).
    """
    # Heavy imports stay inside the function so CI (no torch) can import this module.
    raise NotImplementedError("WBS 3.3.1 (Member B): implement video inference")


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
