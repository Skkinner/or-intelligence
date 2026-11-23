"""Session PDF report in English or Arabic (RTL).

WBS 4.3.1 · Owner: Member C · Branch: feature/member-c-4.3.1-pdf
Depends on: 4.1.2, 4.2.2 · Reviewed visually (Arabic) by Member A in 5.2.3.

Content: case info, colour-coded timeline bars (colours from contracts/classes.json), per-tool stats,
instructor notes with timestamps, and the disclaimer "educational tool, not diagnostic".

Arabic: bundle Noto Naskh Arabic (OFL) in src/reports/fonts/; shape with arabic_reshaper + python-bidi; right-align.

Acceptance:
    - EN and AR PDFs render with correct shaping and RTL layout.
    - Includes timeline chart, stats, notes and the disclaimer.
    - tests/unit/reports: golden test generates both languages from fixtures; pypdf finds the note text.
"""

from __future__ import annotations

from typing import Literal

from src.reports.strings import t


def fmt_time(seconds: float) -> str:
    """``192.0 -> "03:12"``; hours shown as ``h:mm:ss`` when needed."""
    s = int(round(seconds))
    h, rem = divmod(s, 3600)
    m, s = divmod(rem, 60)
    return f"{h}:{m:02d}:{s:02d}" if h else f"{m:02d}:{s:02d}"


def render_report(timeline: dict, notes: list[dict], lang: Literal["en", "ar"], out_path: str) -> str:
    """Render the report and return ``out_path``.

    TODO(C, 4.3.1): ReportLab canvas or platypus; use t(key, lang) for every visible string.
    """
    _ = t
    raise NotImplementedError("WBS 4.3.1 (Member C)")
