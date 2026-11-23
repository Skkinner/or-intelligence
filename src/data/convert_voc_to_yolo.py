"""Convert m2cai16-tool-locations Pascal-VOC boxes to YOLO txt labels (contract C2).

WBS 2.2.1 · Owner: Member A · Branch: feature/member-a-2.2.1-voc-to-yolo
Depends on: 2.1.1 (raw data), 1.2.2 (contracts/classes.json)

Usage:
    python -m src.data.convert_voc_to_yolo --src data/raw/m2cai16_tool_locations --out data/processed/yolo

Output line format (one per box): "cls cx cy w h", all normalised to [0, 1].

Acceptance:
    - Every image has exactly one .txt label file (possibly empty = background image).
    - All class ids in {0..5}; all coordinates in [0, 1].
    - >= 50 visual spot-checks recorded in docs/data/qa_notes.md with < 2% label errors.
    - tests/unit/data/test_convert.py passes in CI.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass, field
from pathlib import Path

from src.common.contracts import load_classes, name_to_id


@dataclass
class ConversionStats:
    images: int = 0
    boxes_written: int = 0
    boxes_dropped: int = 0          # SpecimenBag or unknown names
    empty_images: int = 0
    malformed_xml: list[str] = field(default_factory=list)


def map_class(name: str) -> int | None:
    """Map a VOC object name (any case, e.g. "Grasper") to a class id, or None if it must be dropped.

    TODO(A, 2.2.1): case-insensitive lookup in contracts/classes.json; return None for
    names in `dropped_source_classes` (SpecimenBag) and log unknown names.
    """
    raise NotImplementedError("WBS 2.2.1 (Member A)")


def voc_box_to_yolo(xmin: float, ymin: float, xmax: float, ymax: float,
                    img_w: int, img_h: int) -> tuple[float, float, float, float]:
    """Clip a pixel box to the image bounds and return normalised (cx, cy, w, h).

    TODO(A, 2.2.1): clip to [0, img_w] x [0, img_h] before normalising.
    """
    raise NotImplementedError("WBS 2.2.1 (Member A)")


def convert_xml(xml_path: Path) -> list[str]:
    """Parse one VOC XML file and return YOLO label lines (may be empty).

    TODO(A, 2.2.1): use xml.etree.ElementTree; read <size>, every <object>/<name>/<bndbox>.
    """
    raise NotImplementedError("WBS 2.2.1 (Member A)")


def convert_dataset(src: Path, out: Path) -> ConversionStats:
    """Convert every image/XML pair under ``src`` into ``out/images`` and ``out/labels`` (unsplit).

    Splitting into train/val/test happens later in src/data/split.py (2.2.2).
    """
    _ = (load_classes, name_to_id)  # contract helpers available for the implementation
    raise NotImplementedError("WBS 2.2.1 (Member A)")


def main() -> None:
    parser = argparse.ArgumentParser(description="VOC -> YOLO conversion (WBS 2.2.1)")
    parser.add_argument("--src", type=Path, default=Path("data/raw/m2cai16_tool_locations"))
    parser.add_argument("--out", type=Path, default=Path("data/processed/yolo"))
    args = parser.parse_args()
    stats = convert_dataset(args.src, args.out)
    print(stats)


if __name__ == "__main__":
    main()
