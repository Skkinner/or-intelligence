"""Language and analysis parameters (kept per browser session)."""
from __future__ import annotations

import streamlit as st

from app import ui
from app.ui import T
from or_intelligence import config


def render() -> None:
    choice = st.radio(T("language"), ["English", "العربية"], index=0 if ui.lang() == "en" else 1, horizontal=True)
    new = "ar" if choice == "العربية" else "en"
    if new != ui.lang():
        st.session_state["lang"] = new
        st.rerun()

    p = ui.params()
    st.subheader(T("analysis_params"))
    st.caption(T("params_hint"))
    conf = st.slider(T("p_conf"), 0.05, 0.95, float(p["conf"]), 0.05)
    smooth = st.select_slider(T("p_smooth"), options=[1, 3, 5, 7, 9], value=int(p["smooth"]))
    gap = st.slider(T("p_gap"), 1.0, 120.0, float(p["max_gap"]), 1.0)
    long_use = st.slider(T("p_long"), 30.0, 900.0, float(p["long_use_s"]), 10.0)
    privacy = st.checkbox(T("p_privacy"), value=bool(p.get("privacy", True)))
    st.session_state["params"] = {**st.session_state.get("params", {}), "conf": conf, "smooth": smooth,
                                  "max_gap": gap, "long_use_s": long_use, "privacy": privacy}
    if st.button(T("reset_defaults")):
        st.session_state["params"] = {}
        st.rerun()
    st.caption(f"{T('defaults')}: {config.DEFAULTS}")
