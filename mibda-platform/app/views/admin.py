"""Administration: users, audit log, retention."""
from __future__ import annotations

import pandas as pd
import streamlit as st

from app import ui
from app.ui import T
from or_intelligence import auth, config, db


def render() -> None:
    if not ui.require_role("admin"):
        return
    admin = ui.current_user()
    tab_u, tab_a, tab_d = st.tabs([T("tab_users"), T("tab_audit"), T("tab_data")])

    with tab_u:
        st.dataframe(pd.DataFrame(auth.list_users()).rename(columns={"display_name": T("name")}), hide_index=True, width="stretch")
        with st.form("new_user", clear_on_submit=True):
            c1, c2 = st.columns(2)
            username = c1.text_input(T("username"))
            display = c2.text_input(T("name"))
            c3, c4 = st.columns(2)
            role = c3.selectbox(T("role"), list(auth.ROLES), index=0)
            pw = c4.text_input(T("password"), type="password", help=T("password_rule"))
            if st.form_submit_button(T("create_user")):
                try:
                    uid = auth.create_user(username, pw, role, display or None)
                    db.log(admin["id"], "create_user", None, f"{username.strip().lower()} ({role})")
                    st.success(T("user_created"))
                except Exception as e:  # duplicate name, short password...
                    st.error(str(e))

    with tab_a:
        rows = [{T("time"): pd.Timestamp(r["at"], unit="s").strftime("%Y-%m-%d %H:%M"), T("username"): r["username"] or "-",
                 T("action"): r["action"], T("case"): str(r["case_id"] or ""), T("detail"): r["detail"]}
                for r in db.list_audit(300)]
        st.dataframe(pd.DataFrame(rows), hide_index=True, width="stretch")

    with tab_d:
        cases = db.list_cases(admin)
        expiring = [c for c in cases if c["retention_days"] and c["created_at"] + c["retention_days"] * 86400 <= db.now()]
        st.write(T("retention_status", n=len(expiring)))
        st.caption(T("retention_help"))
        if st.button(T("purge_now"), disabled=not expiring):
            n = db.purge_expired()
            db.log(admin["id"], "purge_expired", None, f"{n} cases")
            st.success(T("purged", n=n))
        st.caption(f"{T('data_folder')}: {config.DATA_DIR}")
