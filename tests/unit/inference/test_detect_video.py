"""Tests for WBS 3.3.1 (Member B). Needs ultralytics + weights, so it is marked `gpu` and skipped in CI
until the fixture video and weights are available."""

from pathlib import Path

import pytest

from src.common.contracts import FIXTURES_DIR, iter_jsonl, validate

VIDEO = FIXTURES_DIR / "sample_video.mp4"


@pytest.mark.gpu
@pytest.mark.skipif(not VIDEO.exists(), reason="tests/fixtures/sample_video.mp4 not created yet (D, 1.2.2)")
def test_fixture_video_output_validates(tmp_path: Path):
    pytest.importorskip("ultralytics")
    from src.inference.detect_video import STAND_IN_WEIGHTS, detect_video

    progress: list[float] = []
    out = tmp_path / "dets.jsonl"
    result = detect_video(str(VIDEO), str(out), sample_fps=1.0, weights=STAND_IN_WEIGHTS,
                          on_progress=progress.append)
    assert result["frames"] > 0
    assert progress and progress[-1] == pytest.approx(1.0)
    for record in iter_jsonl(out):
        validate(record, "detections")
