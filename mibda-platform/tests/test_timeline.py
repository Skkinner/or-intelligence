import numpy as np

from conftest import make_analysis
from or_intelligence import timeline
from or_intelligence.constants import INSTRUMENTS
from or_intelligence.insights import review_flags

HOOK, CLIP = INSTRUMENTS.index("hook"), INSTRUMENTS.index("clipper")


def test_single_segment_and_stats():
    a = make_analysis({HOOK: [(10, 29)]}, duration=100)
    _, _, ivs = timeline.build_intervals(a, smooth_window=1)
    assert len(ivs) == 1 and ivs[0].instrument == HOOK
    assert 19 <= ivs[0].duration <= 21
    stats = timeline.usage_stats(ivs, a.duration).set_index("instrument")
    assert stats.loc["hook", "segments"] == 1
    assert stats.loc["grasper", "active_seconds"] == 0


def test_gap_merging_and_splitting():
    a = make_analysis({HOOK: [(10, 20), (25, 35), (80, 90)]}, duration=100)
    _, _, ivs = timeline.build_intervals(a, smooth_window=1, max_gap=10)
    assert len(ivs) == 2           # 20->25 gap merged, 35->80 gap kept apart
    _, _, ivs = timeline.build_intervals(a, smooth_window=1, max_gap=2)
    assert len(ivs) == 3


def test_smoothing_removes_one_sample_flicker():
    a = make_analysis({HOOK: [(10, 40)]}, duration=60)
    # punch a one-sample hole in the middle of the segment
    for f in a.frames:
        if f.t == 25:
            f.boxes = []
    # samples are 1 s apart: a 1.5 s merge gap bridges neighbours but not the 2 s hole
    _, _, raw = timeline.build_intervals(a, smooth_window=1, max_gap=1.5)
    _, _, smooth = timeline.build_intervals(a, smooth_window=3, max_gap=1.5)
    assert len(raw) == 2 and len(smooth) == 1


def test_confidence_threshold():
    a = make_analysis({HOOK: [(10, 20)]}, duration=40)
    _, _, ivs = timeline.build_intervals(a, conf=0.95, smooth_window=1)
    assert ivs == []


def test_phase_segments_are_contiguous():
    a = make_analysis({HOOK: [(0, 99)]}, duration=90)
    segs = timeline.phase_segments(a)
    assert [s.phase for s in segs] == [0, 1, 2]
    assert all(x.end == y.start for x, y in zip(segs, segs[1:]))
    assert abs(timeline.phase_stats(segs)["pct"].sum() - 100) < 0.5


def test_empty_analysis():
    a = make_analysis({}, duration=10)
    _, _, ivs = timeline.build_intervals(a)
    assert ivs == [] and timeline.case_metrics(ivs, 10)["instrument_entries"] == 0


def test_fmt_time():
    assert timeline.fmt_time(75) == "01:15" and timeline.fmt_time(3725) == "1:02:05"


def test_flags():
    a = make_analysis({HOOK: [(0, 400)], CLIP: [(450, 452), (460, 462)]}, duration=900)
    times, _, ivs = timeline.build_intervals(a, smooth_window=1, max_gap=5)
    kinds = {f.kind for f in review_flags(ivs, a.duration, times, dense=True, long_use_s=300, idle_gap_s=120)}
    assert "long_use" in kinds and "idle_gap" in kinds and "clipper_segments" in kinds
    # sparse sampling must never produce idle-gap flags
    kinds = {f.kind for f in review_flags(ivs, a.duration, times, dense=False, long_use_s=300, idle_gap_s=120)}
    assert "idle_gap" not in kinds


def test_median_step():
    assert timeline.median_step(np.array([0, 2, 4, 6.0])) == 2.0
    assert timeline.median_step(np.array([5.0])) == 1.0


def test_smooth_handles_series_shorter_than_the_window():
    import numpy as np
    for n in (1, 2, 3, 6):
        m = np.ones((n, 2), dtype=bool)
        out = timeline.smooth(m, 3)
        assert out.shape == m.shape
    a = np.array([[0], [1], [1], [1], [0]], dtype=bool)
    assert timeline.smooth(a, 3)[:, 0].tolist() == [False, True, True, True, False]
