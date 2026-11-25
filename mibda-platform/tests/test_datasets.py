import os
from pathlib import Path

import cv2
import numpy as np
import pytest

from conftest import write_fake_cholect50
from or_intelligence.data import cholecinstanceseg, cholect50, masks
from or_intelligence.models import Box


def test_cholect50_loader_skips_boxless_and_imageless(tmp_path):
    root = write_fake_cholect50(tmp_path / "ds", ("VID01",))
    (analysis, frames_dir) = cholect50.load_root(root)["VID01"]
    assert [f.t for f in analysis.frames] == [10.0, 20.0, 30.0]      # frame 99 has no image
    f = analysis.frames[0]
    assert len(f.boxes) == 2 and f.phase == 2 and f.boxes[0].verb == 0 and f.boxes[0].target == 0
    assert analysis.source == "annotations" and not analysis.dense


def test_yolo_line_is_center_normalized_and_clipped():
    # top-left (0.5, 0.25), size (0.3, 0.4) -> center (0.65, 0.45)
    assert cholect50.to_yolo_line(Box(0, 0.5, 0.25, 0.3, 0.4)) == "0 0.650000 0.450000 0.300000 0.400000"
    # a box that sticks out of the frame is clipped, not rejected
    assert cholect50.to_yolo_line(Box(2, 0.9, 0.9, 0.3, 0.3)) == "2 0.950000 0.950000 0.100000 0.100000"
    assert cholect50.to_yolo_line(Box(2, 1.2, 0.5, 0.1, 0.1)) is None


def test_split_is_by_video_and_deterministic():
    ids = ["VID01", "VID02", "VID03", "VID04", "VID05"]
    s1, s2 = cholect50.assign_splits(ids, 1, 1, seed=3), cholect50.assign_splits(ids, 1, 1, seed=3)
    assert s1 == s2 and sorted(s1.values()).count("test") == 1 and sorted(s1.values()).count("train") == 3
    with pytest.raises(ValueError):
        cholect50.assign_splits(["a", "b"], 1, 1)


def test_export_yolo_keeps_videos_apart(tmp_path):
    root = write_fake_cholect50(tmp_path / "ds")
    out = tmp_path / "yolo"
    stats = cholect50.export_yolo(root, out)
    assert (out / "data.yaml").read_text().count(":") >= 6
    seen = {}
    for sp in ("train", "val", "test"):
        for p in (out / "labels" / sp).glob("*.txt"):
            seen.setdefault(p.stem.split("_")[0], set()).add(sp)
    assert all(len(v) == 1 for v in seen.values())                      # no video in two splits
    assert sum(s["images"] for s in stats.values()) == 4 * 3
    assert len(list((out / "images" / "train").glob("*.png"))) == len(list((out / "labels" / "train").glob("*.txt")))


REAL = os.environ.get("ORI_TEST_CHOLECT50")


@pytest.mark.skipif(not REAL, reason="set ORI_TEST_CHOLECT50 to the real challenge-validation folder")
def test_real_dataset_counts():
    cases = cholect50.load_root(REAL)
    assert len(cases) == 5
    assert sum(len(a.frames) for a, _ in cases.values()) > 1000


# ---- CholecInstanceSeg -----------------------------------------------------------
def test_polygon_conversion_normalizes():
    line = cholecinstanceseg.polygon_to_yolo_seg(2, [[0, 0], [100, 0], [100, 50], [0, 50]], 200, 100, simplify=0)
    assert line == "2 0.000000 0.000000 0.500000 0.000000 0.500000 0.500000 0.000000 0.500000"
    assert cholecinstanceseg.polygon_to_yolo_seg(0, [[0, 0], [1, 1]], 10, 10) is None


def test_annotation_unknown_label_and_missing_size():
    data = {"shapes": [
        {"label": "grasper", "shape_type": "polygon", "points": [[10, 10], [60, 10], [60, 40]]},
        {"label": "snare", "shape_type": "polygon", "points": [[1, 1], [5, 1], [5, 5]]}]}
    lines, skipped = cholecinstanceseg.convert_annotation(data)        # no imageWidth -> 854x480 assumed
    assert len(lines) == 1 and lines[0].startswith("0 ")
    assert skipped["snare"] == 1 and skipped["assumed_size_854x480"] == 1
    x = float(lines[0].split()[1])
    assert abs(x - 10 / 854) < 1e-5


# ---- generic masks ---------------------------------------------------------------
def test_masks_to_yolo(tmp_path):
    (tmp_path / "img").mkdir()
    (tmp_path / "msk").mkdir()
    cv2.imwrite(str(tmp_path / "img" / "a.png"), np.zeros((100, 200, 3), np.uint8))
    m = np.zeros((100, 200), np.uint8)
    cv2.rectangle(m, (40, 20), (120, 60), 255, -1)
    cv2.imwrite(str(tmp_path / "msk" / "a.png"), m)
    res = masks.export_yolo_seg(tmp_path / "img", tmp_path / "msk", tmp_path / "out", "tool", val=0, test=0)
    assert res["images"]["train"] == 1
    label = (tmp_path / "out" / "labels" / "train" / "a.txt").read_text().split()
    assert label[0] == "0" and len(label) >= 1 + 6
    xs = [float(v) for v in label[1::2]]
    assert abs(min(xs) - 40 / 200) < 0.02 and abs(max(xs) - 120 / 200) < 0.02
