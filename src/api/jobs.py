"""Background processing: video -> detections.jsonl -> timeline.json, with status/progress updates.

WBS 4.2.1 · Owner: Member C
Calls Member B's ``src.inference.detect_video.detect_video`` (never edit it) and Member C's ``build_timeline``.

INFERENCE_MODE=fixture (default until M4): copy tests/fixtures/sample_detections.jsonl instead of running YOLO,
so the whole API + web flow works before any model exists.
"""

from __future__ import annotations

import os
import shutil
from pathlib import Path

from src.common.contracts import FIXTURES_DIR

STORAGE_DIR = Path(os.getenv("STORAGE_DIR", "storage"))
VIDEOS_DIR = STORAGE_DIR / "videos"
DETECTIONS_DIR = STORAGE_DIR / "detections"
TIMELINES_DIR = STORAGE_DIR / "timelines"


def run_detection(video_path: Path, out_path: Path, on_progress) -> dict:
    """Fixture mode replays the fixture; real mode calls detect_video (contract C4)."""
    if os.getenv("INFERENCE_MODE", "fixture") == "fixture":
        shutil.copyfile(FIXTURES_DIR / "sample_detections.jsonl", out_path)
        on_progress(1.0)
        return {"frames": -1, "seconds": -1.0}
    from src.inference.detect_video import detect_video

    return detect_video(str(video_path), str(out_path),
                        sample_fps=float(os.getenv("SAMPLE_FPS", "5.0")),
                        weights=os.getenv("WEIGHTS_PATH", "models/weights/best.pt"),
                        on_progress=on_progress)


def process_video(video_id: str) -> None:
    """Background task body: set status processing -> run_detection -> build_timeline -> save -> done/failed.

    TODO(C, 4.2.1):
      - Update Video.status / progress in the DB (detection = 0..0.9, timeline = 0.9..1.0).
      - Save timeline JSON to TIMELINES_DIR/<id>.json; set duration_s.
      - On any exception set status=failed and store the error message.
    """
    raise NotImplementedError("WBS 4.2.1 (Member C)")
