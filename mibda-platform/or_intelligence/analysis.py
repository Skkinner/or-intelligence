"""Run a detector over frames or a video file and produce a CaseAnalysis."""
from __future__ import annotations

from pathlib import Path
from typing import Callable

import cv2
import numpy as np

from .detector import Detector
from .models import CaseAnalysis, FrameResult
from .privacy import is_blank, sanitize

Progress = Callable[[float], None]
IMG_EXT = {".png", ".jpg", ".jpeg"}


def analyze_frames(frames_dir: str | Path, detector: Detector, video_id: str, fps: float = 1.0,
                   progress: Progress | None = None) -> CaseAnalysis:
    """Frame-sequence cases (file names are frame numbers sampled at `fps`)."""
    frames_dir = Path(frames_dir)
    names = sorted((p.name for p in frames_dir.iterdir() if p.suffix.lower() in IMG_EXT), key=lambda n: int(Path(n).stem))
    results: list[FrameResult] = []
    for i, name in enumerate(names):
        img = cv2.imread(str(frames_dir / name))
        boxes = [] if img is None or is_blank(img) else detector.detect(img)
        results.append(FrameResult(t=int(Path(name).stem) / fps, image=name, boxes=boxes))
        if progress:
            progress((i + 1) / len(names))
    duration = results[-1].t + 1.0 if results else 0.0
    return CaseAnalysis(video_id=video_id, source="model", duration=duration, frames=results,
                        detector=detector.name, params={"dense": False, "fps": fps})


def analyze_video_file(path: str | Path, detector: Detector, step_s: float = 1.0,
                       progress: Progress | None = None) -> CaseAnalysis:
    cap = cv2.VideoCapture(str(path))
    if not cap.isOpened():
        raise ValueError(f"Cannot open video: {path}")
    fps = cap.get(cv2.CAP_PROP_FPS) or 25.0
    n_frames = cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0
    duration = n_frames / fps if n_frames else 0.0
    results: list[FrameResult] = []
    t = 0.0
    try:
        while duration == 0.0 or t < duration:
            cap.set(cv2.CAP_PROP_POS_MSEC, t * 1000.0)
            ok, img = cap.read()
            if not ok:
                break
            boxes = [] if is_blank(img) else detector.detect(img)
            results.append(FrameResult(t=round(t, 3), boxes=boxes))
            t += step_s
            if progress and duration:
                progress(min(1.0, t / duration))
    finally:
        cap.release()
    if duration == 0.0 and results:
        duration = results[-1].t + step_s
    return CaseAnalysis(video_id=Path(path).stem, source="model", duration=duration, frames=results,
                        detector=detector.name, params={"dense": True, "step_s": step_s})


def read_video_frame(path: str | Path, t: float, privacy: bool = True) -> np.ndarray | None:
    """Frame at time t for display. With privacy=True faces are blurred and blank frames flagged."""
    cap = cv2.VideoCapture(str(path))
    try:
        cap.set(cv2.CAP_PROP_POS_MSEC, t * 1000.0)
        ok, img = cap.read()
    finally:
        cap.release()
    if not ok:
        return None
    return sanitize(img)[0] if privacy else img
