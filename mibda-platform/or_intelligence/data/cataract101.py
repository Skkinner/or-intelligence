"""Adapter for Cataract-101 (ITEC, Klagenfurt; CC BY-NC 4.0): 101 cataract-surgery videos with phase annotations.

Verified against the real release (cataract-101/): videos/case_<id>.mp4 (25 fps), and ONE semicolon-separated
annotations.csv with header VideoID;FrameNo;Phase holding only the START frame of each phase (zero-based frame; the phase
runs to the next row or the video end; the part before the first row is unannotated). phases.csv maps ids 1-10 to names.
The older tolerant per-video CSV parser is kept as a fallback for other layouts.
"""
from __future__ import annotations

import csv
import io
from dataclasses import dataclass
from pathlib import Path

import cv2
import numpy as np

from ..models import CaseAnalysis, FrameResult

VIDEO_EXT = {".mp4", ".avi", ".mov", ".mkv", ".mpg", ".mpeg"}
N_PHASES = 10


class AnnotationFormatError(ValueError):
    """The annotation file does not look like any layout this adapter understands."""


@dataclass
class Scan:
    videos: list[Path]
    matched: dict[Path, Path]         # video -> annotation csv
    unmatched: list[Path]
    other_csvs: list[Path]
    combined: dict[str, list[tuple[int, int]]] | None = None   # video stem -> change points (single annotations.csv)


# ---- finding files ------------------------------------------------------------------
def scan(root: str | Path) -> Scan:
    root = Path(root)
    videos = sorted(p for p in root.rglob("*") if p.is_file() and p.suffix.lower() in VIDEO_EXT)
    csvs = [p for p in root.rglob("*.csv")]
    by_stem = {p.stem.lower(): p for p in csvs}
    matched: dict[Path, Path] = {}
    for v in videos:
        hit = by_stem.get(v.stem.lower())
        if hit is not None:
            matched[v] = hit
    combined = None
    for c in csvs:
        if c.name.lower() == "annotations.csv":
            try:
                combined = parse_combined(c)
            except AnnotationFormatError:
                combined = None
            break
    if combined:
        for v in videos:
            if v.stem.lower() in combined:
                matched[v] = next(c for c in csvs if c.name.lower() == "annotations.csv")
    used = set(matched.values())
    return Scan(videos, matched, [v for v in videos if v not in matched], [c for c in csvs if c not in used], combined)


def parse_combined(path: str | Path, n_phases: int = N_PHASES) -> dict[str, list[tuple[int, int]]]:
    """annotations.csv with header VideoID;FrameNo;Phase -> {"case_<id>": [(start_frame, phase_0based)]}."""
    text = Path(path).read_text(encoding="utf-8-sig", errors="replace")
    rd = csv.DictReader(io.StringIO(text), delimiter=";")
    if not rd.fieldnames or [h.strip().lower() for h in rd.fieldnames] != ["videoid", "frameno", "phase"]:
        raise AnnotationFormatError(f"{path}: not a VideoID;FrameNo;Phase file")
    out: dict[str, list[tuple[int, int]]] = {}
    for r in rd:
        vid, fr, ph = (int(r[k].strip()) for k in rd.fieldnames)
        if not 1 <= ph <= n_phases:
            raise AnnotationFormatError(f"{path}: phase id {ph} outside 1-{n_phases}")
        out.setdefault(f"case_{vid}", []).append((fr, ph - 1))
    return {k: sorted(v) for k, v in out.items()}


# ---- parsing phase annotations --------------------------------------------------------
def _is_num(s: str) -> bool:
    try:
        float(s.strip().replace(",", "."))
        return True
    except ValueError:
        return False


def _read_rows(path: Path) -> list[list[str]]:
    text = Path(path).read_text(encoding="utf-8-sig", errors="replace")
    try:
        dialect = csv.Sniffer().sniff(text[:2048], delimiters=",;\t ")
    except csv.Error:
        dialect = csv.excel
    return [[c.strip() for c in r] for r in csv.reader(io.StringIO(text), dialect) if any(c.strip() for c in r)]


def _runs(frames: list[int], phases: list[int]) -> list[tuple[int, int]]:
    out: list[tuple[int, int]] = []
    for f, p in zip(frames, phases):
        if not out or out[-1][1] != p:
            out.append((f, p))
    return out


