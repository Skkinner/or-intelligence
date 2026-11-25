"""Estimate the surgical phase over time from the instrument timeline alone.

This is deliberately small: a multinomial logistic regression on instrument-usage features,
followed by a left-to-right Viterbi decode (surgery moves forward through its phases, with
rare steps back). It needs no GPU and runs on detections from any detector.

Honest limits: trained on very few videos; features use the whole recording (cumulative usage,
relative time), so it is for OFFLINE review, not live use. Accuracy is reported by
leave-one-video-out evaluation in models/phase_metrics.json.
"""
from __future__ import annotations

import json
from dataclasses import replace
from pathlib import Path

import numpy as np

from .constants import N_INSTRUMENTS
from .models import CaseAnalysis
from .timeline import presence

WINDOWS = (30.0, 90.0)      # seconds, centred


def features(times: np.ndarray, m: np.ndarray, duration: float) -> np.ndarray:
    """One row per sample: windowed instrument presence, cumulative usage share, relative time."""
    n = len(times)
    if n == 0:
        return np.zeros((0, N_INSTRUMENTS * (len(WINDOWS) + 1) + 1))
    mf = m.astype(float)
    cols = []
    for w in WINDOWS:
        win = np.zeros_like(mf)
        for i in range(n):
            sel = np.abs(times - times[i]) <= w
            win[i] = mf[sel].mean(axis=0)
        cols.append(win)
    cum = np.cumsum(mf, axis=0)
    total = np.maximum(cum[-1], 1e-9)
    cols.append(cum / total)
    rel = (times / max(duration, 1e-9))[:, None]
    return np.hstack(cols + [rel])


def left_to_right_transitions(k: int, stay: float = 0.97, forward: float = 0.02, skip: float = 0.005, back: float = 0.0005) -> np.ndarray:
    t = np.zeros((k, k))
    for i in range(k):
        for j in range(k):
            t[i, j] = stay if j == i else forward if j == i + 1 else skip if j > i + 1 else back
        t[i] /= t[i].sum()
    return t


def viterbi(log_p: np.ndarray, trans: np.ndarray, start_at_first: bool = True) -> np.ndarray:
    n, k = log_p.shape
    lt = np.log(trans)
    score = np.full((n, k), -np.inf)
    back = np.zeros((n, k), dtype=int)
    # a complete operation starts in the first phase; an excerpt can start anywhere
    prior = np.where(np.arange(k) == 0, 0.8, 0.2 / max(k - 1, 1)) if start_at_first else np.full(k, 1.0 / k)
    score[0] = log_p[0] + np.log(prior)
    for i in range(1, n):
        cand = score[i - 1][:, None] + lt
        back[i] = cand.argmax(axis=0)
        score[i] = cand.max(axis=0) + log_p[i]
    path = np.zeros(n, dtype=int)
    path[-1] = score[-1].argmax()
    for i in range(n - 1, 0, -1):
        path[i - 1] = back[i, path[i]]
    return path


def neutralise_global(x: np.ndarray, mean: np.ndarray, n_instr: int = N_INSTRUMENTS) -> np.ndarray:
    """Replace the whole-operation features (cumulative usage share, relative time) with their training mean.

    Those features only mean something when the recording is the COMPLETE operation. For a clip cut out of a longer
    operation they would force the video through every phase from first to last (e.g. a 4-minute excerpt ending in
    'gallbladder extraction'), so excerpts use the local instrument pattern only."""
    x = x.copy()
    x[:, len(WINDOWS) * n_instr:] = mean[len(WINDOWS) * n_instr:]
    return x


def features_last(times: np.ndarray, m: np.ndarray, duration: float) -> np.ndarray:
    """Feature row for the LAST sample only, using nothing after it (for live use).

    The offline model divides cumulative usage by the usage over the whole video, which is unknown live; here the
    total is extrapolated from the share of the video seen so far, so this is an approximation of `features`."""
    t = float(times[-1])
    mf = m.astype(float)
    parts = []
    for w in WINDOWS:
        parts.append(mf[np.abs(times - t) <= w].mean(axis=0))
    cum = mf.sum(axis=0)
    seen = max(t / max(duration, 1e-9), 1e-3)
    parts.append(np.clip(cum / np.maximum(cum / seen, 1e-9), 0.0, 1.0) if cum.sum() else np.zeros_like(cum))
    return np.concatenate(parts + [np.array([t / max(duration, 1e-9)])])[None, :]


