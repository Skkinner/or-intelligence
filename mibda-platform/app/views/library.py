"""Searchable case library, plus cross-case moment search ("show me every clipping segment")."""
from __future__ import annotations

import json

import pandas as pd
import streamlit as st

from app import ui
from app.ui import T
from or_intelligence import auth, db, procedures, service, timeline
from or_intelligence.constants import INSTRUMENTS, N_INSTRUMENTS


def _open(case_id: int, t: float | None = None) -> None:
    st.session_state["case_id"] = case_id
    if t is not None:
        st.session_state["pending_t"] = t
    st.switch_page(st.session_state["_pages"]["review"])


def render() -> None:
    user = ui.current_user()
    cases = db.list_cases(user)
    if not cases:
        st.info(T("no_cases_start"))
        return
    users = {u["id"]: u["display_name"] for u in auth.list_users()}

    f1, f2, f3 = st.columns([3, 3, 2])
    q = f1.text_input(T("search"), placeholder=T("search_hint")).strip().lower()
    need = f2.multiselect(T("has_instruments"), list(range(N_INSTRUMENTS)), format_func=ui.inst)
    src = f3.selectbox(T("source"), ["all", "annotations", "model"],
                       format_func=lambda s: {"all": T("all"), "annotations": T("src_annotations_short"), "model": T("src_model")}[s])

    rows = []
    for c in cases:
        stats = json.loads(c["stats_json"] or "{}")
        usage = stats.get("usage", {})
        hay = f'{c["title"]} {c["tags"]} {c["video_id"] or ""}'.lower()
        if q and q not in hay:
            continue
        if any(usage.get(INSTRUMENTS[i], 0) <= 0 for i in need):
            continue
        if src != "all" and c["source"] != src:
            continue
        rows.append({
            "id": c["id"], T("title"): c["title"], T("duration"): ui.fmt_time(c["duration"]),
            T("source"): T("src_model") if c["source"] == "model" else T("src_annotations_short"),
            T("trainee"): users.get(c["trainee_id"], "-"), T("tags"): c["tags"],
            T("instruments_used"): str(stats.get("instruments_used", "-")),
        })
    st.caption(T("n_results", n=len(rows)))
    view = st.radio(T("view"), ["cards", "table"], horizontal=True, label_visibility="collapsed",
                    format_func=lambda v: T("view_cards") if v == "cards" else T("view_table"))
    by_id = {c["id"]: c for c in cases}
    if view == "cards":
        grid = st.columns(3)
        for k, r in enumerate(rows):
            with grid[k % 3]:
                st.markdown(ui.case_card_html(by_id[r["id"]]), unsafe_allow_html=True)
                st.button(T("open_case"), key=f"card_open_{r['id']}", on_click=_open, args=(r["id"],), width="stretch")
    else:
        df = pd.DataFrame(rows)
        ev = st.dataframe(df, hide_index=True, width="stretch", on_select="rerun", selection_mode="single-row", key="lib_table")
        picked = ev.selection.rows if ev is not None else []
        if picked and rows:
            cid = rows[picked[0]]["id"]
            st.button(T("open_case") + f" #{cid}", type="primary", on_click=_open, args=(cid,))

    has_inst = any(procedures.resolve(c['procedure']).n_instruments for c in cases)
    if not has_inst:
        return
    st.divider()
    st.markdown(f"### {T('moment_search')}")
    st.caption(T("moment_hint"))
    inst_i = st.selectbox(T("instrument"), list(range(N_INSTRUMENTS)), format_func=ui.inst, key="moment_inst")
    p = ui.params()
    hits = []
    for c in cases:
        a = ui.load_case_analysis(c)
        _, _, ivs = timeline.build_intervals(a, **service.timeline_params(p))
        for iv in ivs:
            if iv.instrument == inst_i:
                hits.append((c, iv))
    if not hits:
        st.write(T("none"))
    for k, (c, iv) in enumerate(hits[:60]):
        cols = st.columns([4, 2, 2, 1])
        cols[0].write(f'#{c["id"]} · {c["title"]}')
        cols[1].write(f"{ui.fmt_time(iv.start)} - {ui.fmt_time(iv.end)}")
        cols[2].write(ui.fmt_time(iv.duration))
        cols[3].button(T("go"), key=f"hit_{k}", on_click=_open, args=(c["id"], iv.start))
    if len(hits) > 60:
        st.caption(T("showing_first", n=60))
