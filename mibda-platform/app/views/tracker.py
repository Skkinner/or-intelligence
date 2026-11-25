"""Operation tracker: where the operation is, phase by phase, with live playback."""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from app import theme, ui
from app.ui import T
from or_intelligence import config, db, procedures, service, timeline
from or_intelligence.constants import TARGETS, VERBS, VERB_AR
from or_intelligence.phase_estimator import PhaseEstimator


@st.cache_resource(show_spinner=False)
def _estimator() -> PhaseEstimator | None:
    return PhaseEstimator.load(config.PHASE_MODEL_PATH) if config.PHASE_MODEL_PATH.exists() else None


def _estimator_for(proc: procedures.Procedure) -> PhaseEstimator | None:
    """The bundled estimator was trained on cholecystectomy only."""
    return _estimator() if proc.id == procedures.DEFAULT_ID else None


def _phased(case, mode: str, conf: float):
    a = ui.load_case_analysis(case)
    if mode == "annotation":
        return a if any(f.phase is not None for f in a.frames) else None
    est = _estimator_for(ui.proc_of_case(case))
    return est.apply(a, conf=conf, complete=(a.source == "annotations")) if est else None


def _durations(segs, n: int) -> np.ndarray:
    d = np.zeros(n)
    for s in segs:
        if s.phase < n:
            d[s.phase] += max(0.0, s.end - s.start)
    return d


def _elapsed_by_phase(segs, pos: float, n: int) -> np.ndarray:
    d = np.zeros(n)
    for s in segs:
        if s.phase < n:
            d[s.phase] += max(0.0, min(s.end, pos) - s.start)
    return d


def _toggle_play() -> None:
    st.session_state["trk_play"] = not st.session_state.get("trk_play", False)


def _restart(pkey: str, first: float) -> None:
    st.session_state[pkey] = first
    st.session_state["trk_play"] = False


def _scrub(pkey: str, key: str) -> None:
    st.session_state[pkey] = st.session_state[key]


