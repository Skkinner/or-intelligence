"""Side-by-side comparison of two cases of the same procedure."""
from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from app import ui
from app.ui import T
from or_intelligence import db, service, timeline


def _prep(case, proc):
    a = ui.load_case_analysis(case)
    _, _, ivs = timeline.build_intervals(a, **service.timeline_params(ui.params()))
    return a, ivs, timeline.usage_stats(ivs, a.duration, proc), timeline.case_metrics(ivs, a.duration), timeline.phase_segments(a)


def render() -> None:
    cases = db.list_cases(ui.current_user())
    if len(cases) < 2:
        st.info(T("need_two_cases"))
        return
    ids = [c["id"] for c in cases]
    by_id = {c["id"]: c for c in cases}
    names = {c["id"]: f'#{c["id"]} · {c["title"]}' for c in cases}
    c1, c2 = st.columns(2)
    ia = c1.selectbox(T("case_a"), ids, format_func=lambda i: names[i], key="cmp_a")
    proc = ui.proc_of_case(by_id[ia])
    same = [i for i in ids if i != ia and ui.proc_of_case(by_id[i]).id == proc.id]   # compare like with like
    if not same:
        c2.info(T("no_same_procedure"))
        return
    ib = c2.selectbox(T("case_b"), same, format_func=lambda i: names[i], key="cmp_b")
    A, B = _prep(by_id[ia], proc), _prep(by_id[ib], proc)
    n_i = proc.n_instruments

    if n_i:
        labels = [ui.inst(i, proc) for i in range(n_i)]
        fig = go.Figure([
            go.Bar(name=f"#{ia}", x=labels, y=A[2]["pct_of_case"], marker_color="#5C061C"),
            go.Bar(name=f"#{ib}", x=labels, y=B[2]["pct_of_case"], marker_color="#F59E6B"),
        ])
        fig.update_layout(barmode="group", height=300, margin=dict(l=10, r=10, t=30, b=10), yaxis_title=T("pct_of_case"))
        st.plotly_chart(fig, width="stretch")

    rows = [(T("duration"), ui.fmt_time(A[0].duration), ui.fmt_time(B[0].duration))]
    if n_i:
        rows += [(T("entries"), A[3]["instrument_entries"], B[3]["instrument_entries"]),
                 (T("per_min"), A[3]["entries_per_min"], B[3]["entries_per_min"]),
                 (T("instruments_used"), A[3]["instruments_used"], B[3]["instruments_used"])]
    rows.append((T("source"), A[0].source, B[0].source))
    rows = [(m, str(x), str(y)) for m, x, y in rows]       # mixed text/numbers: keep the table Arrow-safe
    st.dataframe(pd.DataFrame(rows, columns=[T("metric"), f"#{ia}", f"#{ib}"]), hide_index=True, width="stretch")

    if A[4] and B[4]:
        st.markdown(f"**{T('phase_share')}**")
        fig = go.Figure()
        for p in range(proc.n_phases):
            vals = []
            for X in (A, B):
                ps = timeline.phase_stats(X[4])
                row = ps[ps["phase"] == p]
                vals.append(float(row["pct"].iloc[0]) if len(row) else 0.0)
            fig.add_trace(go.Bar(name=ui.phase_name(p, proc), y=[f"#{ia}", f"#{ib}"], x=vals, orientation="h",
                                 marker_color=proc.phase_color(p)))
        fig.update_layout(barmode="stack", height=220, margin=dict(l=10, r=10, t=10, b=10), xaxis_title="%")
        st.plotly_chart(fig, width="stretch")

    st.markdown(f"**{T('timeline')} #{ia}**")
    st.plotly_chart(ui.timeline_fig(A[1], A[4], A[0].duration, proc=proc), width="stretch", key="cmp_tl_a")
    st.markdown(f"**{T('timeline')} #{ib}**")
    st.plotly_chart(ui.timeline_fig(B[1], B[4], B[0].duration, proc=proc), width="stretch", key="cmp_tl_b")
    if not (A[0].dense and B[0].dense):
        st.caption(T("sparse_notice"))
