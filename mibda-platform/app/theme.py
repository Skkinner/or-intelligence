"""Visual layer: CSS and small HTML components (all dynamic text is escaped)."""
from __future__ import annotations

from html import escape

import streamlit as st

CSS = """
<style>
:root { --ink:#2A0A12; --muted:#8A7168; --tif:#5C061C; --tif-d:#B26A24; --tif-l:#F0DFD3; --beige:#F2E9E1;
        --card:rgba(255,255,255,.78); --edge:rgba(42,10,18,.08); --shadow:0 10px 30px rgba(42,10,18,.08); }
.stApp { background:
   radial-gradient(700px 420px at 92% -6%, rgba(92,6,28,.22), rgba(92,6,28,0) 70%),
   radial-gradient(640px 420px at -6% 18%, rgba(205,127,50,.5), rgba(245,158,107,0) 70%),
   radial-gradient(600px 380px at 60% 108%, rgba(92,6,28,.12), rgba(155,127,224,0) 70%),
   #F2E9E1; color:var(--ink); }
[data-testid="stHeader"] { background: rgba(242,233,225,.72); backdrop-filter: blur(12px); }
.block-container { padding-top: 1.4rem; max-width: 1200px; }
h1,h2,h3,h4 { letter-spacing:-0.01em; color:var(--ink); font-weight:800; }
[data-testid="stCaptionContainer"], .stCaption { color:var(--muted); }
a { color:var(--tif-d); }

/* sidebar */
[data-testid="stSidebar"] { background:#fff; border-inline-end:1px solid var(--edge); box-shadow:0 0 40px rgba(178,106,36,.08); }
[data-testid="stSidebarNav"] a, [data-testid="stSidebar"] a[data-testid="stSidebarNavLink"] { border-radius:14px; margin:2px 8px; }
[data-testid="stSidebar"] a[data-testid="stSidebarNavLink"][aria-current="page"] { background:#F0DFD3; }
[data-testid="stSidebar"] a[data-testid="stSidebarNavLink"][aria-current="page"] * { color:#B26A24 !important; font-weight:700; }
/* top navigation pills */
a[data-testid="stTopNavLink"] { border-radius:999px; padding:6px 14px; }
a[data-testid="stTopNavLink"]:hover { background:rgba(92,6,28,.12); }
a[data-testid="stTopNavLink"][aria-current="page"] { background:#5C061C; box-shadow:0 8px 18px rgba(92,6,28,.35); }
a[data-testid="stTopNavLink"][aria-current="page"], a[data-testid="stTopNavLink"][aria-current="page"] * { color:#fff !important; }

[data-testid="stExpander"], [data-testid="stForm"] { background:var(--card); border:1px solid var(--edge); border-radius:22px;
   box-shadow:var(--shadow); backdrop-filter: blur(10px); }
[data-testid="stForm"] { padding:16px; }
.stButton > button, .stDownloadButton > button { background:#fff; color:var(--ink); border:1px solid var(--edge); border-radius:999px;
   box-shadow:0 4px 14px rgba(42,10,18,.07); font-weight:600; }
.stButton > button:hover { border-color:var(--tif); color:var(--tif-d); }
.stButton > button[kind="primary"] { background:linear-gradient(135deg,#8A1F3B,#5C061C); color:#fff; border:none; box-shadow:0 8px 20px rgba(92,6,28,.35); }
[data-baseweb="input"], [data-baseweb="select"] > div, textarea { background:#fff !important; border-radius:14px !important; }
[data-testid="stAlert"], [data-testid="stAlert"] > div { background:rgba(255,255,255,.85) !important; border:1px solid var(--edge); border-radius:18px; color:var(--ink); }
[data-testid="stAlert"] * { color:var(--ink) !important; }
[data-testid="stTabs"] button[aria-selected="true"] { color:var(--tif-d); }
[data-testid="stDataFrame"] { border:1px solid var(--edge); border-radius:16px; }

.ori-hero { background: linear-gradient(120deg,#5C061C 0%,#CD7F32 55%,#E6C9A8 100%); color:#fff; border-radius:28px;
            padding:30px 34px; margin-bottom:20px; box-shadow:0 18px 40px rgba(92,6,28,.28); position:relative; overflow:hidden; }
.ori-hero::after { content:""; position:absolute; inset-inline-end:-50px; top:-60px; width:260px; height:260px; border-radius:50%;
                   background:radial-gradient(circle,rgba(255,255,255,.55),rgba(255,255,255,0) 70%); }
.ori-hero h1 { color:#fff; font-size:2rem; margin:0 0 4px; padding:0; position:relative; }
.ori-hero p { color:rgba(255,255,255,.92); margin:0 0 14px; font-size:1.04rem; position:relative; }
.ori-hero .ori-chip { position:relative; background:rgba(255,255,255,.26); color:#fff; border:1px solid rgba(255,255,255,.55); }

.ori-chip { display:inline-block; padding:3px 12px; border-radius:999px; font-size:.78rem; font-weight:700;
            margin-inline-end:6px; margin-bottom:4px; background:var(--tif-l); color:var(--tif-d); border:1px solid rgba(92,6,28,.28); }
.ori-chip.warn { background:#fdf0dd; color:#b8741a; border-color:#f3d9ab; }
.ori-chip.ok { background:#F0DFD3; color:#B26A24; border-color:#E4C9B0; }
.ori-chip.dim { background:rgba(42,10,18,.06); color:var(--muted); border-color:var(--edge); }

.ori-kpis { display:grid; grid-template-columns:repeat(auto-fit,minmax(190px,1fr)); gap:14px; margin:6px 0 20px; }
.ori-kpi { border-radius:26px; padding:18px 20px; color:#fff; box-shadow:0 14px 30px rgba(42,10,18,.14); position:relative; overflow:hidden;
           background:linear-gradient(145deg,#8A1F3B,#5C061C); }
.ori-kpi:nth-child(4n+2) { background:linear-gradient(145deg,#E6C9A8,#CD7F32); }
.ori-kpi:nth-child(4n+3) { background:linear-gradient(145deg,#EEDCC8,#D9A066); }
.ori-kpi:nth-child(4n+4) { background:linear-gradient(145deg,#CD7F32,#B26A24); }
.ori-kpi:nth-child(4n+2), .ori-kpi:nth-child(4n+3) { color:#2A0A12; }
.ori-kpi::after { content:""; position:absolute; inset-inline-end:-30px; bottom:-40px; width:120px; height:120px; border-radius:50%; background:rgba(255,255,255,.18); }
.ori-kpi .l { font-size:.76rem; opacity:.92; text-transform:uppercase; letter-spacing:.05em; font-weight:700; }
.ori-kpi .v { font-size:2rem; font-weight:800; line-height:1.2; }
.ori-kpi .h { font-size:.8rem; opacity:.92; }

.ori-steps { display:flex; gap:10px; flex-wrap:wrap; margin:6px 0 16px; }
.ori-step { flex:1 1 120px; min-width:110px; border-radius:20px; padding:12px 14px; border:1px solid var(--edge);
            background:var(--card); color:var(--muted); transition:all .25s; box-shadow:0 6px 16px rgba(42,10,18,.05); }
.ori-step .n { font-size:.72rem; font-weight:800; opacity:.7; }
.ori-step .t { font-size:.88rem; font-weight:700; line-height:1.25; margin:2px 0 4px; }
.ori-step .d { font-size:.78rem; }
.ori-step.done { background:var(--tif-l); color:var(--tif-d); border-color:rgba(92,6,28,.30); }
.ori-step.active { background:linear-gradient(145deg,#8A1F3B,#5C061C); color:#fff; border-color:transparent;
                   box-shadow:0 14px 28px rgba(92,6,28,.40); transform:translateY(-3px) scale(1.03); }

.ori-now { background:var(--card); border:1px solid var(--edge); border-radius:24px; padding:18px 20px; box-shadow:var(--shadow); }
.ori-now .k { font-size:.76rem; color:var(--muted); text-transform:uppercase; letter-spacing:.05em; font-weight:700; }
.ori-now .big { font-size:1.4rem; font-weight:800; color:var(--ink); margin:2px 0 10px; }
.ori-bar { height:10px; background:rgba(42,10,18,.08); border-radius:999px; overflow:hidden; margin:6px 0 12px; }
.ori-bar > span { display:block; height:100%; background:linear-gradient(90deg,#5C061C,#E6C9A8); border-radius:999px; }

.ori-cards { display:grid; grid-template-columns:repeat(auto-fill,minmax(260px,1fr)); gap:16px; margin:8px 0 18px; }
.ori-card { background:var(--card); border:1px solid var(--edge); border-radius:26px; overflow:hidden; box-shadow:var(--shadow); }
.ori-card .img { height:140px; background:linear-gradient(145deg,#8A1F3B,#5C061C) center/cover no-repeat; }
.ori-card .b { padding:14px 16px; }
.ori-card .t { font-weight:800; color:var(--ink); font-size:.96rem; margin-bottom:2px; }
.ori-card .s { font-size:.8rem; color:var(--muted); margin-bottom:8px; }
.ori-strip { display:flex; height:9px; border-radius:999px; overflow:hidden; margin:6px 0 8px; background:rgba(42,10,18,.08); }
.ori-strip > span { display:block; height:100%; }

.ori-proc { background:var(--card); border:1px solid var(--edge); border-radius:24px; padding:16px 18px; margin-bottom:12px; box-shadow:var(--shadow); }
.ori-proc.ready { border-color:rgba(92,6,28,.55); }
.ori-proc h4 { margin:0 0 2px; color:var(--ink); }
.ori-proc ul { margin:6px 0 0; padding-inline-start:18px; font-size:.86rem; color:var(--muted); }

.ori-brand { display:flex; align-items:center; gap:14px; margin-bottom:8px; }
.ori-brand img { width:68px; height:68px; }
.ori-brand .n { font-size:2.2rem; font-weight:800; color:var(--ink); line-height:1; }
.ori-brand .s { color:var(--muted); font-size:.95rem; }

/* ---- MIBDA brand: deep burgundy, warm beige, muted copper ---- */
[data-testid="stSidebar"] { background:linear-gradient(180deg,#4A0516 0%,#5C061C 55%,#3A0412 100%); border-inline-end:none;
   box-shadow:8px 0 40px rgba(42,10,18,.18); }
[data-testid="stSidebar"] * { color:#F2E9E1; }
[data-testid="stSidebarNav"] a, [data-testid="stSidebar"] a[data-testid="stSidebarNavLink"] { border-radius:12px; margin:2px 10px; padding:9px 12px; }
[data-testid="stSidebar"] a[data-testid="stSidebarNavLink"]:hover { background:rgba(242,233,225,.10); }
[data-testid="stSidebar"] a[data-testid="stSidebarNavLink"][aria-current="page"] { background:rgba(205,127,50,.22); box-shadow:inset 3px 0 0 #CD7F32; }
[data-testid="stSidebar"] a[data-testid="stSidebarNavLink"][aria-current="page"] * { color:#fff !important; font-weight:700; }
[data-testid="stSidebar"] .stButton > button { background:rgba(242,233,225,.10); color:#F2E9E1; border:1px solid rgba(242,233,225,.25); box-shadow:none; }
[data-testid="stSidebar"] .stButton > button:hover { background:#CD7F32; border-color:#CD7F32; color:#fff; }
[data-testid="stSidebar"] hr { border-color:rgba(242,233,225,.18); }

.ori-hero { background:linear-gradient(125deg,#3A0412 0%,#5C061C 52%,#7A1330 100%); border-radius:22px; padding:30px 34px;
            box-shadow:0 18px 40px rgba(92,6,28,.30); }
.ori-hero::after { background:radial-gradient(circle,rgba(205,127,50,.55),rgba(205,127,50,0) 70%); }
.ori-hero .ori-chip { background:rgba(242,233,225,.16); border-color:rgba(242,233,225,.4); }

.ori-kpi { border-radius:18px; background:linear-gradient(145deg,#7A1330,#5C061C); }
.ori-kpi:nth-child(4n+2) { background:linear-gradient(145deg,#E0A96D,#CD7F32); color:#2A0A12; }
.ori-kpi:nth-child(4n+3) { background:#fff; color:#2A0A12; border:1px solid var(--edge); }
.ori-kpi:nth-child(4n+4) { background:linear-gradient(145deg,#4A0516,#2E030E); }
.ori-kpi:nth-child(4n+3)::after { background:rgba(205,127,50,.14); }

.ori-card, .ori-now, .ori-proc, [data-testid="stExpander"], [data-testid="stForm"] { border-radius:18px; background:#fff; }
.ori-card .img { background:linear-gradient(145deg,#8A1F3B,#5C061C) center/cover no-repeat; }
.ori-bar > span { background:linear-gradient(90deg,#CD7F32,#E0A96D); }
.ori-step.active { background:linear-gradient(145deg,#8A1F3B,#5C061C); box-shadow:0 14px 28px rgba(92,6,28,.35); }
.ori-step.done { background:#F0DFD3; color:#8A4B12; border-color:rgba(205,127,50,.4); }
.ori-chip { background:#F0DFD3; color:#8A4B12; border-color:rgba(205,127,50,.35); }
.ori-chip.ok { background:#EBD3D8; color:#5C061C; border-color:#d9aeb8; }

.stButton > button[kind="primary"] { background:linear-gradient(135deg,#8A1F3B,#5C061C); box-shadow:0 8px 20px rgba(92,6,28,.35); }
.stButton > button:hover { border-color:#CD7F32; color:#8A4B12; }
[data-testid="stTabs"] button[aria-selected="true"] { color:#5C061C; }
[data-testid="stTabs"] [data-baseweb="tab-highlight"] { background-color:#CD7F32; }
a { color:#B26A24; }
[data-testid="stMetric"] { background:#fff; border:1px solid var(--edge); border-radius:16px; padding:12px 16px; box-shadow:var(--shadow); }
</style>
"""


