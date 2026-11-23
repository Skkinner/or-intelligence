"""Temporal smoothing: noisy per-frame detections -> stable per-tool presence.

WBS 4.1.1 · Owner: Member C · Branch: feature/member-c-4.1.1-smoothing
Depends on: 1.2.2 only. Develop and test against tests/fixtures/sample_detections.jsonl (no real model needed).

Parameters live in configs/timeline.yaml (conf, window_s, method, on, off).

Acceptance:
    - tests/unit/timeline/test_smoothing.py passes.
    - On the fixture, segment count drops >= 50% vs raw thresholding, and no segment > 2 s is lost.
"""

from __future__ import annotations

from collections.abc import Iterable
from typing import Literal

import numpy as np

from src.common.contracts import class_names

N_TOOLS = len(class_names())  # 6


def presence_matrix(dets: Iterable[dict], conf: float) -> tuple[np.ndarray, np.ndarray]:
    """Convert detection records (contract C4) into a [T, 6] matrix of per-tool max confidence.

    Returns ``(times, matrix)`` where ``times[t]`` is the record timestamp and ``matrix[t, k]`` is the max
    confidence of tool k in frame t if >= ``conf``, else 0.

    TODO(C, 4.1.1): iterate records in order; for each det with conf >= threshold keep the per-class max.
    """
    raise NotImplementedError("WBS 4.1.1 (Member C)")


def smooth(
    matrix: np.ndarray,
    fps: float,
    window_s: float = 2.0,
    method: Literal["majority", "hysteresis", "none"] = "majority",
    on: float = 0.6,
    off: float = 0.4,
) -> np.ndarray:
    """Return a boolean [T, 6] presence array.

    - ``majority``: tool present at t if it is present in > 50% of frames in a centred window of ``window_s``.
    - ``hysteresis``: switch on when the windowed presence ratio >= ``on``, off when it drops <= ``off``.
    - ``none``: raw thresholding (matrix > 0), used as the baseline in 4.1.3.

    TODO(C, 4.1.1): implement with a moving average over int(round(window_s * fps)) frames.
    """
    raise NotImplementedError("WBS 4.1.1 (Member C)")
