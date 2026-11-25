"""Phases shown to the user: contiguous, inside the recording, honest about estimates and excerpts."""
import numpy as np

from conftest import make_analysis
from or_intelligence import timeline
from or_intelligence.phase_estimator import PhaseEstimator, features


def _est(k=7):
    from or_intelligence.constants import N_INSTRUMENTS
    f = N_INSTRUMENTS * 3 + 1
    coef = np.zeros((k, f))
    coef[k - 1, -1] = 8.0                         # a model that is sure "late in the video" means the last phase
    coef[0, -1] = -8.0
    return PhaseEstimator(range(k), np.full(f, 0.5), np.ones(f), coef, np.zeros(k))


def test_excerpt_is_not_forced_through_the_whole_operation():
    a = make_analysis({0: [(0, 99)]}, duration=100)
    full = _est().apply(a, complete=True)
    part = _est().apply(a)                        # default: an excerpt of a longer operation
    assert full.frames[-1].phase == 6 and part.params["complete_operation"] is False
    assert len({f.phase for f in part.frames}) == 1          # no invented march from the first to the last phase
    assert all(0.0 <= f.phase_conf <= 1.0 for f in part.frames)


def test_estimated_segments_are_flagged_and_cover_the_recording():
    a = _est().apply(make_analysis({0: [(0, 99)]}, duration=100))
    segs = timeline.phase_segments(a)
    assert segs and all(not s.verified and s.conf is not None for s in segs)
    assert segs[0].start == 0.0 and segs[-1].end <= a.duration
    assert all(x.end == y.start for x, y in zip(segs, segs[1:]))


def test_annotated_segments_are_verified_and_phase_at_finds_the_playing_one():
    a = make_analysis({0: [(0, 99)]}, duration=90)
    segs = timeline.phase_segments(a)
    assert all(s.verified and not s.uncertain for s in segs)
    for s in segs:
        assert timeline.phase_at(segs, (s.start + s.end) / 2) is s
    assert timeline.phase_at([], 5) is None


def test_low_confidence_or_tiny_estimates_are_uncertain():
    s = timeline.PhaseSegment(1, 0, 100, conf=0.4, verified=False)
    assert s.uncertain
    assert not timeline.PhaseSegment(1, 0, 100, conf=0.9, verified=False).uncertain
    assert timeline.PhaseSegment(1, 0, 5, conf=0.9, verified=False).uncertain
