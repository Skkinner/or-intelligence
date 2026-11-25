"""Add cases: upload a recorded video (needs trained weights) or import the public demo dataset."""
from __future__ import annotations

import importlib.util
from pathlib import Path

import streamlit as st

from app import ui
from app.ui import T
from or_intelligence import auth, config, db, service


def render() -> None:
    user = ui.current_user()
    tab_up, tab_import = st.tabs([T("tab_upload"), T("tab_import")])

    with tab_up:
        weights_ok = config.WEIGHTS_PATH.exists()
        yolo_ok = importlib.util.find_spec("ultralytics") is not None
        if not (weights_ok and yolo_ok):
            st.warning(T("no_weights_hint"))
            if not yolo_ok:
                st.caption(T("no_ultralytics"))
        else:
            p = ui.params()
            file = st.file_uploader(T("video_file"), type=["mp4", "mov", "avi", "mkv"])
            title = st.text_input(T("title"), value=Path(file.name).stem if file else "")
            tags = st.text_input(T("tags"), placeholder="cholecystectomy, resident-3")
            trainee_id = user["id"] if user["role"] == "trainee" else None
            if user["role"] in ("admin", "instructor"):
                trainees = [u for u in auth.list_users() if u["role"] == "trainee"]
                ids = [None] + [u["id"] for u in trainees]
                names = {None: "-", **{u["id"]: u["display_name"] for u in trainees}}
                trainee_id = st.selectbox(T("trainee"), ids, format_func=lambda i: names[i])
            retention = st.number_input(T("retention_days"), 1, 3650, config.DEFAULT_RETENTION_DAYS)
            step = st.number_input(T("sample_step"), 0.2, 10.0, float(p["sample_step_s"]), 0.2)
            consent = st.checkbox(T("consent_text"))
            if st.button(T("analyze"), type="primary", disabled=not (file and title.strip() and consent)):
                from or_intelligence.detector import YoloDetector
                bar = st.progress(0.0, text=T("analyzing"))
                cid = service.create_video_case(
                    data=file.getvalue(), filename=file.name, title=title.strip(), owner_id=user["id"],
                    trainee_id=trainee_id, tags=tags, retention_days=int(retention),
                    detector=YoloDetector(config.WEIGHTS_PATH, conf=p["conf"]), step_s=float(step),
                    progress=lambda v: bar.progress(min(1.0, v), text=T("analyzing")))
                db.log(user["id"], "upload_case", cid, f"retention={int(retention)}d")
                st.session_state["case_id"] = cid
                st.success(T("analysis_done"))
                st.button(T("open_case"), on_click=lambda: st.switch_page(st.session_state["_pages"]["review"]))
            st.caption(T("privacy_note"))

    with tab_import:
        if user["role"] not in ("admin", "instructor"):
            st.info(T("not_allowed"))
        else:
            st.markdown(T("import_help"))
            root = st.text_input(T("dataset_folder"), placeholder=r"C:\data\cholect50-challenge-val")
            if st.button(T("import_btn"), disabled=not root.strip()):
                path = Path(root.strip())
                if not (path / "labels").is_dir():
                    st.error(T("import_bad_folder"))
                else:
                    ids = service.import_cholect50(path, user["id"])
                    db.log(user["id"], "import_dataset", None, f"{len(ids)} cases from {path.name}")
                    st.success(T("import_done", n=len(ids)))

            st.divider()
            st.markdown(T("import_cataract_help"))
            croot = st.text_input(T("dataset_folder") + " (Cataract-101)", placeholder=r"C:\data\cataract-101", key="cat_root")
            climit = st.number_input(T("import_limit"), 1, 101, 5, key="cat_limit")
            if st.button(T("import_cataract_btn"), disabled=not croot.strip()):
                cpath = Path(croot.strip())
                if not cpath.is_dir():
                    st.error(T("import_bad_folder"))
                else:
                    res = service.import_cataract101(cpath, user["id"], limit=int(climit))
                    db.log(user["id"], "import_dataset", None, f"{len(res['ids'])} cataract cases from {cpath.name}")
                    st.success(T("import_done", n=len(res["ids"])))
                    if res["unmatched"]:
                        st.warning(T("import_unmatched", n=len(res["unmatched"])))
                    for name, why in list(res["skipped"].items())[:5]:
                        st.error(f"{name}: {why}")
