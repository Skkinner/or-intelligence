"""Glue between storage, datasets and analysis. The UI and the CLI scripts both call this."""
from __future__ import annotations

import uuid
from pathlib import Path
from typing import Callable

from . import analysis as an
from . import config, db, timeline
from .data import cholect50
from .detector import Detector
from .models import CaseAnalysis


def timeline_params(overrides: dict | None = None) -> dict:
    p = {**config.DEFAULTS, **(overrides or {})}
    return {"conf": p["conf"], "smooth_window": int(p["smooth"]), "max_gap": p["max_gap"]}


def load_analysis(case) -> CaseAnalysis:
    return CaseAnalysis.load(case["analysis_path"])


def refresh_estimated_phases(analysis: CaseAnalysis, conf: float | None = None) -> CaseAnalysis:
    """Stored estimates made before confidence/excerpt handling existed (or with a changed model) are recomputed
    from the stored detections, so what is shown always comes from the current estimator."""
    if analysis.params.get("phase_source") != "estimated" or not config.PHASE_MODEL_PATH.exists():
        return analysis
    from .phase_estimator import PhaseEstimator
    return PhaseEstimator.load(config.PHASE_MODEL_PATH).apply(
        analysis, conf=conf if conf is not None else config.DEFAULTS["conf"])


def _store(analysis: CaseAnalysis, name: str) -> Path:
    config.ensure_dirs()
    path = config.ANALYSIS_DIR / f"{name}.json"
    analysis.save(path)
    return path


def import_cholect50(root: str | Path, owner_id: int | None) -> list[int]:
    """Create one case per video of a CholecT50 challenge-validation folder (ground-truth replay)."""
    new_ids: list[int] = []
    for vid, (analysis, frames_dir) in cholect50.load_root(root).items():
        if db.find_public_case(vid, "cholect50"):
            continue
        path = _store(analysis, f"{vid}_annotations_{uuid.uuid4().hex[:6]}")
        new_ids.append(db.add_case(
            title=f"CholecT50 {vid} (public dataset)", media_kind="frames", media_path=str(frames_dir),
            analysis_path=str(path), source="annotations", owner_id=owner_id, video_id=vid,
            detector=analysis.detector, tags="public-dataset,cholect50", consent=True,
            duration=analysis.duration, n_frames=len(analysis.frames), procedure="lap-chole",
            stats=timeline.summary(analysis, **timeline_params())))
    return new_ids


def import_cataract101(root: str | Path, owner_id: int | None, limit: int | None = None,
                       step_s: float = 1.0) -> dict:
    """One case per Cataract-101 video that has a matching annotation CSV. The videos stay where they are
    (they are referenced, not copied). Returns {"ids": [...], "skipped": {video: reason}, "unmatched": [...]}."""
    from .data import cataract101
    found = cataract101.scan(root)
    ids: list[int] = []
    skipped: dict[str, str] = {}
    for video, ann in list(found.matched.items())[: limit or None]:
        if db.find_public_case(video.stem, "cataract101"):
            continue
        try:
            analysis = cataract101.build_analysis(
                video, ann, step_s=step_s,
                change_points=(found.combined or {}).get(video.stem.lower()) if found.combined else None)
        except (ValueError, OSError) as e:          # AnnotationFormatError is a ValueError
            skipped[video.name] = str(e)
            continue
        path = _store(analysis, f"cataract101_{video.stem}_{uuid.uuid4().hex[:6]}")
        ids.append(db.add_case(
            title=f"Cataract-101 {video.stem} (public dataset)", media_kind="video", media_path=str(video),
            analysis_path=str(path), source="annotations", owner_id=owner_id, video_id=video.stem,
            detector=analysis.detector, tags="public-dataset,cataract101", consent=True,
            duration=analysis.duration, n_frames=len(analysis.frames), procedure="cataract",
            stats=timeline.summary(analysis, **timeline_params())))
    return {"ids": ids, "skipped": skipped, "unmatched": [v.name for v in found.unmatched]}


def run_model_on_case(case_id: int, detector: Detector, step_s: float = 1.0,
                      progress: Callable[[float], None] | None = None) -> CaseAnalysis:
    case = db.get_case(case_id)
    if case is None:
        raise KeyError(case_id)
    if case["media_kind"] == "frames":
        result = an.analyze_frames(case["media_path"], detector, case["video_id"] or f"case{case_id}", progress=progress)
    else:
        result = an.analyze_video_file(case["media_path"], detector, step_s=step_s, progress=progress)
    path = _store(result, f"case{case_id}_model_{uuid.uuid4().hex[:6]}")
    old = case["analysis_path"]
    db.update_case(case_id, analysis_path=str(path), source="model", detector=detector.name,
                   duration=result.duration, n_frames=len(result.frames),
                   stats_json=timeline.summary(result, **timeline_params()))
    if Path(old).parent.resolve() == config.ANALYSIS_DIR.resolve() and Path(old) != path:
        Path(old).unlink(missing_ok=True)
    return result


def create_video_case(*, data: bytes, filename: str, title: str, owner_id: int, trainee_id: int | None,
                      tags: str, retention_days: int | None, detector: Detector, step_s: float,
                      progress: Callable[[float], None] | None = None) -> int:
    config.ensure_dirs()
    ext = Path(filename).suffix.lower() or ".mp4"
    media = config.UPLOAD_DIR / f"{uuid.uuid4().hex}{ext}"
    media.write_bytes(data)
    try:
        result = an.analyze_video_file(media, detector, step_s=step_s, progress=progress)
    except Exception:
        media.unlink(missing_ok=True)
        raise
    path = _store(result, f"upload_{uuid.uuid4().hex[:8]}")
    return db.add_case(
        title=title, media_kind="video", media_path=str(media), analysis_path=str(path), source="model",
        owner_id=owner_id, trainee_id=trainee_id, video_id=media.stem, detector=detector.name, tags=tags,
        consent=True, retention_days=retention_days, duration=result.duration, n_frames=len(result.frames),
        stats=timeline.summary(result, **timeline_params()))




def save_live_case(analysis: CaseAnalysis, video_path: str | Path, title: str, owner_id: int,
                   retention_days: int | None = None) -> int:
    """Store a finished live analysis as a case: copy the video into the platform folder and, when the phase
    estimator is available, recompute the phases offline over the whole video (more accurate than the live ones)."""
    import shutil
    from .phase_estimator import PhaseEstimator

    config.ensure_dirs()
    ext = Path(video_path).suffix.lower() or ".mp4"
    media = config.UPLOAD_DIR / f"{uuid.uuid4().hex}{ext}"
    shutil.copy(video_path, media)
    if config.PHASE_MODEL_PATH.exists():
        analysis = PhaseEstimator.load(config.PHASE_MODEL_PATH).apply(analysis)
    path = _store(analysis, f"live_{uuid.uuid4().hex[:8]}")
    return db.add_case(
        title=title, media_kind="video", media_path=str(media), analysis_path=str(path), source="model",
        owner_id=owner_id, video_id=media.stem, detector=analysis.detector, tags="live", consent=True,
        retention_days=retention_days, duration=analysis.duration, n_frames=len(analysis.frames),
        procedure="lap-chole", stats=timeline.summary(analysis, **timeline_params()))