def parse_phase_csv(path: str | Path, n_phases: int = N_PHASES) -> list[tuple[int, int]]:
    """Return change points [(start_frame, phase_index_0based)], sorted by frame.

    Understood layouts (header optional): (frame, phase) per-frame labels; (frame, phase) phase-start boundaries;
    (start, end, phase) intervals; (phase, start) boundaries. Anything else raises AnnotationFormatError.
    """
    rows = _read_rows(Path(path))
    if not rows:
        raise AnnotationFormatError(f"{path}: empty file")
    header: list[str] | None = None
    if not all(_is_num(c) for c in rows[0]):
        header = [c.lower() for c in rows[0]]
        rows = rows[1:]
    num = [[float(c.replace(",", ".")) for c in r if _is_num(c)] for r in rows]
    num = [r for r in num if r]
    if not num:
        raise AnnotationFormatError(f"{path}: no numeric rows")
    width = max(len(r) for r in num)
    num = [r for r in num if len(r) == width]
    cols = list(zip(*num))

    def looks_phase(col) -> bool:
        return all(float(v).is_integer() and 0 <= v <= n_phases for v in col)

    named = {}
    if header and len(header) >= width:
        for i, h in enumerate(header[:width]):
            for key in ("phase", "label", "class", "start", "begin", "end", "stop", "frame"):
                if key in h and key not in named:
                    named[key] = i
    ph_idx = named.get("phase", named.get("label", named.get("class")))

    if width == 2:
        if ph_idx is None:
            cand = [i for i in (0, 1) if looks_phase(cols[i])]
            if len(cand) == 2:   # both small: the one with more distinct values is the frame/time column
                cand = [min((0, 1), key=lambda i: len(set(cols[i])))]
            if len(cand) != 1:
                raise AnnotationFormatError(f"{path}: cannot tell which of the 2 columns is the phase")
            ph_idx = cand[0]
        fr_idx = 1 - ph_idx
        frames, phases = [int(v) for v in cols[fr_idx]], [int(v) for v in cols[ph_idx]]
        order = np.argsort(frames, kind="stable")
        cps = _runs([frames[i] for i in order], [phases[i] for i in order])
    elif width == 3:
        if ph_idx is None:
            cand = [i for i in range(3) if looks_phase(cols[i])]
            if len(cand) != 1:
                raise AnnotationFormatError(f"{path}: cannot tell which of the 3 columns is the phase")
            ph_idx = cand[0]
        start_idx, end_idx = [i for i in range(3) if i != ph_idx]
        if any(e < s for s, e in zip(cols[start_idx], cols[end_idx])):
            start_idx, end_idx = end_idx, start_idx
        if any(e < s for s, e in zip(cols[start_idx], cols[end_idx])):
            raise AnnotationFormatError(f"{path}: interval columns are not (start <= end)")
        order = np.argsort(cols[start_idx], kind="stable")
        cps = _runs([int(cols[start_idx][i]) for i in order], [int(cols[ph_idx][i]) for i in order])
    else:
        raise AnnotationFormatError(f"{path}: {width} numeric columns is not a supported layout")

    ids = [p for _, p in cps]
    if min(ids) >= 1 and max(ids) <= n_phases:        # 1-based ids -> 0-based
        cps = [(f, p - 1) for f, p in cps]
    if min(p for _, p in cps) < 0 or max(p for _, p in cps) >= n_phases:
        raise AnnotationFormatError(f"{path}: phase ids {sorted(set(ids))} do not fit {n_phases} phases")
    return cps


def phase_at(change_points: list[tuple[int, int]], frame: int) -> int | None:
    cur = None
    for f, p in change_points:
        if f <= frame:
            cur = p
        else:
            break
    return cur


# ---- building a case ------------------------------------------------------------------------
def video_info(path: Path) -> tuple[float, int]:
    cap = cv2.VideoCapture(str(path))
    try:
        if not cap.isOpened():
            raise ValueError(f"Cannot open video: {path}")
        return float(cap.get(cv2.CAP_PROP_FPS) or 25.0), int(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
    finally:
        cap.release()


def build_analysis(video: Path, annotation: Path, step_s: float = 1.0,
                   change_points: list[tuple[int, int]] | None = None) -> CaseAnalysis:
    fps, n_frames = video_info(video)
    if n_frames <= 0:
        raise ValueError(f"{video}: video reports no frames")
    cps = change_points if change_points is not None else parse_phase_csv(annotation)
    duration = n_frames / fps
    frames = [FrameResult(t=round(float(t), 3), phase=phase_at(cps, int(t * fps)))
              for t in np.arange(0.0, duration, step_s)]
    return CaseAnalysis(
        video_id=video.stem, source="annotations", duration=duration, frames=frames,
        detector="Cataract-101 phase annotations (dataset labels, not model output)",
        params={"dense": True, "fps": fps, "step_s": step_s}, procedure="cataract")
