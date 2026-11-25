"""CholecT45 (zip or unzipped folder) -> small JPEG frames + a per-frame instrument-presence table.

The release is ~58 GB of PNG frames at 1 fps (45 videos, ~90k frames) with per-frame instrument PRESENCE labels
(6 classes, multi-label) and triplets. There are NO bounding boxes and NO phase labels in this package.
This script streams the zip (no need to unzip 58 GB), shrinks every frame to --width and writes:

  <out>/frames/VIDxx/000123.jpg
  <out>/labels.csv    video,frame,split,grasper,bipolar,hook,scissors,clipper,irrigator,blank

Splits are BY VIDEO (never by frame). Frames that are fully black (out-of-body, anonymised) are flagged `blank`.

  python scripts/prepare_cholect45_frames.py --src C:/Users/me/Downloads/CholecT45.zip --out datasets/cholect45_cls
"""
from __future__ import annotations

import argparse
import csv
import io
import zipfile
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import cv2
import numpy as np

CLASSES = ["grasper", "bipolar", "hook", "scissors", "clipper", "irrigator"]


def split_for(video_idx: int, n_videos: int) -> str:
    """Deterministic by-video split: ~70 / 15 / 15."""
    r = video_idx / max(n_videos, 1)
    return "train" if r < 0.7 else ("val" if r < 0.85 else "test")


def _labels(z: zipfile.ZipFile, vid: str) -> np.ndarray:
    rows = [list(map(int, ln.split(","))) for ln in z.read(f"CholecT45/instrument/{vid}.txt").decode().split() if ln]
    arr = np.array(rows)
    return arr[:, 1:7]            # column 0 is the frame index


def process_video(args: tuple[str, str, str, int, int]) -> list[list]:
    src, out, vid, idx, n_videos = args
    z = zipfile.ZipFile(src)
    lab = _labels(z, vid)
    out_dir = Path(out) / "frames" / vid
    out_dir.mkdir(parents=True, exist_ok=True)
    split = split_for(idx, n_videos)
    rows = []
    for f in range(len(lab)):
        data = z.read(f"CholecT45/data/{vid}/{f:06d}.png")
        img = cv2.imdecode(np.frombuffer(data, np.uint8), cv2.IMREAD_COLOR)
        blank = int(img.max() == 0)
        h, w = img.shape[:2]
        width = 320
        img = cv2.resize(img, (width, round(h * width / w)), interpolation=cv2.INTER_AREA)
        cv2.imwrite(str(out_dir / f"{f:06d}.jpg"), img, [cv2.IMWRITE_JPEG_QUALITY, 88])
        rows.append([vid, f, split, *[int(v > 0) for v in lab[f]], blank])
    return rows


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--src", required=True, help="CholecT45.zip")
    ap.add_argument("--out", default="datasets/cholect45_cls")
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--max-videos", type=int, default=0, help="0 = all (use a small number to test)")
    a = ap.parse_args()
    z = zipfile.ZipFile(a.src)
    vids = sorted({n.split("/")[2] for n in z.namelist() if n.startswith("CholecT45/instrument/") and n.endswith(".txt")})
    vids = [v[:-4] for v in vids]
    if a.max_videos:
        vids = vids[: a.max_videos]
    Path(a.out).mkdir(parents=True, exist_ok=True)
    jobs = [(a.src, a.out, v, i, len(vids)) for i, v in enumerate(vids)]
    rows: list[list] = []
    with ProcessPoolExecutor(a.workers) as ex:
        for n, part in enumerate(ex.map(process_video, jobs), 1):
            rows += part
            print(f"[{n}/{len(vids)}] {vids[n - 1]}: {len(part)} frames", flush=True)
    with open(Path(a.out) / "labels.csv", "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["video", "frame", "split", *CLASSES, "blank"])
        w.writerows(rows)
    print("done:", len(rows), "frames ->", a.out)


if __name__ == "__main__":
    main()
