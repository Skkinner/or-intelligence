"""Per-trainee progress over cases (descriptive statistics, never a skill score)."""
from __future__ import annotations

import json

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from app import ui
from app.ui import T
from or_intelligence import auth, db
from or_intelligence.constants import INSTRUMENT_COLORS, INSTRUMENTS, N_INSTRUMENTS


def render() -> None:
    user = ui.current_user()
    if user["role"] == "trainee":
        tid = user["id"]
    else:
        trainees = [u for u in auth.list_users() if u["role"] == "trainee"]
        if not trainees:
            st.info(T("no_trainees"))
            return
        names = {u["id"]: u["display_name"] for u in trainees}
        tid = st.selectbox(T("trainee"), list(names), format_func=lambda i: names[i])

    cases = sorted((c for c in db.list_cases(user) if c["trainee_id"] == tid), key=lambda c: c["created_at"])
    if not cases:
        st.info(T("no_trainee_cases"))
        return
    st.caption(T("progress_disclaimer"))
    rows = []
    for c in cases:
        s = json.loads(c["stats_json"] or "{}")
        usage = s.get("usage", {})
        dur = c["duration"] or 1.0
        row = {"id": c["id"], T("title"): c["title"], T("duration"): round(dur / 60, 1),
               T("per_min"): s.get("entries_per_min", 0), T("source"): c["source"]}
        for n in INSTRUMENTS:
            row[n] = round(100 * float(usage.get(n, 0)) / dur, 1)
        rows.append(row)
    df = pd.DataFrame(rows)
    labels = [f'#{r["id"]}' for r in rows]

    fig = go.Figure(go.Scatter(x=labels, y=df[T("per_min")], mode="lines+markers", line=dict(color="#5C061C")))
    fig.update_layout(height=260, margin=dict(l=10, r=10, t=10, b=10), yaxis_title=T("per_min"))
    st.markdown(f"**{T('entries_trend')}**")
    st.plotly_chart(fig, width="stretch")

    fig = go.Figure([go.Bar(name=ui.inst(i), x=labels, y=df[INSTRUMENTS[i]], marker_color=INSTRUMENT_COLORS[INSTRUMENTS[i]])
                     for i in range(N_INSTRUMENTS)])
    fig.update_layout(barmode="stack", height=300, margin=dict(l=10, r=10, t=10, b=10), yaxis_title=T("pct_of_case"))
    st.markdown(f"**{T('usage_mix')}**")
    st.plotly_chart(fig, width="stretch")

    st.dataframe(df.rename(columns={n: ui.inst(i) for i, n in enumerate(INSTRUMENTS)}), hide_index=True, width="stretch")
    st.download_button(T("download_csv"), df.to_csv(index=False).encode("utf-8-sig"), file_name=f"trainee{tid}_progress.csv",
                       mime="text/csv")