def inject() -> None:
    st.markdown(CSS, unsafe_allow_html=True)


def chip(text: str, kind: str = "") -> str:
    return f'<span class="ori-chip {kind}">{escape(str(text))}</span>'


def hero(title: str, subtitle: str, chips: list[str] | None = None) -> None:
    st.markdown(f'<div class="ori-hero"><h1>{escape(title)}</h1><p>{escape(subtitle)}</p>{"".join(chips or [])}</div>',
                unsafe_allow_html=True)


def kpis(items: list[tuple[str, str, str]]) -> None:
    cells = "".join(f'<div class="ori-kpi"><div class="l">{escape(l)}</div><div class="v">{escape(str(v))}</div>'
                    f'<div class="h">{escape(h)}</div></div>' for l, v, h in items)
    st.markdown(f'<div class="ori-kpis">{cells}</div>', unsafe_allow_html=True)


def steps(items: list[dict]) -> None:
    """items: {name, state: done|active|todo, time, index}"""
    cells = "".join(
        f'<div class="ori-step {escape(i["state"])}"><div class="n">{i["index"]}</div>'
        f'<div class="t">{escape(i["name"])}</div><div class="d">{escape(i["time"])}</div></div>' for i in items)
    st.markdown(f'<div class="ori-steps">{cells}</div>', unsafe_allow_html=True)


