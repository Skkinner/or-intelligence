"""Live analysis: play a video and watch the instrument detector and the phase estimate work frame by frame."""
from __future__ import annotations

import importlib.util
import tempfile
import time
from pathlib import Path

import cv2
import numpy as np
import streamlit as st

from app import theme, ui
from app.ui import T
from or_intelligence import config, procedures, service, timeline
from or_intelligence.privacy import is_blank
from or_intelligence.models import CaseAnalysis, FrameResult
from or_intelligence.phase_estimator import OnlinePhase, PhaseEstimator

SAMPLES = config.ROOT / "datasets" / "samples"


def _proc() -> procedures.Procedure:
    return procedures.get(procedures.DEFAULT_ID)      # the detector is trained on cholecystectomy instruments


def _estimator() -> PhaseEstimator | None:
    return PhaseEstimator.load(config.PHASE_MODEL_PATH) if config.PHASE_MODEL_PATH.exists() else None


def _status_html(proc, t, duration, active, phase, n_done, n_total) -> str:
    chips = "".join(
        f'<span class="ori-chip" style="background:{proc.instrument_color(i)}22;color:#2A0A12;border-color:{proc.instrument_color(i)}">'
        f'{proc.instrument_names[i]}</span>' for i in sorted(active)) or f'<span class="ori-chip dim">{T("live_none_now")}</span>'
    ph = ui.phase_name(phase, proc) if phase is not None else "-"
    pct = 100 * n_done / max(n_total, 1)
    return (f'<div class="ori-now"><div class="k">{T("live_now_phase")}</div><div class="big">{ph}</div>'
            f'<div class="k">{T("live_instruments_now")}</div><div style="margin:6px 0 12px">{chips}</div>'
            f'<div class="k">{ui.fmt_time(t)} / {ui.fmt_time(duration)}</div>'
            f'<div class="ori-bar"><span style="width:{pct:.1f}%"></span></div></div>')


def _steps(proc, phase, seen: set[int]) -> None:
    items = []
    for i in range(proc.n_phases):
        state = "active" if i == phase else "done" if i in seen else "todo"
        items.append({"index": f"{i + 1}", "name": ui.phase_name(i, proc), "state": state, "time": ""})
    theme.steps(items)


def _analysis(frames: list[FrameResult], duration: float, step_s: float, name: str, det_name: str) -> CaseAnalysis:
    return CaseAnalysis(video_id=name, source="model", duration=duration, frames=list(frames), detector=det_name,
                        params={"dense": True, "step_s": step_s})


def _chart(proc, analysis: CaseAnalysis, phases_by_t: list[tuple[float, int]], duration: float, cursor: float | None):
    times, _, ivs = timeline.build_intervals(analysis, **service.timeline_params())
    segs = []
    for t, p in phases_by_t:
        if segs and segs[-1].phase == p:
            segs[-1].end = t + analysis.params["step_s"]
        else:
            segs.append(timeline.PhaseSegment(p, t, t + analysis.params["step_s"]))
    return ui.timeline_fig(ivs, segs, duration, cursor=cursor, proc=proc, height=300)


