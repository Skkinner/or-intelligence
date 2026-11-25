"""Inference performance benchmark (processing time per video-minute at several sample rates).

WBS 6.1.1 · Owner: Member B · priority Low
Times ``src.inference.detect_video`` end to end (decode + sample + YOLO + JSON write) on one video.

Usage:
    python -m src.models.benchmark <clip>.mp4 --fps 1 2 5            # GPU if available
    python -m src.models.benchmark <clip>.mp4 --fps 1 --cpu          # force CPU

Prints one Markdown table row per sample rate, ready to paste into docs/model/BENCHMARK.md.
"""

from __future__ import annotations

import argparse
import os
import platform
import time
from pathlib import Path


def time_run(video: Path, fps: float, weights: str) -> dict:
    """Time one detect_video run and return {"fps", "wall_s", "video_s", "frames", "s_per_video_min"}."""
    from src.inference.detect_video import detect_video

    out = Path("runs/benchmark") / f"{video.stem}_{fps:g}fps.jsonl"
    out.parent.mkdir(parents=True, exist_ok=True)
    start = time.perf_counter()
    result = detect_video(str(video), str(out), sample_fps=fps, weights=weights)
    wall = time.perf_counter() - start
    return {"fps": fps, "wall_s": wall, "video_s": result["seconds"], "frames": result["frames"],
            "s_per_video_min": wall / max(result["seconds"] / 60.0, 1e-9)}


def device_name() -> str:
    import torch

    if torch.cuda.is_available():
        return f"GPU {torch.cuda.get_device_name(0)}"
    return f"CPU {platform.processor() or platform.machine()} ({os.cpu_count()} threads)"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("video", type=Path)
    parser.add_argument("--fps", type=float, nargs="+", default=[1.0, 2.0, 5.0])
    parser.add_argument("--weights", default="models/weights/best.pt")
    parser.add_argument("--cpu", action="store_true", help="hide the GPU and run on the CPU")
    args = parser.parse_args()
    if args.cpu:
        os.environ["CUDA_VISIBLE_DEVICES"] = ""   # must be set before torch initialises CUDA

    # Warm-up: load the model and run one frame so the first timed run does not include start-up cost.
    import numpy as np
    from ultralytics import YOLO

    YOLO(args.weights).predict(np.zeros((640, 640, 3), dtype=np.uint8), verbose=False)

    dev = device_name()
    print("| Device | sample_fps | Video length (min) | Frames | Wall time (s) | s per video-minute |")
    print("|---|---|---|---|---|---|")
    for f in args.fps:
        r = time_run(args.video, f, args.weights)
        print(f"| {dev} | {r['fps']:g} | {r['video_s'] / 60:.1f} | {r['frames']} | {r['wall_s']:.1f} "
              f"| {r['s_per_video_min']:.1f} |", flush=True)


if __name__ == "__main__":
    main()
