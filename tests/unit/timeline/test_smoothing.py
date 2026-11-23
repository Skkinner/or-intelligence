"""Unit tests for WBS 4.1.1 / 4.1.2 (Member C). Remove skip marks as you implement."""

import numpy as np
import pytest

from src.common.contracts import FIXTURES_DIR, iter_jsonl, validate

TODO_SMOOTH = pytest.mark.skip(reason="TODO WBS 4.1.1 (Member C): implement smoothing")
TODO_BUILD = pytest.mark.skip(reason="TODO WBS 4.1.2 (Member C): implement builder")
FIXTURE = FIXTURES_DIR / "sample_detections.jsonl"


@TODO_SMOOTH
def test_single_frame_flicker_removed():
    from src.timeline.smoothing import smooth

    m = np.zeros((50, 6))
    m[:, 2] = 0.9
    m[25, 2] = 0.0                      # 1-frame dropout at 5 fps
    out = smooth(m, fps=5.0, window_s=2.0, method="majority")
    assert out[:, 2][5:45].all()


@TODO_SMOOTH
def test_real_three_second_gap_kept():
    from src.timeline.smoothing import smooth

    m = np.zeros((100, 6))
    m[:40, 0] = 0.9
    m[55:, 0] = 0.9                     # 3 s gap at 5 fps
    out = smooth(m, fps=5.0, window_s=2.0, method="majority")
    assert not out[45:50, 0].any()


@TODO_SMOOTH
def test_presence_matrix_shape_and_dtype():
    from src.timeline.smoothing import presence_matrix

    times, m = presence_matrix(iter_jsonl(FIXTURE), conf=0.4)
    assert m.shape[1] == 6 and len(times) == m.shape[0]
    assert np.issubdtype(m.dtype, np.floating)


@TODO_BUILD
def test_builder_output_validates_against_c5():
    from src.timeline.builder import build_timeline, load_params

    timeline = build_timeline(str(FIXTURE), "fixture_case_01", load_params())
    validate(timeline, "timeline")
