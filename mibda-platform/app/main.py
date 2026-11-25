"""Entry point:  streamlit run app/main.py"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import streamlit as st  # noqa: E402

from app import theme, ui  # noqa: E402
from app.ui import T  # noqa: E402
from app.views import dashboard, library, live, login, review, settings, tracker  # noqa: E402
from or_intelligence import db  # noqa: E402

st.set_page_config(page_title="مبضع | MIBDA'", page_icon=str(theme.ASSETS / "mibda_icon.svg"), layout="wide", initial_sidebar_state="expanded")
db.init_db()
st.session_state.setdefault("lang", "en")
ui.inject_css()
theme.inject()

st.logo(str(theme.ASSETS / "mibda_logo_dark.svg"), size="large")
user = ui.current_user()
if user is None:
    st.navigation([st.Page(login.render, title=T("sign_in"), url_path="login")], position="hidden").run()
    st.stop()

pages = {
    "dashboard": st.Page(dashboard.render, title=T("nav_dashboard"), icon=":material/dashboard:", url_path="dashboard", default=True),
    "live": st.Page(live.render, title=T("nav_live"), icon=":material/videocam:", url_path="live"),
    "tracker": st.Page(tracker.render, title=T("nav_tracker"), icon=":material/monitor_heart:", url_path="tracker"),
    "library": st.Page(library.render, title=T("nav_library"), icon=":material/video_library:", url_path="library"),
    "review": st.Page(review.render, title=T("nav_review"), icon=":material/timeline:", url_path="review"),
}
pages["settings"] = st.Page(settings.render, title=T("nav_settings"), icon=":material/settings:", url_path="settings")
st.session_state["_pages"] = pages

st.sidebar.markdown(f"**{user['display_name']}** · {T('role_' + user['role'])}")
if st.sidebar.button(T("sign_out")):
    db.log(user["id"], "logout")
    for k in list(st.session_state.keys()):
        if k != "lang":
            del st.session_state[k]
    st.rerun()

st.navigation(list(pages.values()), position="sidebar").run()
