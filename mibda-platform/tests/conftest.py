import json
import sys
from pathlib import Path

import pytest
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from or_intelligence import config, db  # noqa: E402
from or_intelligence.models import Box, CaseAnalysis, FrameResult  # noqa: E402


@pytest.fixture()
def tmp_platform(tmp_path, monkeypatch):
    """Point the platform at an empty temp data folder."""
    data = tmp_path / "data"
    monkeypatch.setattr(config, "DATA_DIR", data)
    monkeypatch.setattr(config, "DB_PATH", data / "app.db")
    monkeypatch.setattr(config, "UPLOAD_DIR", data / "uploads")
    monkeypatch.setattr(config, "ANALYSIS_DIR", data / "analysis")
    db.init_db()
    return data


def make_analysis(spans: dict[int, list[tuple[float, float]]], duration=100.0, step=1.0, dense=True) -> CaseAnalysis:
    """spans: instrument -> [(start, end)] ranges during which the instrument is detected."""
    frames = []
    t = 0.0
    while t < duration:
        boxes = [Box(i, 0.1, 0.1, 0.2, 0.2, 0.9) for i, rs in spans.items() if any(a <= t <= b for a, b in rs)]
        frames.append(FrameResult(t=t, boxes=boxes, phase=int(t // (duration / 3 + 1e-9))))
        t += step
    return CaseAnalysis("TEST", "model", duration, frames, "test", {"dense": dense})


def write_fake_cholect50(root: Path, videos=("VID01", "VID02", "VID03", "VID04")) -> Path:
    """A tiny dataset in the CholecT50 challenge-validation layout."""
    for n, vid in enumerate(videos, start=1):
        (root / "videos" / vid).mkdir(parents=True)
        (root / "labels").mkdir(exist_ok=True)
        ann = {}
        for fid in (10, 20, 30):
            Image.new("RGB", (200, 100), (90, 20, 20)).save(root / "videos" / vid / f"{fid:06d}.png")
            # [triplet, instrument, prob, x, y, w, h, verb, target, ..., phase]
            ann[str(fid)] = [[7, 0, 1.0, 0.5, 0.25, 0.3, 0.4, 0, 0, 1.0, -1, -1, -1, -1, 2],
                             [79, 4, 1.0, 0.1, 0.1, 0.2, 0.2, 4, 2, 1.0, -1, -1, -1, -1, 2]]
        # one entry without a box (x = -1) must be ignored, one frame without image must be skipped
        ann["99"] = [[1, 1, 1.0, -1, -1, -1, -1, 0, 0, 1.0, -1, -1, -1, -1, 2]]
        (root / "labels" / f"{vid}.json").write_text(json.dumps({"video": n, "fps": 1, "num_frames": 4, "annotations": ann}))
    return root
