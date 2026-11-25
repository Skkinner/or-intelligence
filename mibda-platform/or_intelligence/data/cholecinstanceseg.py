"""Adapter for CholecInstanceSeg annotations (LabelMe polygons) -> YOLO segmentation labels.

IMPORTANT: the public release contains ANNOTATIONS ONLY. The matching frames come from
Cholec80 / CholecT50 / CholecSeg8k, which you must obtain from their owners. Without
images this adapter can still write the label files (`images_root=None`).
"""
from __future__ import annotations

import csv
import json
import shutil
import zipfile
from collections import Counter
from pathlib import Path

from ..constants import INSTRUMENT_ID, INSTRUMENTS

try:
    import cv2
    import numpy as np
except Exception:  # pragma: no cover
    cv2 = None
    np = None


DEFAULT_SIZE = (854, 480)


def polygon_to_yolo_seg(cls_id: int, points: list[list[float]], width: int, height: int, simplify: float = 1.5) -> str | None:
    pts = [(float(x), float(y)) for x, y in points]
    if simplify and cv2 is not None and len(pts) > 8:
        approx = cv2.approxPolyDP(np.array(pts, dtype=np.float32).reshape(-1, 1, 2), simplify, True)
        pts = [(float(p[0][0]), float(p[0][1])) for p in approx]
    if len(pts) < 3:
        return None
    flat = []
    for x, y in pts:
        flat.append(f"{min(max(x / width, 0.0), 1.0):.6f}")
        flat.append(f"{min(max(y / height, 0.0), 1.0):.6f}")
    return f"{cls_id} " + " ".join(flat)


def convert_annotation(data: dict, simplify: float = 1.5) -> tuple[list[str], Counter]:
    """LabelMe dict -> (YOLO-seg lines, counter of skipped labels)."""
    lines: list[str] = []
    skipped: Counter = Counter()
    if data.get("imageWidth") and data.get("imageHeight"):
        w, h = int(data["imageWidth"]), int(data["imageHeight"])
    else:
        # The CholecSeg8k-derived files carry no size. Every polygon in them lies inside
        # 854x480 (checked: max x=853, max y=479), the standard Cholec80 frame size.
        w, h = DEFAULT_SIZE
        if data.get("shapes"):
            skipped["assumed_size_854x480"] += 1
    for s in data.get("shapes", []):
        label = s.get("label", "")
        if label not in INSTRUMENT_ID or s.get("shape_type", "polygon") != "polygon":
            skipped[label or "?"] += 1
            continue
        line = polygon_to_yolo_seg(INSTRUMENT_ID[label], s["points"], w, h, simplify)
        if line:
            lines.append(line)
        else:
            skipped["degenerate"] += 1
    return lines, skipped


def _find_image(images_root: Path, source: str, video_id: str, img_name: str) -> Path | None:
    for cand in (
        images_root / video_id / img_name,
        images_root / source / video_id / img_name,
        images_root / source.lower() / video_id / img_name,
    ):
        if cand.exists():
            return cand
    return None


def export_yolo_seg(
    zip_path: str | Path,
    metadata_csv: str | Path,
    out_dir: str | Path,
    images_root: str | Path | None = None,
    limit: int | None = None,
) -> dict:
    """Write labels (and images when `images_root` has them), using the dataset's own train/val/test split."""
    out = Path(out_dir)
    z = zipfile.ZipFile(zip_path)
    names = set(z.namelist())
    stats = {"written": 0, "missing_images": 0, "skipped": Counter(), "per_split": Counter(), "instances": Counter()}
    with open(metadata_csv, newline="", encoding="utf-8") as fh:
        for i, row in enumerate(csv.DictReader(fh)):
            if limit and i >= limit:
                break
            inner = row["Annotation_Path"].replace("\\", "/")
            if inner not in names:
                continue
            sp = row["Dataset_Split"]
            stem = f"{row['Source_Dataset']}_{row['Video_ID']}_{Path(row['Img_filename_in_source_dataset']).stem}"
            lines, skipped = convert_annotation(json.loads(z.read(inner)))
            stats["skipped"].update(skipped)
            if images_root is not None:
                img = _find_image(Path(images_root), row["Source_Dataset"], row["Video_ID"], row["Img_filename_in_source_dataset"])
                if img is None:
                    stats["missing_images"] += 1
                    continue
                (out / "images" / sp).mkdir(parents=True, exist_ok=True)
                shutil.copy2(img, out / "images" / sp / f"{stem}{img.suffix}")
            (out / "labels" / sp).mkdir(parents=True, exist_ok=True)
            (out / "labels" / sp / f"{stem}.txt").write_text("\n".join(lines) + ("\n" if lines else ""), encoding="utf-8")
            stats["written"] += 1
            stats["per_split"][sp] += 1
            for ln in lines:
                stats["instances"][INSTRUMENTS[int(ln.split()[0])]] += 1
    names_yaml = "\n".join(f"  {i}: {n}" for i, n in enumerate(INSTRUMENTS))
    (out / "data.yaml").write_text(
        f"path: {out.resolve().as_posix()}\ntrain: images/train\nval: images/val\ntest: images/test\nnames:\n{names_yaml}\n",
        encoding="utf-8",
    )
    return stats