def _run(proc, path: str, name: str, rate: float, conf: float) -> None:
    from or_intelligence.detector import YoloDetector

    det = YoloDetector(config.WEIGHTS_PATH, conf=conf)
    cap = cv2.VideoCapture(path)
    if not cap.isOpened():
        st.error(T("live_cannot_open"))
        return
    fps = cap.get(cv2.CAP_PROP_FPS) or 25.0
    n_total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
    duration = n_total / fps if n_total else 0.0
    skip = max(1, round(fps / rate))
    step_s = skip / fps
    est = _estimator()
    online = OnlinePhase(est, duration or 1.0) if est is not None else None

    left, right = st.columns([3, 2])
    img_ph, status_ph = left.empty(), right.empty()
    steps_ph, chart_ph = st.empty(), st.empty()
    prog = st.progress(0.0)

    frames: list[FrameResult] = []
    phases: list[tuple[float, int]] = []
    seen: set[int] = set()
    phase = None
    idx = 0
    t0 = time.time()
    while cap.grab():
        if idx % skip == 0:
            ok, bgr = cap.retrieve()
            if not ok:
                break
            t = idx / fps
            boxes = [] if is_blank(bgr) else det.detect(bgr)
            frames.append(FrameResult(t=round(t, 3), boxes=boxes))
            active = {b.instrument for b in boxes}
            if online is not None:
                present = np.zeros(proc.n_instruments, bool)
                for b in boxes:
                    present[b.instrument] = True
                phase = online.update(t, present)
                phases.append((t, phase))
                seen.add(phase)
            img_ph.image(ui.draw_boxes(ui.bgr_to_pil(bgr), boxes, proc=proc), width="stretch")
            status_ph.markdown(_status_html(proc, t, duration, active, phase, idx, n_total), unsafe_allow_html=True)
            if online is not None:
                with steps_ph.container():
                    _steps(proc, phase, seen - {phase})
            if len(frames) % 6 == 0 or idx + skip >= n_total:
                a = _analysis(frames, duration, step_s, name, det.name)
                chart_ph.plotly_chart(_chart(proc, a, phases, duration, t), width="stretch", key=f"live_{len(frames)}")
                st.session_state["live_partial"] = (a, phases, path, rate)
            prog.progress(min(1.0, idx / max(n_total, 1)))
        idx += 1
    cap.release()
    prog.empty()
    a = _analysis(frames, duration, step_s, name, det.name)
    st.session_state["live_result"] = {"analysis": a, "phases": phases, "path": path, "seconds": time.time() - t0,
                                       "rate": rate}
    st.rerun()


def _result(proc) -> None:
    res = st.session_state["live_result"]
    a: CaseAnalysis = res["analysis"]
    n = len(a.frames)
    used = {b.instrument for f in a.frames for b in f.boxes}
    theme.kpis([(T("live_frames"), str(n), T("live_frames_hint", s=f"{res['seconds']:.0f}")),
                (T("live_instr_seen"), str(len(used)), ", ".join(proc.instrument_names[i] for i in sorted(used)) or "-"),
                (T("live_duration"), ui.fmt_time(a.duration), "")])
    st.plotly_chart(_chart(proc, a, res["phases"], a.duration, None), width="stretch", key="live_final")
    if res["phases"]:
        st.caption(T("live_phase_note"))
    user = ui.current_user()
    with st.form("live_save"):
        title = st.text_input(T("title"), value=Path(res["path"]).stem)
        consent = st.checkbox(T("consent_text"))
        if st.form_submit_button(T("live_save"), type="primary"):
            if not (title.strip() and consent):
                st.error(T("live_need_consent"))
            else:
                cid = service.save_live_case(a, res["path"], title.strip(), user["id"], config.DEFAULT_RETENTION_DAYS)
                st.success(T("live_saved", id=cid))


def render() -> None:
    proc = _proc()
    theme.hero(T("live_title"), T("live_sub"))
    ready = config.WEIGHTS_PATH.exists() and importlib.util.find_spec("ultralytics") is not None
    if not ready:
        st.warning(T("live_need_weights"))
        return

    samples = sorted(SAMPLES.glob("*.mp4")) if SAMPLES.exists() else []
    up = st.file_uploader(T("video_file"), type=["mp4", "mov", "avi", "mkv"])
    pick = st.selectbox(T("live_sample"), [None] + samples, format_func=lambda p: "-" if p is None else p.stem) if samples else None
    c1, c2 = st.columns(2)
    rate = c1.slider(T("live_rate"), 1.0, 8.0, 3.0, 0.5)
    conf = c2.slider(T("live_conf"), 0.1, 0.9, 0.25, 0.05)
    if st.button(T("live_start"), type="primary", disabled=not (up or pick)):
        st.session_state.pop("live_result", None)
        if up:
            tmp = Path(tempfile.gettempdir()) / f"mibda_live_{up.name}"
            tmp.write_bytes(up.getvalue())
            path, name = str(tmp), Path(up.name).stem
        else:
            path, name = str(pick), pick.stem
        _run(proc, path, name, rate, conf)
    elif "live_result" in st.session_state:
        _result(proc)
