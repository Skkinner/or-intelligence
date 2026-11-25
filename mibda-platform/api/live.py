"""Live analysis: run the detector and the online phase estimator over a video in a background thread and let the
browser poll the results as they arrive (same pipeline as the Streamlit Live page)."""
from __future__ import annotations

import importlib.util
import io
import tempfile
import threading
import time
import uuid
from pathlib import Path

import cv2
import numpy as np
from fastapi import APIRouter, Depends, HTTPException, Request, Response
from pydantic import BaseModel

from or_intelligence import config, procedures, service, timeline
from or_intelligence.analysis import sanitize
from or_intelligence.models import CaseAnalysis, FrameResult
from or_intelligence.phase_estimator import OnlinePhase, PhaseEstimator
from or_intelligence.privacy import is_blank

from .main import _both, _proc_json, _seg_json, current_user

router = APIRouter(prefix="/api/live")
SAMPLES = config.ROOT / "datasets" / "samples"
UPLOAD_TMP = Path(tempfile.gettempdir()) / "mibda_live"
MAX_UPLOAD = 1024 * 1024 * 1024
JOBS: dict[str, "Job"] = {}


def _proc() -> procedures.Procedure:
    return procedures.get(procedures.DEFAULT_ID)      # the detector is trained on cholecystectomy instruments


def ready() -> bool:
    return config.WEIGHTS_PATH.exists() and importlib.util.find_spec("ultralytics") is not None


class Job:
    def __init__(self, owner: int, path: str, name: str, rate: float, conf: float):
        self.id = uuid.uuid4().hex[:12]
        self.owner, self.path, self.name, self.rate, self.conf = owner, path, name, rate, conf
        self.lock = threading.Lock()
        self.stop = threading.Event()
        self.status = "running"          # running | done | stopped | error
        self.error = ""
        self.duration = 0.0
        self.step_s = 1.0
        self.n_total = 0
        self.idx = 0
        self.frames: list[FrameResult] = []
        self.phases: list[tuple[float, int]] = []
        self.seen: set[int] = set()
        self.cur_phase: int | None = None
        self.latest: dict | None = None
        self.jpeg: bytes | None = None
        self.detector_name = ""
        self.started = time.time()
        self.seconds = 0.0
        self.saved_case: int | None = None

    # -- worker
    def run(self) -> None:
        try:
            from or_intelligence.detector import YoloDetector
            proc = _proc()
            det = YoloDetector(config.WEIGHTS_PATH, conf=self.conf)
            self.detector_name = det.name
            cap = cv2.VideoCapture(self.path)
            if not cap.isOpened():
                raise RuntimeError("The video could not be opened.")
            fps = cap.get(cv2.CAP_PROP_FPS) or 25.0
            self.n_total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
            self.duration = self.n_total / fps if self.n_total else 0.0
            skip = max(1, round(fps / self.rate))
            self.step_s = skip / fps
            est = PhaseEstimator.load(config.PHASE_MODEL_PATH) if config.PHASE_MODEL_PATH.exists() else None
            online = OnlinePhase(est, self.duration or 1.0) if est is not None else None
            idx = 0
            while not self.stop.is_set() and cap.grab():
                if idx % skip == 0:
                    ok, bgr = cap.retrieve()
                    if not ok:
                        break
                    t = idx / fps
                    boxes = [] if is_blank(bgr) else det.detect(bgr)
                    phase = None
                    if online is not None:
                        present = np.zeros(proc.n_instruments, bool)
                        for b in boxes:
                            present[b.instrument] = True
                        phase = online.update(t, present)
                    shown = sanitize(bgr)[0]
                    h, w = shown.shape[:2]
                    if w > 960:
                        shown = cv2.resize(shown, (960, int(h * 960 / w)))
                    ok2, buf = cv2.imencode(".jpg", shown, [cv2.IMWRITE_JPEG_QUALITY, 78])
                    with self.lock:
                        self.frames.append(FrameResult(t=round(t, 3), boxes=boxes))
                        if phase is not None:
                            self.phases.append((t, phase))
                            self.seen.add(phase)
                            self.cur_phase = phase
                        self.idx = idx
                        self.latest = {"t": round(t, 2), "phase": phase,
                                       "boxes": [[b.instrument, round(b.x, 4), round(b.y, 4), round(b.w, 4), round(b.h, 4), round(b.conf, 2)] for b in boxes],
                                       "seq": len(self.frames)}
                        if ok2:
                            self.jpeg = buf.tobytes()
                idx += 1
            cap.release()
            with self.lock:
                self.status = "stopped" if self.stop.is_set() else "done"
                self.seconds = time.time() - self.started
        except Exception as e:      # surfaced to the page, never a stack trace
            with self.lock:
                self.status, self.error = "error", f"{type(e).__name__}: {str(e)[:200]}"

    # -- views
    def analysis(self) -> CaseAnalysis:
        return CaseAnalysis(video_id=self.name, source="model", duration=self.duration, frames=list(self.frames),
                            detector=self.detector_name, params={"dense": True, "step_s": self.step_s})

    def phase_segments(self) -> list[timeline.PhaseSegment]:
        segs: list[timeline.PhaseSegment] = []
        for t, p in self.phases:
            if segs and segs[-1].phase == p:
                segs[-1].end = t + self.step_s
            else:
                segs.append(timeline.PhaseSegment(p, t, t + self.step_s, verified=False))
        return segs

    def snapshot(self, with_chart: bool) -> dict:
        with self.lock:
            out = {"id": self.id, "status": self.status, "error": self.error, "duration": self.duration, "n_frames": len(self.frames),
                   "progress": min(1.0, self.idx / max(self.n_total, 1)) if self.status == "running" else 1.0,
                   "latest": self.latest, "seen": sorted(self.seen), "phase": self.cur_phase, "seconds": round(self.seconds or (time.time() - self.started), 1),
                   "rate": self.rate, "name": self.name, "saved_case": self.saved_case}
            a = self.analysis() if with_chart else None
            segs = self.phase_segments() if with_chart else []
        if a is not None:
            _, _, ivs = timeline.build_intervals(a, **service.timeline_params())
            out["chart"] = {"intervals": [{"i": iv.instrument, "start": round(iv.start, 2), "end": round(iv.end, 2)} for iv in ivs],
                            "phases": [_seg_json(s) for s in segs]}
            used = {b.instrument for f in a.frames for b in f.boxes}
            out["instruments_seen"] = sorted(used)
        return out


