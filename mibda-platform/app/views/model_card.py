"""Model metrics, supported datasets and the limits of the system."""
from __future__ import annotations

import json

import pandas as pd
import streamlit as st
import yaml

from app import ui
from app.ui import T
from or_intelligence import config
from or_intelligence.constants import INSTRUMENTS


def render() -> None:
    st.subheader(T("model_metrics"))
    if config.METRICS_PATH.exists():
        m = json.loads(config.METRICS_PATH.read_text(encoding="utf-8"))
        o = m["overall"]
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("mAP@0.5", f'{o["map50"]:.3f}')
        c2.metric("mAP@0.5:0.95", f'{o["map50_95"]:.3f}')
        c3.metric(T("precision"), f'{o["precision"]:.3f}')
        c4.metric(T("recall"), f'{o["recall"]:.3f}')
        rows = [{T("instrument"): ui.inst(INSTRUMENTS.index(k)), "mAP@0.5": round(v["map50"], 3),
                 "mAP@0.5:0.95": round(v["map50_95"], 3), T("precision"): round(v["precision"], 3),
                 T("recall"): round(v["recall"], 3)} for k, v in m["per_class"].items()]
        st.dataframe(pd.DataFrame(rows), hide_index=True, width="stretch")
        st.caption(T("metrics_meta", split=m["split"], w=m["weights"], at=m["evaluated_at"]))
        if m.get("classes_missing_from_split"):
            st.warning(T("classes_missing") + ": " + ", ".join(m["classes_missing_from_split"]))
    else:
        st.info(T("no_metrics"))

    st.subheader(T("datasets"))
    st.caption(T("datasets_hint"))
    if config.DATASETS_YAML.exists():
        data = yaml.safe_load(config.DATASETS_YAML.read_text(encoding="utf-8"))["datasets"]
        df = pd.DataFrame([{
            T("name"): d["name"], T("procedure"): d["procedure"], T("contents"): d["contents"],
            T("license"): d["license"], T("access"): d["access"], T("adapter"): d["adapter"],
            T("link"): d["url"]} for d in data])
        st.dataframe(df, hide_index=True, width="stretch",
                     column_config={T("link"): st.column_config.LinkColumn(T("link"))})

    st.subheader(T("limits"))
    for k in ("limit_1", "limit_2", "limit_3", "limit_4", "limit_5"):
        st.write("• " + T(k))
