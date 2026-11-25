"""Merge several YOLO datasets (detection or segmentation) into one, with class-name mapping.

Each source folder needs data.yaml (names) and images/<split>/ + labels/<split>/. Class names are matched
by name (optionally renamed through `rename`), a class mapped to None is dropped, and every file is
prefixed with its dataset tag so names never collide. Splits are kept as they are in each source.
"""
from __future__ import annotations

import shutil
from collections import Counter
from pathlib import Path

import yaml

IMG_EXT = {".png", ".jpg", ".jpeg", ".bmp"}


def read_names(dataset: Path) -> dict[int, str]:
    d = yaml.safe_load((dataset / "data.yaml").read_text(encoding="utf-8"))
    names = d["names"]
    return dict(enumerate(names)) if isinstance(names, list) else {int(k): v for k, v in names.items()}


def merge(sources: dict[str, str | Path], out_dir: str | Path, rename: dict[str, str | None] | None = None,
          class_order: list[str] | None = None) -> dict:
    """sources: {tag: dataset_dir}. rename: {source class name: unified name or None to drop}."""
    rename = rename or {}
    out = Path(out_dir)
    per_source = {tag: read_names(Path(p)) for tag, p in sources.items()}
    unified: list[str] = list(class_order or [])
    for names in per_source.values():
        for n in names.values():
            u = rename.get(n, n)
            if u is not None and u not in unified:
                unified.append(u)
    index = {n: i for i, n in enumerate(unified)}
    stats = {"images": Counter(), "instances": Counter(), "dropped_instances": 0, "skipped_unlabelled": 0}
    for tag, src in sources.items():
        src = Path(src)
        names = per_source[tag]
        for split in ("train", "val", "test"):
            ldir, idir = src / "labels" / split, src / "images" / split
            if not ldir.is_dir():
                continue
            for lp in sorted(ldir.glob("*.txt")):
                img = next((p for p in idir.glob(lp.stem + ".*") if p.suffix.lower() in IMG_EXT), None)
                if img is None:
                    stats["skipped_unlabelled"] += 1
                    continue
                lines = []
                for ln in lp.read_text(encoding="utf-8").splitlines():
                    parts = ln.split()
                    if not parts:
                        continue
                    u = rename.get(names[int(parts[0])], names[int(parts[0])])
                    if u is None:
                        stats["dropped_instances"] += 1
                        continue
                    lines.append(" ".join([str(index[u])] + parts[1:]))
                    stats["instances"][u] += 1
                (out / "images" / split).mkdir(parents=True, exist_ok=True)
                (out / "labels" / split).mkdir(parents=True, exist_ok=True)
                shutil.copy2(img, out / "images" / split / f"{tag}__{img.name}")
                (out / "labels" / split / f"{tag}__{lp.name}").write_text("\n".join(lines) + ("\n" if lines else ""), encoding="utf-8")
                stats["images"][split] += 1
    names_yaml = "\n".join(f"  {i}: {n}" for i, n in enumerate(unified))
    (out / "data.yaml").write_text(
        f"path: {out.resolve().as_posix()}\ntrain: images/train\nval: images/val\ntest: images/test\nnames:\n{names_yaml}\n",
        encoding="utf-8")
    stats["classes"] = unified
    return stats
