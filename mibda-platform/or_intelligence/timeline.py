"""Turn per-frame detections into instrument segments, usage statistics and phase segments."""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

from . import procedures
from .models import CaseAnalysis


UNCERTAIN_BELOW = 0.6


def proc_of(analysis: CaseAnalysis) -> procedures.Procedure:
    return procedures.resolve(analysis.procedure)


@dataclass
class Interval:
    instrument: int
    start: float
    end: float
    n_samples: int = 1

    @property
    def duration(self) -> float:
        return max(0.0, self.end - self.start)


@dataclass
class PhaseSegment:
    phase: int
    start: float
    end: float
    conf: float | None = None       # mean estimator confidence (None for ground-truth labels)
    verified: bool = True           # False when the phase is a model estimate, not an annotation

    @property
    def uncertain(self) -> bool:
        """Estimated phases are never presented as fact; low confidence or a very short stretch is flagged as well."""
        return (not self.verified) and ((self.conf or 0.0) < UNCERTAIN_BELOW or (self.end - self.start) < 10.0)


def fmt_time(seconds: float) -> str:
    s = int(round(max(0.0, seconds)))
    h, rem = divmod(s, 3600)
    m, sec = divmod(rem, 60)
    return f"{h:d}:{m:02d}:{sec:02d}" if h else f"{m:02d}:{sec:02d}"


def median_step(times: np.ndarray) -> float:
    if len(times) < 2:
        return 1.0
    step = float(np.median(np.diff(np.sort(times))))
    return step if step > 0 else 1.0


def presence(analysis: CaseAnalysis, conf: float = 0.25) -> tuple[np.ndarray, np.ndarray]:
    """Return (times, presence matrix [n_samples, n_instruments])."""
    frames = sorted(analysis.frames, key=lambda f: f.t)
    times = np.array([f.t for f in frames], dtype=float)
    n_instr = proc_of(analysis).n_instruments       # 0 for procedures without instrument labels
    m = np.zeros((len(frames), n_instr), dtype=bool)
    for i, f in enumerate(frames):
        for b in f.boxes:
            if b.conf >= conf and 0 <= b.instrument < n_instr:
                m[i, b.instrument] = True
    return times, m


