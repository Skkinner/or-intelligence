"""Make a short sample clip (real surgical frames) from the prepared CholecT45 frames, for the Live analysis page.

  python scripts/make_sample_clip.py --video VID14 --start 400 --n 300

The frames are 1 fps, so the clip plays at 1 fps (real time). Output: datasets/samples/<video>.mp4 (never committed).
"""
from __future__ import annotations

import argparse
from pathlib import Path

import cv2
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--video", default="VID14")
    ap.add_argument("--start", type=int, default=400)
    ap.add_argument("--n", type=int, default=300)
    ap.add_argument("--src", default=str(ROOT / "datasets" / "cholect45_cls"))
    a = ap.parse_args()
    d = pd.read_csv(Path(a.src) / "labels.csv")
    d = d[(d.video == a.video) & (d.blank == 0) & (d.frame >= a.start)].head(a.n)
    first = cv2.imread(str(Path(a.src) / "frames" / a.video / f"{int(d.iloc[0].frame):06d}.jpg"))
    h, w = first.shape[:2]
    out = ROOT / "datasets" / "samples" / f"{a.video}_clip.mp4"
    out.parent.mkdir(parents=True, exist_ok=True)
    vw = cv2.VideoWriter(str(out), cv2.VideoWriter_fourcc(*"mp4v"), 1.0, (w, h))
    for f in d.frame:
        vw.write(cv2.imread(str(Path(a.src) / "frames" / a.video / f"{int(f):06d}.jpg")))
    vw.release()
    print("wrote", out, len(d), "frames")


if __name__ == "__main__":
    main()
