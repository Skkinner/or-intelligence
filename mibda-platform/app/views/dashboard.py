"""Landing page: hero, key numbers, recent cases, procedure coverage."""
from __future__ import annotations

import json

import plotly.graph_objects as go
import streamlit as st

from app import theme, ui
from app.ui import T
from or_intelligence import config, db, procedures
from or_intelligence.constants import INSTRUMENT_COLORS, INSTRUMENTS, N_INSTRUMENTS


def _go(page: str) -> None:
    st.switch_page(st.session_state["_pages"][page])


def render() -> None:
    user = ui.current_user()
    cases = db.list_cases(user)
    weights = config.WEIGHTS_PATH.exists()
    phase_model = config.PHASE_MODEL_PATH.exists()

    theme.hero(T("welcome", name=user["display_name"]), T("dash_sub"))

    total = sum(c["duration"] for c in cases)
    n_phased = sum(1 for c in cases if json.loads(c["stats_json"] or "{}").get("phases"))
    ready = [p for p in procedures.load_all() if p.status == "ready"]
    theme.kpis([
        (T("cases"), str(len(cases)), T("kpi_cases_hint")),
        (T("total_duration"), ui.fmt_time(total), T("kpi_time_hint")),
        (T("kpi_phased"), str(n_phased), T("kpi_phased_hint")),
        (T("kpi_procedures"), f"{len(ready)} / {len(procedures.load_all())}", T("kpi_procedures_hint"))])

    b1, b2, _ = st.columns([1.2, 1.2, 4.2])
    b1.button(T("nav_tracker"), on_click=_go, args=("tracker",), type="primary", width="stretch")
    b2.button(T("nav_library"), on_click=_go, args=("library",), width="stretch")

    if not cases:
        st.info(T("no_cases_start"))
    else:
        st.markdown(f"### {T('recent_cases')}")
        cards = "".join(ui.case_card_html(c) for c in cases[:6])
        st.markdown(f'<div class="ori-cards">{cards}</div>', unsafe_allow_html=True)

    usage = [0.0] * N_INSTRUMENTS
    for c in cases:
        u = json.loads(c["stats_json"] or "{}").get("usage", {})
        for i, n in enumerate(INSTRUMENTS):
            usage[i] += float(u.get(n, 0.0))
    if sum(usage) > 0:
        st.markdown(f"### {T('usage_all')}")
        fig = go.Figure(go.Bar(x=[ui.inst(i) for i in range(N_INSTRUMENTS)], y=[v / 60 for v in usage],
                               marker_color=[INSTRUMENT_COLORS[n] for n in INSTRUMENTS]))
        fig.update_layout(height=260, margin=dict(l=0, r=0, t=10, b=0), yaxis_title=T("minutes"))
        st.plotly_chart(fig, width="stretch")

