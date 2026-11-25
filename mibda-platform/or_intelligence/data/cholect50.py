"""Adapter for the CholecT50 *Challenge Validation* release (CAMMA, CC BY-NC-SA 4.0).

Layout:  <root>/labels/VIDxx.json   <root>/videos/VIDxx/<frame>.png
Each annotation entry is:
  [triplet, instrument, prob, x, y, w, h, verb, target, ..., phase]
with x, y, w, h normalized and (x, y) the TOP-LEFT corner (checked visually on real
frames). Frames are sampled at 1 fps, so frame id == seconds, but only a subset of
frames is annotated, i.e. the timeline from this data is sparse.
"""
from __future__ import annotations

import json
import random
import shutil
from collections import Counter
from pathlib import Path

from ..constants import INSTRUMENTS
from ..models import Box, CaseAnalysis, FrameResult


def _entry_to_box(a: list) -> Box | None:
    if len(a) < 9 or a[3] is None or a[3] < 0:
        return None
    x, y, w, h = (float(v) for v in a[3:7])
    if w <= 0 or h <= 0:
        return None
    return Box(
        instrument=int(a[1]), x=x, y=y, w=w, h=h,
        conf=float(a[2]) if 0 <= float(a[2]) <= 1 else 1.0,
        verb=int(a[7]), target=int(a[8]), triplet=int(a[0]),
    )


def load_video(label_path: str | Path, frames_dir: str | Path | None = None) -> CaseAnalysis:
    j = json.loads(Path(label_path).read_text(encoding="utf-8"))
    fps = float(j.get("fps", 1)) or 1.0
    vid = f"VID{int(j['video']):02d}" if "video" in j else Path(label_path).stem
    frames: list[FrameResult] = []
    for key in sorted(j["annotations"], key=int):
        fid = int(key)
        entries = j["annotations"][key]
        boxes = [b for b in (_entry_to_box(a) for a in entries) if b is not None]
        phase = int(entries[0][-1]) if entries else None
        img = f"{fid:06d}.png"
        if frames_dir is not None and not (Path(frames_dir) / img).exists():
            continue  # annotation without an image on disk: skip
        frames.append(FrameResult(t=fid / fps, image=img, boxes=boxes, phase=phase))
    duration = (frames[-1].t + 1.0) if frames else 0.0
    return CaseAnalysis(
        video_id=vid, source="annotations", duration=duration, frames=frames,
        detector="CholecT50 ground-truth annotations (demo replay, not model output)",
        params={"dense": False, "fps": fps},
    )


def load_root(root: str | Path) -> dict[str, tuple[CaseAnalysis, Path]]:
    """Return {video_id: (analysis, frames_dir)} for every labels/*.json under root."""
    root = Path(root)
    out: dict[str, tuple[CaseAnalysis, Path]] = {}
    for lp in sorted((root / "labels").glob("VID*.json")):
        frames_dir = root / "videos" / lp.stem
        if not frames_dir.is_dir():
            continue
        out[lp.stem] = (load_video(lp, frames_dir), frames_dir)
    return out


def assign_splits(video_ids: list[str], n_val: int = 1, n_test: int = 1, seed: int = 0) -> dict[str, str]:
    """Split BY VIDEO (never by frame): neighbouring frames are near-duplicates and would leak."""
    ids = sorted(video_ids)
    if len(ids) < n_val + n_test + 1:
        raise ValueError("Need at least one training video besides the val/test videos.")
    random.Random(seed).shuffle(ids)
    split = {v: "test" for v in ids[:n_test]}
    split.update({v: "val" for v in ids[n_test:n_test + n_val]})
    split.update({v: "train" for v in ids[n_test + n_val:]})
    return split


def to_yolo_line(b: Box) -> str | None:
    x1, y1 = max(0.0, b.x), max(0.0, b.y)
    x2, y2 = min(1.0, b.x + b.w), min(1.0, b.y + b.h)
    w, h = x2 - x1, y2 - y1
    if w <= 0 or h <= 0:
        return None
    return f"{b.instrument} {x1 + w / 2:.6f} {y1 + h / 2:.6f} {w:.6f} {h:.6f}"


def export_yolo(root: str | Path, out_dir: str | Path, split: dict[str, str] | None = None) -> dict:
    """Write an Ultralytics detection dataset. Unlabelled frames are NOT exported
    (a missing label file would silently teach the model that they are background)."""
    root, out = Path(root), Path(out_dir)
    cases = load_root(root)
    split = split or assign_splits(list(cases))
    stats: dict[str, dict] = {s: {"images": 0, "boxes": Counter(), "videos": []} for s in ("train", "val", "test")}
    for vid, (analysis, frames_dir) in cases.items():
        sp = split[vid]
        (out / "images" / sp).mkdir(parents=True, exist_ok=True)
        (out / "labels" / sp).mkdir(parents=True, exist_ok=True)
        stats[sp]["videos"].append(vid)
        for f in analysis.frames:
            lines = [ln for ln in (to_yolo_line(b) for b in f.boxes) if ln]
            if not lines:
                continue
            stem = f"{vid}_{Path(f.image).stem}"
            shutil.copy2(frames_dir / f.image, out / "images" / sp / f"{stem}.png")
            (out / "labels" / sp / f"{stem}.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
            stats[sp]["images"] += 1
            for b in f.boxes:
                stats[sp]["boxes"][INSTRUMENTS[b.instrument]] += 1
    names = "\n".join(f"  {i}: {n}" for i, n in enumerate(INSTRUMENTS))
    (out / "data.yaml").write_text(
        f"path: {out.resolve().as_posix()}\ntrain: images/train\nval: images/val\ntest: images/test\nnames:\n{names}\n",
        encoding="utf-8",
    )
    return stats