def phase_strip(segments: list[tuple[float, str]]) -> str:
    """segments: [(weight, color)] -> thin multi-colour bar."""
    total = sum(w for w, _ in segments) or 1.0
    return '<div class="ori-strip">' + "".join(
        f'<span style="width:{100 * w / total:.2f}%;background:{c}"></span>' for w, c in segments) + "</div>"


def case_card(title: str, subtitle: str, chips_html: str, strip_html: str, thumb_uri: str | None) -> str:
    img = f'style="background-image:url({thumb_uri})"' if thumb_uri else ""
    return (f'<div class="ori-card"><div class="img" {img}></div><div class="b"><div class="t">{escape(title)}</div>'
            f'<div class="s">{escape(subtitle)}</div>{strip_html}{chips_html}</div></div>')


ASSETS = __import__("pathlib").Path(__file__).resolve().parent / "assets"
NAME_AR, NAME_EN = "مبضع", "MIBDA'"


def brand_header(subtitle: str) -> None:
    """Login-page brand block: symbol + wordmark (inline SVG, no external files at runtime)."""
    import base64
    svg = (ASSETS / "mibda_logo_light.svg").read_bytes()
    uri = "data:image/svg+xml;base64," + base64.b64encode(svg).decode()
    st.markdown(f'<div class="ori-brand"><img src="{uri}"><div><div class="n">{NAME_AR} | {NAME_EN}</div>'
                f'<div class="s">{escape(subtitle)}</div></div></div>', unsafe_allow_html=True)
