"""Inference performance benchmark (processing time per video-minute at several sample rates).

WBS 6.1.1 · Owner: Member B · Branch: feature/member-b-6.1.1-benchmark   (priority: Low — cut first if late)
Depends on: 3.3.2 (best.pt), 4.1.3 (Member C's src/timeline/evaluate.py — call it, don't modify it)

Usage:
    python -m src.models.benchmark data/raw/<10-min clip>.mp4 --fps 1 2 5 [--cpu]

Output: docs/model/BENCHMARK.md (table: device, sample_fps, seconds per video-minute; recommended default sample_fps)
"""

from __future__ import annotations

import argparse
import time
from pathlib import Path

from src.inference.detect_video import detect_video


def time_run(video: Path, fps: float, weights: str) -> dict:
    """Time one detect_video run and return {"fps", "wall_s", "video_s", "s_per_video_min"}."""
    out = Path("runs/benchmark") / f"{video.stem}_{fps}fps.jsonl"
    out.parent.mkdir(parents=True, exist_ok=True)
    start = time.perf_counter()
    result = detect_video(str(video), str(out), sample_fps=fps, weights=weights)
    wall = time.perf_counter() - start
    return {"fps": fps, "wall_s": wall, "video_s": result["seconds"],
            "s_per_video_min": wall / max(result["seconds"] / 60.0, 1e-9)}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("video", type=Path)
    parser.add_argument("--fps", type=float, nargs="+", default=[1.0, 2.0, 5.0])
    parser.add_argument("--weights", default="models/weights/best.pt")
    args = parser.parse_args()
    rows = [time_run(args.video, f, args.weights) for f in args.fps]
    # TODO(B, 6.1.1): add a CPU run at 1 fps; optional macro-F1 vs fps via src.timeline.evaluate
    for r in rows:
        print(r)


if __name__ == "__main__":
    main()