def render() -> None:
    user = ui.current_user()
    cases = db.list_cases(user)
    if not cases:
        st.info(T("no_cases"))
        return
    ids = [c["id"] for c in cases]
    names = {c["id"]: f'#{c["id"]} · {c["title"]}' for c in cases}
    if st.session_state.get("case_id") not in ids:
        st.session_state["case_id"] = ids[0]
    case_id = st.selectbox(T("case"), ids, key="case_id", format_func=lambda i: names[i])
    case = db.get_case(case_id)
    if case is None or not db.can_view(user, case):
        st.error(T("not_allowed"))
        return

    p = ui.params()
    proc = ui.proc_of_case(case)
    nph = proc.n_phases
    a = ui.load_case_analysis(case)
    has_ann = any(f.phase is not None for f in a.frames)
    est = _estimator_for(proc)
    modes = (["annotation"] if has_ann else []) + (["estimated"] if est else [])
    if not modes:
        st.warning(T("no_phase_source"))
        return
    mode = st.radio(T("phase_source"), modes, horizontal=True, key=f"trk_mode_{case_id}",
                    format_func=lambda m: T("ps_annotation") if m == "annotation" else T("ps_estimated"))
    ap = _phased(case, mode, p["conf"])
    segs = timeline.phase_segments(ap)
    if not segs:
        st.warning(T("no_phase_source"))
        return
    times, m_raw, ivs = timeline.build_intervals(ap, **service.timeline_params(p))
    frames = sorted(ap.frames, key=lambda f: f.t)
    snap = [f.t for f in frames]
    is_frames = case["media_kind"] == "frames"

    est_acc = None
    if config.PHASE_METRICS_PATH.exists():
        est_acc = json.loads(config.PHASE_METRICS_PATH.read_text(encoding="utf-8")).get("clean", {}).get("mean_accuracy")

    chips = [theme.chip(proc.label(ui.lang()), "ok"),
             theme.chip(T("src_model") if case["source"] == "model" else T("src_annotations_short"),
                        "" if case["source"] == "model" else "warn"),
             theme.chip(T("ps_annotation") if mode == "annotation" else T("ps_estimated"),
                        "dim" if mode == "annotation" else "warn")]
    theme.hero(case["title"], T("tracker_sub"), chips)
    if mode == "estimated":
        st.caption(T("estimator_note", acc=f"{100 * est_acc:.0f}" if est_acc else "?"))

    # ---- playback controls
    pkey = f"trk_pos_{case_id}"
    st.session_state.setdefault(pkey, snap[0])
    st.session_state.setdefault("trk_speed", 30)
    playing = st.session_state.get("trk_play", False)
    c1, c2, c3 = st.columns([1, 1, 3])
    c1.button(T("pause") if playing else T("play"), on_click=_toggle_play, type="primary", width="stretch")
    c2.button(T("restart"), on_click=_restart, args=(pkey, snap[0]), width="stretch")
    c3.select_slider(T("speed"), [1, 10, 30, 60, 120], key="trk_speed", format_func=lambda s: f"{s}x")
    if not playing:
        sk = f"trk_scrub_{case_id}_{int(st.session_state[pkey])}"
        st.select_slider(T("time"), options=snap, value=min(snap, key=lambda x: abs(x - st.session_state[pkey])),
                         key=sk, format_func=ui.fmt_time, on_change=_scrub, args=(pkey, sk))

    # ---- the live part (re-runs every second while playing)
    def live() -> None:
        pos = st.session_state[pkey]
        if st.session_state.get("trk_play"):
            pos = min(snap[-1], pos + st.session_state["trk_speed"])
            st.session_state[pkey] = pos
            if pos >= snap[-1]:
                st.session_state["trk_play"] = False
                st.rerun(scope="app")
        f = timeline.frame_at(ap, pos)
        cur = f.phase if f is not None else None
        elapsed = _elapsed_by_phase(segs, pos, nph)
        items = []
        for i in range(nph):
            seg_i = [s for s in segs if s.phase == i]
            finished = bool(seg_i) and all(s.end <= pos for s in seg_i)
            state = "active" if i == cur else "done" if finished else "todo"
            items.append({"index": f"{i + 1}", "name": ui.phase_name(i, proc), "state": state,
                          "time": ui.fmt_time(elapsed[i]) if elapsed[i] > 0 else "-"})
        theme.steps(items)

        left, right = st.columns([3, 2])
        with left:
            if is_frames and f is not None:
                path = Path(case["media_path"]) / (f.image or "")
                if path.is_file():
                    st.image(ui.draw_boxes(ui.load_image(str(path)), f.boxes, proc=proc), width="stretch")
            elif not is_frames:
                from or_intelligence.analysis import read_video_frame
                frame = read_video_frame(case["media_path"], pos, privacy=bool(p.get("privacy", True)))
                if frame is not None and f is not None:
                    st.image(ui.draw_boxes(ui.bgr_to_pil(frame), f.boxes, proc=proc), width="stretch")
        with right:
            pct = 100 * pos / ap.duration if ap.duration else 0
            active = sorted({b.instrument for b in (f.boxes if f else []) if b.instrument < proc.n_instruments})
            chips_now = "".join(
                f'<span class="ori-chip" style="background:{proc.instrument_color(i)}22;'
                f'color:{proc.instrument_color(i)};border-color:{proc.instrument_color(i)}66">{ui.inst(i, proc)}</span>'
                for i in active) or '<span class="ori-chip dim">-</span>'
            instr_html = f'<div class="k">{T("visible_now")}</div><div>{chips_now}</div>' if proc.n_instruments else ""
            st.markdown(
                f'<div class="ori-now"><div class="k">{T("current_phase")}</div>'
                f'<div class="big">{ui.phase_name(cur, proc)}</div>'
                f'<div class="k">{T("elapsed")} / {T("case_progress")}</div>'
                f'<div><b>{ui.fmt_time(pos)}</b> / {ui.fmt_time(ap.duration)} · {pct:.0f}%</div>'
                f'<div class="ori-bar"><span style="width:{pct:.1f}%"></span></div>{instr_html}</div>',
                unsafe_allow_html=True)
            trip = [b for b in (f.boxes if f else []) if b.triplet is not None and b.verb is not None]
            if trip and case["source"] == "annotations":
                st.caption(T("actions_annotated"))
                for b in trip:
                    verb = VERB_AR[VERBS[b.verb]] if ui.lang() == "ar" else VERBS[b.verb]
                    st.write(f"{ui.inst(b.instrument, proc)} · {verb} · {TARGETS[b.target].replace('_', ' ')}")

        # phase strip with playhead
        fig = go.Figure()
        for s in segs:
            fig.add_trace(go.Bar(base=[s.start], x=[max(1.0, s.end - s.start)], y=[""], orientation="h",
                                 marker_color=proc.phase_color(s.phase), showlegend=False,
                                 hovertemplate=f"{ui.phase_name(s.phase, proc)}<br>{ui.fmt_time(s.start)} - {ui.fmt_time(s.end)}<extra></extra>"))
        fig.add_shape(type="line", x0=pos, x1=pos, y0=0, y1=1, yref="paper", line=dict(color="#111", width=3))
        tk = np.linspace(0, ap.duration, 7)
        fig.update_layout(barmode="overlay", height=90, margin=dict(l=0, r=0, t=4, b=24),
                          xaxis=dict(range=[0, ap.duration], tickvals=list(tk), ticktext=[ui.fmt_time(t) for t in tk]),
                          yaxis=dict(visible=False))
        st.plotly_chart(fig, width="stretch", key="trk_strip", config={"displayModeBar": False})

    frag = st.fragment(run_every=1.0)(live) if playing else st.fragment(live)
    frag()

    # ---- analytics (static)
    st.divider()
    dur = _durations(segs, nph)
    ref_rows = []
    for c in cases:
        if ui.proc_of_case(c).id != proc.id:          # only compare like with like
            continue
        other = _phased(c, "annotation", p["conf"]) or _phased(c, "estimated", p["conf"])
        if other is not None:
            ref_rows.append(_durations(timeline.phase_segments(other), nph))
    pn = [ui.phase_name(i, proc) for i in range(nph)]
    a1, a2 = st.columns(2) if proc.n_instruments else (st.container(), None)
    with a1:
        st.markdown(f"**{T('time_per_phase')}**")
        fig = go.Figure()
        fig.add_trace(go.Bar(name=T("this_case"), x=pn, y=dur / 60, marker_color="#5C061C"))
        if len(ref_rows) >= 3:
            fig.add_trace(go.Bar(name=T("library_median", n=len(ref_rows)), x=pn, y=np.median(ref_rows, axis=0) / 60,
                                 marker_color="#cdd8d6"))
        fig.update_layout(barmode="group", height=300, margin=dict(l=0, r=0, t=10, b=0), yaxis_title=T("minutes"),
                          legend=dict(orientation="h", y=1.12))
        st.plotly_chart(fig, width="stretch", key="trk_tpp")
        if len(ref_rows) < 3:
            st.caption(T("reference_needs_cases"))
    if a2 is not None:
        with a2:
            st.markdown(f"**{T('tool_phase_heatmap')}**")
            phase_of = np.array([f.phase if f.phase is not None else -1 for f in frames])
            mat = np.zeros((proc.n_instruments, nph))
            for ph in range(nph):
                sel = phase_of == ph
                if sel.any():
                    mat[:, ph] = m_raw[sel].mean(axis=0) * 100
            fig = go.Figure(go.Heatmap(z=mat, x=[f"{i + 1}" for i in range(nph)], y=[ui.inst(i, proc) for i in range(proc.n_instruments)],
                                       colorscale="Teal", zmin=0, zmax=100, text=np.round(mat).astype(int), texttemplate="%{text}",
                                       hovertemplate="%{y} · %{x}: %{z:.0f}%<extra></extra>", showscale=False))
            fig.update_layout(height=300, margin=dict(l=0, r=0, t=10, b=0), yaxis=dict(autorange="reversed"),
                              xaxis_title=T("phase_number"))
            st.plotly_chart(fig, width="stretch", key="trk_heat")
            st.caption(T("heatmap_hint"))

    rows = []
    snap_arr = np.array(snap)
    for s in segs:
        sel = (snap_arr >= s.start) & (snap_arr < s.end)
        row = {T("phase"): ui.phase_name(s.phase, proc), T("start"): ui.fmt_time(s.start), T("end"): ui.fmt_time(s.end),
               T("duration"): ui.fmt_time(s.end - s.start)}
        if proc.n_instruments:
            top = np.argsort(-m_raw[sel].mean(axis=0))[:2] if sel.any() else []
            row[T("main_instruments")] = ", ".join(ui.inst(int(i), proc) for i in top if m_raw[sel][:, i].any())
        rows.append(row)
    st.dataframe(pd.DataFrame(rows), hide_index=True, width="stretch")