class OnlinePhase:
    """Causal phase estimate: left-to-right forward filtering over the estimator's per-sample probabilities."""

    def __init__(self, est: "PhaseEstimator", duration: float, complete: bool = False):
        self.est, self.duration, self.complete = est, duration, complete
        k = len(est.classes)
        self.trans = left_to_right_transitions(k)
        self.belief = np.where(np.arange(k) == 0, 0.8, 0.2 / max(k - 1, 1))
        self.times: list[float] = []
        self.rows: list[np.ndarray] = []

    def update(self, t: float, present: np.ndarray) -> int:
        self.times.append(float(t))
        self.rows.append(np.asarray(present, bool))
        p = self.est.predict_proba(features_last(np.array(self.times), np.array(self.rows), self.duration),
                                   local_only=not self.complete)[0]
        b = (self.belief @ self.trans) * np.clip(p, 1e-9, 1.0)
        self.belief = b / b.sum()
        return int(self.est.classes[int(self.belief.argmax())])


class PhaseEstimator:
    def __init__(self, classes, mean, scale, coef, intercept, meta: dict | None = None):
        self.classes = np.asarray(classes, dtype=int)
        self.mean, self.scale = np.asarray(mean, float), np.asarray(scale, float)
        self.coef, self.intercept = np.asarray(coef, float), np.asarray(intercept, float)
        self.meta = meta or {}

    def predict_proba(self, x: np.ndarray, local_only: bool = False) -> np.ndarray:
        if local_only:
            x = neutralise_global(x, self.mean)
        z = ((x - self.mean) / self.scale) @ self.coef.T + self.intercept
        z -= z.max(axis=1, keepdims=True)
        e = np.exp(z)
        return e / e.sum(axis=1, keepdims=True)

    def estimate_matrix(self, times: np.ndarray, m: np.ndarray, duration: float, complete: bool = False):
        """(phase id per sample, confidence per sample). `complete` = the recording is the whole operation."""
        if len(times) == 0:
            return np.zeros(0, dtype=int), np.zeros(0)
        p = self.predict_proba(features(times, m, duration), local_only=not complete)
        k = len(self.classes)
        log_p = np.log(np.clip(p, 1e-9, 1.0))
        path = viterbi(log_p, left_to_right_transitions(k), start_at_first=complete)
        return self.classes[path], p[np.arange(len(path)), path]

    def apply(self, analysis: CaseAnalysis, conf: float = 0.25, complete: bool | None = None) -> CaseAnalysis:
        """Copy of `analysis` with an estimated phase (and its confidence) on every frame.
        `complete` defaults to analysis.params["complete_operation"], which is False unless someone says so."""
        if complete is None:
            complete = bool(analysis.params.get("complete_operation", False))
        frames = sorted(analysis.frames, key=lambda f: f.t)
        times, m = presence(replace(analysis, frames=frames), conf)
        phases, confs = self.estimate_matrix(times, m, analysis.duration, complete)
        new_frames = [replace(f, phase=int(p), phase_conf=round(float(c), 3)) for f, p, c in zip(frames, phases, confs)]
        return replace(analysis, frames=new_frames,
                       params={**analysis.params, "phase_source": "estimated", "complete_operation": complete})

    # ---- persistence (JSON, no pickle) ----
    def save(self, path: str | Path) -> None:
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        Path(path).write_text(json.dumps({
            "classes": self.classes.tolist(), "mean": self.mean.tolist(), "scale": self.scale.tolist(),
            "coef": self.coef.tolist(), "intercept": self.intercept.tolist(), "meta": self.meta}), encoding="utf-8")

    @classmethod
    def load(cls, path: str | Path) -> "PhaseEstimator":
        d = json.loads(Path(path).read_text(encoding="utf-8"))
        return cls(d["classes"], d["mean"], d["scale"], d["coef"], d["intercept"], d.get("meta"))