def _job(job_id: str, user: dict) -> Job:
    j = JOBS.get(job_id)
    if j is None or (j.owner != user["id"] and user["role"] != "admin"):
        raise HTTPException(404, "analysis not found")
    return j


@router.get("/info")
def info(user: dict = Depends(current_user)) -> dict:
    proc = _proc()
    return {"ready": ready(), "procedure": _proc_json(proc), "has_phase_model": config.PHASE_MODEL_PATH.exists(),
            "samples": sorted(p.stem for p in SAMPLES.glob("*.mp4")) if SAMPLES.exists() else [],
            "retention_days": config.DEFAULT_RETENTION_DAYS}


@router.post("/upload")
async def upload(request: Request, name: str = "video.mp4", user: dict = Depends(current_user)) -> dict:
    """Raw video bytes in the request body (no multipart dependency). Returns a server-side token for /start."""
    UPLOAD_TMP.mkdir(parents=True, exist_ok=True)
    ext = Path(name).suffix.lower()
    if ext not in (".mp4", ".mov", ".avi", ".mkv"):
        raise HTTPException(415, "unsupported video type")
    token = uuid.uuid4().hex
    dest = UPLOAD_TMP / f"{token}{ext}"
    size = 0
    with dest.open("wb") as f:
        async for chunk in request.stream():
            size += len(chunk)
            if size > MAX_UPLOAD:
                f.close()
                dest.unlink(missing_ok=True)
                raise HTTPException(413, "video too large")
            f.write(chunk)
    return {"token": f"{token}{ext}", "name": Path(name).stem, "size": size}


class StartIn(BaseModel):
    token: str | None = None
    sample: str | None = None
    name: str = "video"
    rate: float = 3.0
    conf: float = 0.25


@router.post("/start")
def start(body: StartIn, user: dict = Depends(current_user)) -> dict:
    if not ready():
        raise HTTPException(503, "The detector weights or ultralytics are not available on this server.")
    if body.sample:
        path = SAMPLES / f"{Path(body.sample).name}.mp4"
        name = Path(body.sample).name
    elif body.token:
        path = UPLOAD_TMP / Path(body.token).name        # token is a file name we created; never a client path
        name = body.name
    else:
        raise HTTPException(422, "choose a video or a sample")
    if not path.is_file():
        raise HTTPException(404, "video not found")
    for j in JOBS.values():                               # one running analysis per user keeps the CPU usable
        if j.owner == user["id"] and j.status == "running":
            j.stop.set()
    rate = min(8.0, max(1.0, body.rate))
    conf = min(0.9, max(0.1, body.conf))
    job = Job(user["id"], str(path), name, rate, conf)
    JOBS[job.id] = job
    threading.Thread(target=job.run, daemon=True).start()
    return {"id": job.id}


@router.get("/{job_id}")
def poll(job_id: str, user: dict = Depends(current_user)) -> dict:
    j = _job(job_id, user)
    return j.snapshot(with_chart=True)


@router.get("/{job_id}/frame")
def frame(job_id: str, user: dict = Depends(current_user)) -> Response:
    j = _job(job_id, user)
    with j.lock:
        data = j.jpeg
    if data is None:
        raise HTTPException(404, "no frame yet")
    return Response(data, media_type="image/jpeg", headers={"Cache-Control": "no-store"})


@router.post("/{job_id}/stop")
def stop(job_id: str, user: dict = Depends(current_user)) -> dict:
    _job(job_id, user).stop.set()
    return {"ok": True}


class SaveIn(BaseModel):
    title: str
    consent: bool = False


@router.post("/{job_id}/save")
def save(job_id: str, body: SaveIn, user: dict = Depends(current_user)) -> dict:
    j = _job(job_id, user)
    if j.status not in ("done", "stopped") or not j.frames:
        raise HTTPException(409, "the analysis has not finished")
    if not (body.title.strip() and body.consent):
        raise HTTPException(422, "a title and the consent confirmation are required")
    if j.saved_case:
        return {"case_id": j.saved_case}
    cid = service.save_live_case(j.analysis(), j.path, body.title.strip()[:200], user["id"], config.DEFAULT_RETENTION_DAYS)
    j.saved_case = cid
    from or_intelligence import db
    db.log(user["id"], "live_save", cid)
    return {"case_id": cid}
