"""Shared Streamlit helpers: language, session, drawing, charts."""
from __future__ import annotations

from functools import lru_cache
from pathlib import Path

import numpy as np
import plotly.graph_objects as go
import streamlit as st
from PIL import Image, ImageDraw, ImageFilter

from or_intelligence import config, procedures, service, timeline
from or_intelligence.i18n import tr
from or_intelligence.models import Box, CaseAnalysis

fmt_time = timeline.fmt_time


def lang() -> str:
    return st.session_state.get("lang", "en")


def T(key: str, **kw) -> str:
    return tr(key, lang(), **kw)


def current_user() -> dict | None:
    return st.session_state.get("user")


def params() -> dict:
    return {**config.DEFAULTS, **st.session_state.get("params", {})}


def default_proc() -> procedures.Procedure:
    return procedures.get(procedures.DEFAULT_ID)


def proc_of_case(case) -> procedures.Procedure:
    return procedures.resolve(case["procedure"])


def inst(i: int, proc: procedures.Procedure | None = None) -> str:
    return (proc or default_proc()).instrument_label(i, lang())


def phase_name(i: int | None, proc: procedures.Procedure | None = None) -> str:
    return (proc or default_proc()).phase_label(i, lang())


def inject_css() -> None:
    rtl = """
    [data-testid="stAppViewContainer"], [data-testid="stSidebar"], [data-testid="stHeader"] { direction: rtl; }
    .js-plotly-plot, .stPlotlyChart { direction: ltr; }
    """ if lang() == "ar" else ""
    st.markdown(f"""<style>
    .ori-badge {{display:inline-block;padding:2px 10px;border-radius:999px;font-size:.8rem;font-weight:600;}}
    .ori-demo {{background:#fdf0dd;color:#b8741a;border:1px solid #f3d9ab;}}
    .ori-model {{background:#F0DFD3;color:#B26A24;border:1px solid rgba(92,6,28,.35);}}
    .ori-note {{font-size:.85rem;color:#8A7168;}}
    {rtl}
    </style>""", unsafe_allow_html=True)


def source_badge(source: str) -> str:
    if source == "model":
        return f'<span class="ori-badge ori-model">{T("src_model")}</span>'
    return f'<span class="ori-badge ori-demo">{T("src_annotations")}</span>'


def require_role(*roles: str) -> bool:
    u = current_user()
    if not u or u["role"] not in roles:
        st.error(T("not_allowed"))
        return False
    return True


# ---- drawing ---------------------------------------------------------------
def draw_boxes(img: Image.Image, boxes: list[Box], only: set[int] | None = None, labels: bool = True,
               proc: procedures.Procedure | None = None) -> Image.Image:
    proc = proc or default_proc()
    out = img.convert("RGB").copy()
    d = ImageDraw.Draw(out)
    W, H = out.size
    for b in boxes:
        if (only is not None and b.instrument not in only) or not 0 <= b.instrument < proc.n_instruments:
            continue
        color = proc.instrument_color(b.instrument)
        x1, y1, x2, y2 = b.x * W, b.y * H, (b.x + b.w) * W, (b.y + b.h) * H
        d.rectangle([x1, y1, x2, y2], outline=color, width=3)
        if labels:
            txt = proc.instrument_names[b.instrument] + (f" {b.conf:.2f}" if b.conf < 1.0 else "")
            tw = d.textlength(txt) + 8
            d.rectangle([x1, max(0, y1 - 14), x1 + tw, max(14, y1)], fill=color)
            d.text((x1 + 4, max(0, y1 - 13)), txt, fill="white")
    return out


@lru_cache(maxsize=256)
def load_image(path: str) -> Image.Image:
    with Image.open(path) as im:
        return im.convert("RGB")


def bgr_to_pil(arr: np.ndarray) -> Image.Image:
    return Image.fromarray(arr[:, :, ::-1])


def phase_status(s: timeline.PhaseSegment) -> str:
    """Plain-language provenance of a phase: annotation, or a model estimate (flagged when uncertain)."""
    if s.verified:
        return T("phase_verified")
    conf = f" ({100 * s.conf:.0f}%)" if s.conf is not None else ""
    return T("phase_uncertain") + conf if s.uncertain else T("phase_estimated") + conf