def smooth(matrix: np.ndarray, window: int = 3) -> np.ndarray:
    """Majority filter along time, per instrument. Removes one-sample flicker."""
    if window <= 1 or len(matrix) == 0:
        return matrix.copy()
    k = window if window % 2 else window + 1
    need = k // 2 + 1
    out = np.zeros_like(matrix)
    kernel = np.ones(k, dtype=int)
    for j in range(matrix.shape[1]):
        # zero-padded "same" convolution; np.convolve(mode="same") returns the LONGER input, which broke series shorter than k
        out[:, j] = np.convolve(np.pad(matrix[:, j].astype(int), k // 2), kernel, mode="valid") >= need
    return out


def build_intervals(
    analysis: CaseAnalysis,
    conf: float = 0.25,
    smooth_window: int = 3,
    max_gap: float = 15.0,
) -> tuple[np.ndarray, np.ndarray, list[Interval]]:
    """Group consecutive positive samples into per-instrument segments.

    Each sample stands for a window of one median sampling step, so a single
    positive sample becomes a segment of that length instead of zero.
    """
    times, raw = presence(analysis, conf)
    if len(times) == 0:
        return times, raw, []
    m = smooth(raw, smooth_window)
    step = median_step(times)
    pad = step / 2.0
    duration = analysis.duration if analysis.duration > 0 else float(times.max() + step)
    intervals: list[Interval] = []
    for j in range(m.shape[1]):
        pos = times[m[:, j]]
        if len(pos) == 0:
            continue
        start = prev = pos[0]
        n = 1
        for t in pos[1:]:
            if t - prev <= max_gap:
                prev = t
                n += 1
            else:
                intervals.append(Interval(j, max(0.0, start - pad), min(duration, prev + pad), n))
                start = prev = t
                n = 1
        intervals.append(Interval(j, max(0.0, start - pad), min(duration, prev + pad), n))
    intervals.sort(key=lambda iv: (iv.start, iv.instrument))
    return times, m, intervals


def usage_stats(intervals: list[Interval], duration: float, proc: procedures.Procedure | None = None) -> pd.DataFrame:
    proc = proc or procedures.get(procedures.DEFAULT_ID)
    rows = []
    for j, name in enumerate(proc.instrument_names):
        ivs = [iv for iv in intervals if iv.instrument == j]
        active = sum(iv.duration for iv in ivs)
        rows.append({
            "instrument": name,
            "active_seconds": round(active, 1),
            "pct_of_case": round(100.0 * active / duration, 1) if duration > 0 else 0.0,
            "segments": len(ivs),
            "first_use": min((iv.start for iv in ivs), default=None),
            "last_use": max((iv.end for iv in ivs), default=None),
            "longest_segment": round(max((iv.duration for iv in ivs), default=0.0), 1),
        })
    return pd.DataFrame(rows)


def case_metrics(intervals: list[Interval], duration: float) -> dict:
    entries = len(intervals)
    minutes = duration / 60.0 if duration > 0 else 0.0
    return {
        "duration_s": round(duration, 1),
        "instrument_entries": entries,
        "entries_per_min": round(entries / minutes, 2) if minutes > 0 else 0.0,
        "instruments_used": len({iv.instrument for iv in intervals}),
    }


def phase_segments(analysis: CaseAnalysis) -> list[PhaseSegment]:
    """Contiguous phase segments covering the recording from its first to its last sample.

    Boundaries sit where the labels change (ground-truth annotation or model estimate); nothing is spread evenly.
    Segments of estimated phases carry `verified=False` and their mean confidence."""
    frames = sorted((f for f in analysis.frames if f.phase is not None), key=lambda f: f.t)
    if not frames:
        return []
    verified = analysis.params.get("phase_source") != "estimated"
    segs: list[PhaseSegment] = []
    confs: list[list[float]] = []
    for f in frames:
        if segs and segs[-1].phase == f.phase:
            segs[-1].end = f.t
        else:
            segs.append(PhaseSegment(f.phase, f.t, f.t, verified=verified))
            confs.append([])
        if f.phase_conf is not None:
            confs[-1].append(f.phase_conf)
    for s, c in zip(segs, confs):
        s.conf = round(float(np.mean(c)), 2) if c else None
    for a, b in zip(segs, segs[1:]):
        a.end = b.start
    step = median_step(np.array([f.t for f in frames]))
    segs[-1].end = min(analysis.duration, segs[-1].end + step) if analysis.duration else segs[-1].end + step
    if segs[0].start <= 2 * step:                 # the first label covers the start of the recording
        segs[0].start = 0.0
    return segs


def phase_at(segments: list[PhaseSegment], t: float) -> PhaseSegment | None:
    """The segment playing at time t (the last one if t is at the very end)."""
    for s in segments:
        if s.start <= t < s.end:
            return s
    return segments[-1] if segments and t >= segments[-1].end else None


def phase_stats(segments: list[PhaseSegment]) -> pd.DataFrame:
    rows: dict[int, float] = {}
    for s in segments:
        rows[s.phase] = rows.get(s.phase, 0.0) + max(0.0, s.end - s.start)
    total = sum(rows.values()) or 1.0
    return pd.DataFrame(
        [{"phase": p, "seconds": round(v, 1), "pct": round(100 * v / total, 1)} for p, v in sorted(rows.items())]
    )


def summary(analysis: CaseAnalysis, **params) -> dict:
    """Compact summary stored in the database so the library can search without reloading files."""
    _, _, ivs = build_intervals(analysis, **params)
    stats = usage_stats(ivs, analysis.duration, proc_of(analysis))
    out = case_metrics(ivs, analysis.duration)
    out["usage"] = {r.instrument: r.active_seconds for r in stats.itertuples()}
    out["phases"] = sorted({s.phase for s in phase_segments(analysis)})
    return out


def frame_at(analysis: CaseAnalysis, t: float):
    """Nearest sampled frame to time t (or None for an empty case)."""
    if not analysis.frames:
        return None
    return min(analysis.frames, key=lambda f: abs(f.t - t))
