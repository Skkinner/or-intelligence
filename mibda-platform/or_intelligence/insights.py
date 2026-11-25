"""Rule-based review flags.

These are pointers for a human reviewer ("look here"), NOT error detection or
scoring of the surgeon. Rules only use instrument presence over time.
"""
from __future__ import annotations

from dataclasses import dataclass

from .constants import INSTRUMENTS
from .timeline import Interval


@dataclass
class Flag:
    kind: str                 # long_use | frequent_entries | idle_gap | clipper_segments
    start: float
    end: float
    instrument: int | None = None
    value: float = 0.0


def review_flags(
    intervals: list[Interval],
    duration: float,
    times,
    *,
    dense: bool,
    long_use_s: float = 300.0,
    switch_window_s: float = 60.0,
    switch_count: int = 6,
    idle_gap_s: float = 120.0,
    instrument_names: list[str] | None = None,
) -> list[Flag]:
    flags: list[Flag] = []

    for iv in intervals:
        if iv.duration >= long_use_s:
            flags.append(Flag("long_use", iv.start, iv.end, iv.instrument, iv.duration))

    starts = sorted(iv.start for iv in intervals)
    i = 0
    last_end = -1.0
    for j, s in enumerate(starts):
        while starts[i] < s - switch_window_s:
            i += 1
        n = j - i + 1
        if n >= switch_count and s > last_end:
            flags.append(Flag("frequent_entries", starts[i], s + switch_window_s, None, n))
            last_end = s + switch_window_s

    if dense and len(intervals):
        covered = sorted((iv.start, iv.end) for iv in intervals)
        cursor = 0.0
        for a, b in covered:
            if a - cursor >= idle_gap_s:
                flags.append(Flag("idle_gap", cursor, a, None, a - cursor))
            cursor = max(cursor, b)
        if duration - cursor >= idle_gap_s:
            flags.append(Flag("idle_gap", cursor, duration, None, duration - cursor))

    names = instrument_names if instrument_names is not None else INSTRUMENTS
    clip = names.index("clipper") if "clipper" in names else None
    clip_ivs = [iv for iv in intervals if clip is not None and iv.instrument == clip]
    if clip_ivs:
        flags.append(Flag("clipper_segments", clip_ivs[0].start, clip_ivs[-1].end, clip, len(clip_ivs)))

    flags.sort(key=lambda f: f.start)
    return flags
