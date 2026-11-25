"""Generic adapter: folder of images + folder of binary masks -> YOLO segmentation dataset.

Useful for datasets distributed as image/mask pairs (for example Kvasir-Instrument or
EndoVis-style binary masks). Check each dataset's license before using it.
"""
from __future__ import annotations

import hashlib
import shutil
from pathlib import Path

import cv2

IMG_EXT = {".png", ".jpg", ".jpeg", ".bmp"}


def mask_to_polygons(mask: "cv2.Mat", min_area: float = 50.0, epsilon: float = 1.5) -> list[list[tuple[float, float]]]:
    m = (mask > 127).astype("uint8") * 255
    contours, _ = cv2.findContours(m, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    polys = []
    for c in contours:
        if cv2.contourArea(c) < min_area:
            continue
        a = cv2.approxPolyDP(c, epsilon, True)
        if len(a) >= 3:
            polys.append([(float(p[0][0]), float(p[0][1])) for p in a])
    return polys


def _split_of(stem: str, val: float, test: float) -> str:
    r = int(hashlib.md5(stem.encode()).hexdigest(), 16) % 1000 / 1000.0
    return "test" if r < test else "val" if r < test + val else "train"


def export_yolo_seg(
    images_dir: str | Path, masks_dir: str | Path, out_dir: str | Path,
    class_name: str = "tool", class_id: int = 0, val: float = 0.1, test: float = 0.1,
) -> dict:
    images_dir, masks_dir, out = Path(images_dir), Path(masks_dir), Path(out_dir)
    masks = {p.stem: p for p in masks_dir.iterdir() if p.suffix.lower() in IMG_EXT}
    n = {"train": 0, "val": 0, "test": 0}
    no_mask = no_poly = 0
    for img in sorted(p for p in images_dir.iterdir() if p.suffix.lower() in IMG_EXT):
        mp = masks.get(img.stem)
        if mp is None:
            no_mask += 1
            continue
        mask = cv2.imread(str(mp), cv2.IMREAD_GRAYSCALE)
        if mask is None:
            no_mask += 1
            continue
        h, w = mask.shape[:2]
        polys = mask_to_polygons(mask)
        if not polys:
            no_poly += 1
        sp = _split_of(img.stem, val, test)
        (out / "images" / sp).mkdir(parents=True, exist_ok=True)
        (out / "labels" / sp).mkdir(parents=True, exist_ok=True)
        shutil.copy2(img, out / "images" / sp / img.name)
        lines = [
            f"{class_id} " + " ".join(f"{min(max(x / w, 0), 1):.6f} {min(max(y / h, 0), 1):.6f}" for x, y in poly)
            for poly in polys
        ]
        (out / "labels" / sp / f"{img.stem}.txt").write_text("\n".join(lines) + ("\n" if lines else ""), encoding="utf-8")
        n[sp] += 1
    (out / "data.yaml").write_text(
        f"path: {out.resolve().as_posix()}\ntrain: images/train\nval: images/val\ntest: images/test\nnames:\n  {class_id}: {class_name}\n",
        encoding="utf-8",
    )
    return {"images": n, "without_mask": no_mask, "empty_masks": no_poly}
