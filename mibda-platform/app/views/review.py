"""Case review: timeline, viewer, phases, usage, notes, exports and the AI tools."""
from __future__ import annotations

import importlib.util
import tempfile
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from app import ui
from app.views import case_ai
from app.ui import T
from or_intelligence import auth, config, db, report, service, timeline
from or_intelligence.analysis import read_video_frame
from or_intelligence.constants import TARGETS, VERBS, VERB_AR
from or_intelligence.insights import review_flags


def _jump(tkey: str, snap: list[float], t: float) -> None:
    st.session_state[tkey] = min(snap, key=lambda x: abs(x - t)) if snap else t


def render() -> None:
    user = ui.current_user()
    cases = db.list_cases(user)
    if not cases:
        st.info(T("no_cases"))
        return
    ids = [c["id"] for c in cases]
    titles = {c["id"]: f'#{c["id"]} · {c["title"]}' for c in cases}
    if st.session_state.get("case_id") not in ids:
        st.session_state["case_id"] = ids[0]
    case_id = st.selectbox(T("case"), ids, key="case_id", format_func=lambda i: titles[i])
    case = db.get_case(case_id)
    if case is None or not db.can_view(user, case):
        st.error(T("not_allowed"))
        return
    if st.session_state.get("_viewed") != case_id:
        st.session_state["_viewed"] = case_id
        db.log(user["id"], "view_case", case_id)

    a = ui.load_case_analysis(case)
    p = ui.params()
    times, _, intervals = timeline.build_intervals(a, **service.timeline_params(p))
    proc = ui.proc_of_case(case)
    n_i = proc.n_instruments
    usage = timeline.usage_stats(intervals, a.duration, proc)
    metrics = timeline.case_metrics(intervals, a.duration)
    phases = timeline.phase_segments(a)
    flags = review_flags(intervals, a.duration, times, dense=a.dense, long_use_s=p["long_use_s"],
                         switch_window_s=p["switch_window_s"], switch_count=int(p["switch_count"]),
                         idle_gap_s=p["idle_gap_s"], instrument_names=proc.instrument_names)
    is_frames = case["media_kind"] == "frames"

    # ---- header
    st.subheader(case["title"])
    st.markdown(ui.source_badge(case["source"]), unsafe_allow_html=True)
    if not a.dense:
        st.caption(T("sparse_notice"))
    st.caption(proc.label(ui.lang()))
    if n_i:
        c1, c2, c3, c4 = st.columns(4)
        c1.metric(T("duration"), ui.fmt_time(a.duration))
        c2.metric(T("entries"), metrics["instrument_entries"])
        c3.metric(T("per_min"), metrics["entries_per_min"])
        c4.metric(T("instruments_used"), metrics["instruments_used"])
        sel = st.multiselect(T("instruments"), list(range(n_i)), default=list(range(n_i)),
                             format_func=lambda i: ui.inst(i, proc), key=f"only_{case_id}")
        only = set(sel) if len(sel) < n_i else None
    else:
        c1, c2 = st.columns(2)
        c1.metric(T("duration"), ui.fmt_time(a.duration))
        c2.metric(T("kpi_phased"), len({s.phase for s in phases}))
        only = None

    # ---- time state
    if is_frames:
        snap = sorted({f.t for f in a.frames})
    else:
        step = max(1, int(a.duration // 2000))
        snap = list(range(0, int(a.duration) + 1, step))
    tkey = f"t_{case_id}"
    if "pending_t" in st.session_state:
        _jump(tkey, snap, float(st.session_state.pop("pending_t")))
    if tkey not in st.session_state and snap:
        st.session_state[tkey] = snap[0]
    t = st.session_state.get(tkey, 0)

    # ---- timeline (click a row to jump)
    ckey = f"tl_{case_id}"
    st.caption(T("timeline_hint"))
    st.plotly_chart(ui.timeline_fig(intervals, phases, a.duration, cursor=t, only=only, proc=proc), key=ckey,
                    on_select="rerun", selection_mode=["points", "box"], width="stretch")
    picked = ui.click_time(ckey)
    if picked is not None and st.session_state.get(f"{ckey}_last") != picked:
        st.session_state[f"{ckey}_last"] = picked
        _jump(tkey, snap, picked)
        st.rerun()  # redraw the cursor at the new position

    if snap:
        st.select_slider(T("time"), options=snap, key=tkey, format_func=ui.fmt_time)
        t = st.session_state[tkey]

    # ---- viewer
    f = timeline.frame_at(a, t)
    left, right = st.columns([3, 2])
    with left:
        if is_frames and f is not None:
            img_path = Path(case["media_path"]) / (f.image or "")
            if img_path.is_file():
                st.image(ui.draw_boxes(ui.load_image(str(img_path)), f.boxes, only, proc=proc),
                         caption=f"{ui.fmt_time(f.t)}", width="stretch")
            else:
                st.warning(T("frame_missing"))
        elif not is_frames:
            vp = Path(case["media_path"])
            if vp.is_file():
                st.video(str(vp), start_time=int(t))
                frame = read_video_frame(vp, t, privacy=bool(p.get("privacy", True)))
                if frame is not None and f is not None:
                    st.image(ui.draw_boxes(ui.bgr_to_pil(frame), f.boxes, only, proc=proc), caption=f"{ui.fmt_time(t)}", width="stretch")
            else:
                st.warning(T("video_missing"))
    with right:
        st.markdown(f"**{T('now')}: {ui.fmt_time(t)}**")
        cur = timeline.phase_at(phases, t)
        if cur is not None:
            st.write(f"{T('phase')}: {ui.phase_name(cur.phase, proc)}")
            if not cur.verified:
                st.caption(ui.phase_status(cur))
        present = sorted({b.instrument for b in (f.boxes if f else []) if b.instrument < n_i})
        if n_i:
            st.write(f"{T('visible_now')}: " + (", ".join(ui.inst(i, proc) for i in present) if present else "-"))
        trip = [b for b in (f.boxes if f else []) if b.triplet is not None and b.verb is not None]
        if trip and case["source"] == "annotations":
            st.caption(T("actions_annotated"))
            rows = [{T("instrument"): ui.inst(b.instrument, proc),
                     T("verb"): (VERB_AR[VERBS[b.verb]] if ui.lang() == "ar" else VERBS[b.verb]),
                     T("target"): TARGETS[b.target].replace("_", " ")} for b in trip]
            st.dataframe(pd.DataFrame(rows), hide_index=True, width="stretch")

    # ---- phases: each row jumps to its start; the one playing now is highlighted
    st.markdown(f"### {T('phases_title')}")
    if not phases:
        st.caption(T("phases_none"))
    else:
        if any(not x.verified for x in phases):
            st.warning(T("phases_estimated_warning"))
            if not a.params.get("complete_operation"):
                st.caption(T("phases_excerpt_note"))
        st.caption(T("phases_hint"))
        for i, ph in enumerate(phases):
            cols = st.columns([4, 2.4, 1.2, 3, 1])
            nm = ui.phase_name(ph.phase, proc)
            cols[0].markdown(f":violet-background[**▶ {nm}** · {T('phase_playing')}]" if ph is cur else nm)
            cols[1].write(f"`{ui.fmt_time(ph.start)} - {ui.fmt_time(ph.end)}`")
            cols[2].write(ui.fmt_time(ph.end - ph.start))
            cols[3].caption(ui.phase_status(ph))
            cols[4].button(T("go"), key=f"phase_go_{case_id}_{i}", on_click=_jump, args=(tkey, snap, ph.start))

    tabs = st.tabs([T("tab_usage"), T("tab_notes"), T("tab_export"),
                    "🤖 " + T("tab_report"), "📚 " + T("tab_resources"), "💬 " + T("tab_assistant")])
    ai_ctx = case_ai.Ctx(case, a, proc, usage, phases, flags, metrics, user, tkey)

    # ---- usage
    with tabs[0]:
        if not n_i:
            st.info(T("no_instrument_labels"))
        else:
            fig = go.Figure(go.Bar(
                x=[ui.inst(i, proc) for i in range(n_i)], y=usage["active_seconds"],
                marker_color=[proc.instrument_color(i) for i in range(n_i)]))
            fig.update_layout(height=280, margin=dict(l=10, r=10, t=10, b=10), yaxis_title=T("active_seconds"))
            st.plotly_chart(fig, width="stretch")
            show = usage.copy()
            show["instrument"] = [ui.inst(i, proc) for i in range(n_i)]
            show["first_use"] = show["first_use"].map(lambda v: ui.fmt_time(v) if pd.notna(v) else "-")
            show["last_use"] = show["last_use"].map(lambda v: ui.fmt_time(v) if pd.notna(v) else "-")
            show.columns = [T("instrument"), T("active_seconds"), T("pct_of_case"), T("segments"),
                            T("first_use"), T("last_use"), T("longest")]
            st.dataframe(show, hide_index=True, width="stretch")

    # ---- notes
    with tabs[1]:
        with st.form(f"note_form_{case_id}", clear_on_submit=True):
            txt = st.text_area(T("note_at", t=ui.fmt_time(t)), height=90)
            if st.form_submit_button(T("add_note")) and txt.strip():
                db.add_note(case_id, user["id"], float(t), txt)
                db.log(user["id"], "add_note", case_id)
                st.rerun()
        for n in db.list_notes(case_id):
            cols = st.columns([1, 6, 1, 1])
            cols[0].write(f"`{ui.fmt_time(n['t_seconds'])}`")
            cols[1].write(f"**{n['display_name']}**: {n['text']}")
            cols[2].button(T("go"), key=f"note_go_{n['id']}", on_click=_jump, args=(tkey, snap, n["t_seconds"]))
            if user["role"] == "admin" or n["author_id"] == user["id"]:
                if cols[3].button("✕", key=f"note_del_{n['id']}"):
                    db.delete_note(n["id"], user)
                    st.rerun()

    # ---- export / manage
    with tabs[2]:
        pkey = f"pdf_{case_id}_{ui.lang()}"
        if st.button(T("make_pdf"), key=f"mk_{case_id}"):
            with tempfile.TemporaryDirectory() as d:
                out = Path(d) / "report.pdf"
                used = report.build_report(
                    out, case=dict(case), duration=a.duration, intervals=intervals, usage_df=usage, phases=phases,
                    flags=flags, notes=db.list_notes(case_id), clips=db.list_clips(case_id), metrics=metrics,
                    dense=a.dense, lang=ui.lang(), proc=proc)
                st.session_state[pkey] = (out.read_bytes(), used)
            db.log(user["id"], "export_pdf", case_id)
        if pkey in st.session_state:
            data, used = st.session_state[pkey]
            if used != ui.lang():
                st.warning(T("pdf_lang_fallback"))
            st.download_button(T("download_pdf"), data, file_name=f"case{case_id}_report.pdf", mime="application/pdf")

        st.divider()
        weights_ok = config.WEIGHTS_PATH.exists() and importlib.util.find_spec("ultralytics") is not None
        can_manage = user["role"] in ("admin", "instructor") or user["id"] == case["owner_id"]
        if can_manage and weights_ok:
            if st.button(T("run_model"), key=f"run_{case_id}"):
                from or_intelligence.detector import YoloDetector
                bar = st.progress(0.0)
                service.run_model_on_case(case_id, YoloDetector(config.WEIGHTS_PATH, conf=p["conf"]),
                                          step_s=p["sample_step_s"], progress=bar.progress)
                db.log(user["id"], "run_model", case_id)
                st.rerun()
        elif can_manage:
            st.caption(T("no_weights_hint"))

        if user["role"] in ("admin", "instructor"):
            with st.form(f"meta_{case_id}"):
                new_tags = st.text_input(T("tags"), value=case["tags"])
                trainees = [u for u in auth.list_users() if u["role"] == "trainee"]
                ids = [None] + [u["id"] for u in trainees]
                names = {None: "-", **{u["id"]: u["display_name"] for u in trainees}}
                cur = ids.index(case["trainee_id"]) if case["trainee_id"] in ids else 0
                new_tr = st.selectbox(T("trainee"), ids, index=cur, format_func=lambda i: names[i])
                if st.form_submit_button(T("save")):
                    db.update_case(case_id, tags=new_tags, trainee_id=new_tr)
                    db.log(user["id"], "edit_case", case_id)
                    st.rerun()

        if user["role"] == "admin" or user["id"] == case["owner_id"]:
            with st.expander(T("danger_zone")):
                ok = st.checkbox(T("confirm_delete"), key=f"cd_{case_id}")
                if st.button(T("delete_case"), key=f"del_{case_id}", disabled=not ok):
                    db.log(user["id"], "delete_case", case_id, case["title"])
                    db.delete_case(case_id)
                    st.session_state.pop("case_id", None)
                    st.rerun()

    with tabs[3]:
        case_ai.report_tab(ai_ctx)
    with tabs[4]:
        case_ai.resources_tab(ai_ctx)
    with tabs[5]:
        case_ai.assistant_tab(ai_ctx)
