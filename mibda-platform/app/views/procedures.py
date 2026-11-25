"""Procedure library: which operations the platform covers and what each still needs."""
from __future__ import annotations

from html import escape

import streamlit as st

from app import theme, ui
from app.ui import T
from or_intelligence import config, db, procedures


def render() -> None:
    cases = db.list_cases(ui.current_user())
    reg = procedures.dataset_registry()
    procs = procedures.load_all()
    ready = [p for p in procs if p.status == "ready"]
    theme.hero(T("nav_procedures"), T("procedures_sub"),
               [theme.chip(T("n_ready", n=len(ready)), "ok"), theme.chip(T("n_planned", n=len(procs) - len(ready)), "warn")])
    st.caption(T("procedures_honest"))

    cols = st.columns(2)
    for i, p in enumerate(procs):
        n_cases = sum(1 for c in cases if ui.proc_of_case(c).id == p.id)
        caps = "".join(f"<li><b>{escape(k.replace('_', ' '))}</b>: {escape(v)}</li>" for k, v in p.capabilities.items())
        links = " · ".join(f'<a href="{escape(reg[d]["url"])}" target="_blank">{escape(reg[d]["name"])}</a>'
                           for d in p.datasets if d in reg)
        status = {"ready": theme.chip(T("status_ready"), "ok"),
                  "adapter-untested": theme.chip(T("status_untested"), "warn")}.get(p.status, theme.chip(T("status_planned"), "dim"))
        extra = theme.chip(T("n_cases_chip", n=n_cases), "") if n_cases else ""
        card_class = "ready" if p.status == "ready" else ""
        with cols[i % 2]:
            st.markdown(
                f'<div class="ori-proc {card_class}"><h4>{escape(p.label(ui.lang()))}</h4>'
                f'<div style="color:#8A7168;font-size:.82rem;margin-bottom:6px">{escape(p.specialty_label(ui.lang()))}</div>'
                f'{status}{extra}<ul>{caps}</ul>'
                f'<div style="font-size:.8rem;margin-top:8px">{T("datasets")}: {links or "-"}</div></div>',
                unsafe_allow_html=True)

    st.markdown(f"#### {T('add_procedure')}")
    st.markdown(T("add_procedure_steps"))
    st.caption(f"{config.PROCEDURES_YAML.name}, {config.DATASETS_YAML.name}")
