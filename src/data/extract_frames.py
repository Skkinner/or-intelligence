"""Optional 1 fps frame dump for debugging timeline-evaluation videos (ffmpeg via subprocess).

WBS 2.3.1 · Owner: Member A

Usage:
    python -m src.data.extract_frames data/raw/cholec80/videos/video41.mp4 --fps 1 --out data/processed/frames/video41
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
from pathlib import Path


def extract_frames(video: Path, out_dir: Path, fps: float = 1.0) -> int:
    """Write ``out_dir/%06d.jpg`` at ``fps`` and return the number of frames written.

    TODO(A, 2.3.1): build the ffmpeg command, run it with check=True, count the output files.
    """
    if shutil.which("ffmpeg") is None:
        raise RuntimeError("ffmpeg not found on PATH")
    _ = subprocess  # used by the implementation
    raise NotImplementedError("WBS 2.3.1 (Member A)")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("video", type=Path)
    parser.add_argument("--fps", type=float, default=1.0)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    print(extract_frames(args.video, args.out, args.fps))


if __name__ == "__main__":
    main()
