"""Sign-in page."""
from __future__ import annotations

import streamlit as st

import os

from app import theme, ui
from app.ui import T
from or_intelligence import auth, db


def render() -> None:
    theme.brand_header(T("tagline"))
    left, _ = st.columns([2, 3])
    with left:
        choice = st.radio(T("language"), ["English", "العربية"], index=0 if ui.lang() == "en" else 1, horizontal=True)
        new = "ar" if choice == "العربية" else "en"
        if new != ui.lang():
            st.session_state["lang"] = new
            st.rerun()
        with st.form("login"):
            username = st.text_input(T("username"))
            password = st.text_input(T("password"), type="password")
            if st.form_submit_button(T("sign_in")):
                user = auth.authenticate(username, password)
                if user:
                    st.session_state["user"] = user
                    db.log(user["id"], "login")
                    st.rerun()
                else:
                    db.log(None, "login_failed", detail=username.strip().lower()[:40])
                    st.error(T("bad_login"))
    if os.environ.get("ORI_DEMO_MODE") == "1":          # local demo only: one click, no password
        demo = next((u for u in auth.list_users() if u["username"] == "instructor"), None)
        if demo and st.button(T("enter_demo"), type="primary"):
            st.session_state["user"] = demo
            db.log(demo["id"], "login", detail="demo")
            st.rerun()
    st.info(T("edu_notice"))