# ---- charts ----------------------------------------------------------------
def timeline_fig(intervals, phases, duration: float, cursor: float | None = None,
                 only: set[int] | None = None, height: int | None = None,
                 proc: procedures.Procedure | None = None) -> go.Figure:
    proc = proc or default_proc()
    labels = [inst(i, proc) for i in range(proc.n_instruments)]
    phase_row = T("phase_row")
    rows = labels + ([phase_row] if phases else [])
    fig = go.Figure()
    for i in range(proc.n_instruments):
        if only is not None and i not in only:
            continue
        ivs = [iv for iv in intervals if iv.instrument == i]
        if not ivs:
            continue
        fig.add_trace(go.Bar(
            base=[iv.start for iv in ivs], x=[iv.duration for iv in ivs], y=[labels[i]] * len(ivs),
            orientation="h", marker_color=proc.instrument_color(i), showlegend=False,
            customdata=[[fmt_time(iv.start), fmt_time(iv.end)] for iv in ivs],
            hovertemplate=f"{labels[i]}<br>%{{customdata[0]}} - %{{customdata[1]}}<extra></extra>"))
    for s in phases:
        fig.add_trace(go.Bar(
            base=[s.start], x=[max(1.0, s.end - s.start)], y=[phase_row], orientation="h",
            marker_color=proc.phase_color(s.phase), showlegend=False,
            marker_pattern_shape="" if s.verified else "/", marker_opacity=1.0 if s.verified else 0.7,
            customdata=[[phase_name(s.phase, proc), fmt_time(s.start), fmt_time(s.end), phase_status(s)]],
            hovertemplate="%{customdata[0]}<br>%{customdata[1]} - %{customdata[2]}<br>%{customdata[3]}<extra></extra>"))
    # Invisible points make every row clickable: a click returns the time under the cursor.
    grid = np.linspace(0, max(duration, 1.0), 300)
    fig.add_trace(go.Scatter(
        x=np.tile(grid, len(rows)), y=np.repeat(rows, len(grid)), mode="markers",
        # hoverinfo="none" (not "skip"): "skip" also disables click events in Plotly
        marker=dict(size=14, opacity=0.001), hoverinfo="none", showlegend=False, name="click"))
    ticks = np.linspace(0, duration, 7) if duration > 0 else [0]
    fig.update_layout(
        barmode="overlay", height=height or 60 + 34 * len(rows), margin=dict(l=10, r=10, t=10, b=30),
        xaxis=dict(range=[0, max(duration, 1.0)], tickvals=list(ticks), ticktext=[fmt_time(t) for t in ticks]),
        yaxis=dict(autorange="reversed", categoryorder="array", categoryarray=rows),
        clickmode="event+select", dragmode="select", selectdirection="h", plot_bgcolor="rgba(0,0,0,0)")
    if cursor is not None:
        fig.add_shape(type="line", x0=cursor, x1=cursor, y0=0, y1=1, yref="paper",
                      line=dict(color="#2A0A12", width=2, dash="dot"))
    return fig


def click_time(chart_key: str) -> float | None:
    ev = st.session_state.get(chart_key)
    try:
        pts = ev["selection"]["points"] if ev else []
    except (KeyError, TypeError):
        pts = []
    xs = [p["x"] for p in pts if isinstance(p.get("x"), (int, float))]
    return float(np.mean(xs)) if xs else None


def _protect(im: Image.Image) -> Image.Image:
    """Dashboard previews are blurred on the server (the sharp pixels never reach the browser); the sharp frame is
    only shown inside the case review, which checks who may open the case."""
    return im.filter(ImageFilter.GaussianBlur(radius=16))


@lru_cache(maxsize=64)
def _thumb(path: str) -> str | None:
    import base64
    import io
    try:
        with Image.open(path) as im:
            im = im.convert("RGB")
            im.thumbnail((440, 260))
            im = _protect(im)
            buf = io.BytesIO()
            im.save(buf, "JPEG", quality=72)
        return "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode()
    except OSError:
        return None


def case_card_html(case) -> str:
    """HTML card: thumbnail, phase strip, key facts. Thumbnail only for frame-sequence cases."""
    from app import theme
    a = load_case_analysis(case)
    proc = proc_of_case(case)
    thumb = None
    if case["media_kind"] == "frames" and a.frames:
        mid = sorted(a.frames, key=lambda f: f.t)[len(a.frames) // 2]
        thumb = _thumb(str(Path(case["media_path"]) / (mid.image or "")))
    elif case["media_kind"] == "video":
        thumb = _video_thumb(case["media_path"], round(a.duration / 2))
    segs = timeline.phase_segments(a)
    strip = theme.phase_strip([(max(1.0, s.end - s.start), proc.phase_color(s.phase)) for s in segs]) if segs else ""
    kind = "" if case["source"] == "model" else "warn"
    chips = theme.chip("🔒 " + T("preview_protected"), "dim") + theme.chip(fmt_time(case["duration"])) + theme.chip(
        T("src_model") if case["source"] == "model" else T("src_annotations_short"), kind)
    return theme.case_card(f'#{case["id"]} · {case["title"]}', proc.label(lang()), chips, strip, thumb)


@lru_cache(maxsize=64)
def _video_thumb(path: str, t: int) -> str | None:
    import base64
    import io

    from or_intelligence.analysis import read_video_frame
    frame = read_video_frame(path, float(t), privacy=True)
    if frame is None:
        return None
    im = bgr_to_pil(frame)
    im.thumbnail((440, 260))
    im = _protect(im)
    buf = io.BytesIO()
    im.save(buf, "JPEG", quality=72)
    return "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode()


@st.cache_data(show_spinner=False)
def cached_analysis(path: str, mtime: float, model_mtime: float = 0.0) -> CaseAnalysis:
    return service.refresh_estimated_phases(CaseAnalysis.load(path))


def load_case_analysis(case) -> CaseAnalysis:
    p = Path(case["analysis_path"])
    mp = config.PHASE_MODEL_PATH
    return cached_analysis(str(p), p.stat().st_mtime, mp.stat().st_mtime if mp.exists() else 0.0)
