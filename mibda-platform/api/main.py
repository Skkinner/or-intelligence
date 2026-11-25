"""HTTP API for the React front end:  uvicorn api.main:app --port 8000

Thin layer over the existing platform modules (db, timeline, service, case_report, assistant, references, ...).
Authentication is a signed, HTTP-only session cookie; every case route re-checks db.can_view."""
from __future__ import annotations

import base64
import hashlib
import hmac
import io
import json
import os
import secrets
import tempfile
import time
from functools import lru_cache
from pathlib import Path

import requests
from fastapi import Depends, FastAPI, HTTPException, Request, Response
from fastapi.responses import FileResponse, JSONResponse
from PIL import Image, ImageFilter
from pydantic import BaseModel

from or_intelligence import (assistant, auth, case_report, casecontext, config, db, deid, llm, procedures, references,
                             report, service, timeline)
from or_intelligence.analysis import read_video_frame
from or_intelligence.i18n import STRINGS
from or_intelligence.insights import review_flags
from or_intelligence.models import CaseAnalysis

DOCTORS = ("admin", "instructor")
COOKIE = "mibda_session"
TTL = 12 * 3600

app = FastAPI(title="MIBDA API", docs_url="/api/docs", openapi_url="/api/openapi.json")


@app.on_event("startup")
def _startup() -> None:
    config.ensure_dirs()
    db.init_db()


# ------------------------------------------------------------------ auth (signed cookie)
def _secret() -> bytes:
    env = os.environ.get("ORI_API_SECRET")
    if env:
        return env.encode()
    f = config.DATA_DIR / ".api_secret"
    config.ensure_dirs()
    if not f.exists():
        f.write_text(secrets.token_hex(32))
    return f.read_text().strip().encode()


def _sign(payload: str) -> str:
    return hmac.new(_secret(), payload.encode(), hashlib.sha256).hexdigest()


def _make_token(uid: int) -> str:
    body = base64.urlsafe_b64encode(json.dumps({"u": uid, "e": int(time.time()) + TTL}).encode()).decode()
    return f"{body}.{_sign(body)}"


def _read_token(tok: str | None) -> int | None:
    if not tok or "." not in tok:
        return None
    body, sig = tok.rsplit(".", 1)
    if not hmac.compare_digest(sig, _sign(body)):
        return None
    try:
        d = json.loads(base64.urlsafe_b64decode(body.encode()))
    except ValueError:
        return None
    return d["u"] if d.get("e", 0) > time.time() else None


def current_user(request: Request) -> dict:
    uid = _read_token(request.cookies.get(COOKIE))
    user = auth.get_user(uid) if uid else None
    if not user:
        raise HTTPException(401, "not signed in")
    return user


def _set_cookie(resp: Response, uid: int) -> None:
    resp.set_cookie(COOKIE, _make_token(uid), httponly=True, samesite="lax", max_age=TTL, path="/")


class Login(BaseModel):
    username: str
    password: str


@app.get("/api/meta")
def meta() -> dict:
    ok, why = llm.status()
    return {"demo": os.environ.get("ORI_DEMO_MODE") == "1", "ai": {"ok": ok, "reason": why}}


@app.get("/api/i18n")
def i18n() -> dict:
    return {k: dict(v) for k, v in STRINGS.items()}


@app.post("/api/login")
def login(body: Login, response: Response) -> dict:
    user = auth.authenticate(body.username, body.password)
    if not user:
        db.log(None, "login_failed", detail=body.username.strip().lower()[:40])
        raise HTTPException(401, "bad credentials")
    db.log(user["id"], "login")
    _set_cookie(response, user["id"])
    return user


@app.post("/api/demo")
def demo(response: Response) -> dict:
    if os.environ.get("ORI_DEMO_MODE") != "1":
        raise HTTPException(404)
    user = next((u for u in auth.list_users() if u["username"] == "instructor"), None)
    if not user:
        raise HTTPException(404)
    db.log(user["id"], "login", detail="demo")
    _set_cookie(response, user["id"])
    return user


@app.post("/api/logout")
def logout(response: Response, user: dict = Depends(current_user)) -> dict:
    db.log(user["id"], "logout")
    response.delete_cookie(COOKIE, path="/")
    return {"ok": True}


@app.get("/api/me")
def me(user: dict = Depends(current_user)) -> dict:
    return user


# ------------------------------------------------------------------ case helpers
def _get_case(case_id: int, user: dict):
    case = db.get_case(case_id)
    if case is None:
        raise HTTPException(404, "case not found")
    if not db.can_view(user, case):
        raise HTTPException(403, "not allowed")
    return case


@lru_cache(maxsize=32)
def _analysis_cached(path: str, mtime: float, model_mtime: float) -> CaseAnalysis:
    return service.refresh_estimated_phases(CaseAnalysis.load(path))


def _analysis(case) -> CaseAnalysis:
    p = Path(case["analysis_path"])
    mp = config.PHASE_MODEL_PATH
    return _analysis_cached(str(p), p.stat().st_mtime, mp.stat().st_mtime if mp.exists() else 0.0)


class Ctx:
    """Everything derived from a case (same maths as the Streamlit review page)."""

    def __init__(self, case):
        self.case = case
        self.a = _analysis(case)
        self.proc = procedures.resolve(case["procedure"])
        p = dict(config.DEFAULTS)
        self.times, self.m, self.intervals = timeline.build_intervals(self.a, **service.timeline_params(p))
        self.usage = timeline.usage_stats(self.intervals, self.a.duration, self.proc)
        self.metrics = timeline.case_metrics(self.intervals, self.a.duration)
        self.phases = timeline.phase_segments(self.a)
        self.flags = review_flags(self.intervals, self.a.duration, self.times, dense=self.a.dense, long_use_s=p["long_use_s"],
                                  switch_window_s=p["switch_window_s"], switch_count=int(p["switch_count"]),
                                  idle_gap_s=p["idle_gap_s"], instrument_names=self.proc.instrument_names)
        self.notes = db.list_notes(case["id"])
        self.clips = db.list_clips(case["id"])

    @property
    def facts(self) -> dict:
        return casecontext.build_facts(self.case, self.a, self.notes, self.clips, self.proc, self.phases, self.usage,
                                       self.flags, self.metrics)


def _both(fn) -> dict:
    return {"en": fn("en"), "ar": fn("ar")}


def _proc_json(proc) -> dict:
    return {
        "id": proc.id, "label": _both(proc.label),
        "instruments": [{"name": _both(lambda l, i=i: proc.instrument_label(i, l)), "color": proc.instrument_color(i)}
                        for i in range(proc.n_instruments)],
        "phases": [{"name": _both(lambda l, i=i: proc.phase_label(i, l)), "color": proc.phase_color(i)} for i in range(proc.n_phases)],
    }


def _seg_json(s: timeline.PhaseSegment) -> dict:
    return {"phase": s.phase, "start": round(s.start, 2), "end": round(s.end, 2), "conf": s.conf, "verified": s.verified,
            "uncertain": s.uncertain}


def _jpeg(im: Image.Image, q: int = 80) -> Response:
    buf = io.BytesIO()
    im.convert("RGB").save(buf, "JPEG", quality=q)
    return Response(buf.getvalue(), media_type="image/jpeg", headers={"Cache-Control": "private, max-age=60"})


def _frame_image(case, a: CaseAnalysis, t: float) -> Image.Image | None:
    if case["media_kind"] == "frames":
        f = timeline.frame_at(a, t)
        if f is not None and f.image:
            p = Path(case["media_path"]) / f.image
            if p.is_file():
                with Image.open(p) as im:
                    return im.convert("RGB")
        return None
    bgr = read_video_frame(Path(case["media_path"]), t, privacy=True)
    return Image.fromarray(bgr[:, :, ::-1]) if bgr is not None else None


def _playable(path: str) -> bool:
    """Browsers play H.264 (avc1); MPEG-4 part 2 (FMP4/mp4v) does not, so those are shown as server-side frames."""
    try:
        import cv2
        cap = cv2.VideoCapture(path)
        f = int(cap.get(cv2.CAP_PROP_FOURCC))
        cap.release()
        return bytes([f & 255, (f >> 8) & 255, (f >> 16) & 255, (f >> 24) & 255]).lower() in (b"avc1", b"h264", b"x264")
    except Exception:
        return False


# ------------------------------------------------------------------ dashboard / library
def _card(case) -> dict:
    a = _analysis(case)
    proc = procedures.resolve(case["procedure"])
    segs = timeline.phase_segments(a)
    stats = json.loads(case["stats_json"] or "{}")
    return {
        "id": case["id"], "title": case["title"], "source": case["source"], "duration": case["duration"], "tags": case["tags"],
        "procedure": {"id": proc.id, "label": _both(proc.label)}, "trainee_id": case["trainee_id"],
        "strip": [{"w": round(max(1.0, s.end - s.start), 1), "color": proc.phase_color(s.phase), "verified": s.verified} for s in segs],
        "usage": stats.get("usage", {}), "instruments_used": stats.get("instruments_used"),
        "phased": bool(stats.get("phases")),
    }


@app.get("/api/dashboard")
def dashboard(user: dict = Depends(current_user)) -> dict:
    cs = db.list_cases(user)
    ready = [p for p in procedures.load_all() if p.status == "ready"]
    usage: dict[str, float] = {}
    for c in cs:
        for k, v in json.loads(c["stats_json"] or "{}").get("usage", {}).items():
            usage[k] = usage.get(k, 0.0) + float(v)
    default = procedures.get(procedures.DEFAULT_ID)
    # phase time across the library (per procedure), temporal series per case, and real model figures where they exist
    phase_totals: dict[str, list[float]] = {}
    series = []
    for c in sorted(cs, key=lambda x: x["id"]):
        proc = procedures.resolve(c["procedure"])
        tot = phase_totals.setdefault(proc.id, [0.0] * proc.n_phases)
        for sg in timeline.phase_segments(_analysis(c)):
            if sg.phase < proc.n_phases:
                tot[sg.phase] += max(0.0, sg.end - sg.start)
        st = json.loads(c["stats_json"] or "{}")
        series.append({"id": c["id"], "duration": c["duration"], "entries_per_min": st.get("entries_per_min"),
                       "instrument_entries": st.get("instrument_entries")})
    acc = None
    if config.PHASE_METRICS_PATH.exists():
        acc = json.loads(config.PHASE_METRICS_PATH.read_text(encoding="utf-8")).get("clean", {}).get("mean_accuracy")
    det_metrics = None
    if config.METRICS_PATH.exists():
        try:
            det_metrics = json.loads(config.METRICS_PATH.read_text(encoding="utf-8"))
        except ValueError:
            det_metrics = None
    return {
        "phase_defs": {pid: _proc_json(procedures.get(pid))["phases"] for pid in phase_totals if procedures.get(pid)},
        "phase_totals": phase_totals, "series": series, "phase_accuracy": acc, "detector_metrics": det_metrics,
        "detector": {"weights": config.WEIGHTS_PATH.name, "available": config.WEIGHTS_PATH.exists(), "classes": default.instrument_names},
        "kpis": {"cases": len(cs), "total_duration": sum(c["duration"] for c in cs),
                 "phased": sum(1 for c in cs if json.loads(c["stats_json"] or "{}").get("phases")),
                 "procedures_ready": len(ready), "procedures_total": len(procedures.load_all())},
        "recent": [_card(c) for c in cs[:6]],
        "usage": [{"name": _both(lambda l, i=i: default.instrument_label(i, l)), "color": default.instrument_color(i),
                   "seconds": usage.get(n, 0.0)} for i, n in enumerate(default.instrument_names)],
    }


@app.get("/api/cases")
def cases(user: dict = Depends(current_user)) -> list[dict]:
    users = {u["id"]: u["display_name"] for u in auth.list_users()}
    out = []
    for c in db.list_cases(user):
        d = _card(c)
        d["trainee"] = users.get(c["trainee_id"])
        out.append(d)
    return out


@lru_cache(maxsize=64)
def _thumb_bytes(case_id: int, mtime: float) -> bytes | None:
    case = db.get_case(case_id)
    a = _analysis(case)
    if not a.frames:
        return None
    mid = sorted(a.frames, key=lambda f: f.t)[len(a.frames) // 2]
    im = _frame_image(case, a, mid.t)
    if im is None:
        return None
    im.thumbnail((440, 260))
    buf = io.BytesIO()
    im.filter(ImageFilter.GaussianBlur(radius=16)).save(buf, "JPEG", quality=72)
    return buf.getvalue()


@app.get("/api/cases/{case_id}/thumb")
def thumb(case_id: int, user: dict = Depends(current_user)) -> Response:
    case = _get_case(case_id, user)
    b = _thumb_bytes(case_id, Path(case["analysis_path"]).stat().st_mtime)
    if b is None:
        raise HTTPException(404)
    return Response(b, media_type="image/jpeg", headers={"Cache-Control": "private, max-age=300"})   # always blurred


# ------------------------------------------------------------------ review
def _nan(v):
    return None if isinstance(v, float) and v != v else v


@app.get("/api/cases/{case_id}")
def case_detail(case_id: int, user: dict = Depends(current_user)) -> dict:
    case = _get_case(case_id, user)
    db.log(user["id"], "view_case", case_id)
    c = Ctx(case)
    a = c.a
    frames = [{"t": round(f.t, 2), "phase": f.phase,
               "boxes": [[b.instrument, round(b.x, 4), round(b.y, 4), round(b.w, 4), round(b.h, 4), round(b.conf, 2)] for b in f.boxes
                         if b.instrument < c.proc.n_instruments]} for f in sorted(a.frames, key=lambda f: f.t)]
    media = None
    if case["media_kind"] == "video" and Path(case["media_path"]).is_file():
        media = {"kind": "video", "playable": _playable(case["media_path"])}
    elif case["media_kind"] == "frames":
        media = {"kind": "frames", "playable": False}
    return {
        "case": {"id": case["id"], "title": case["title"], "source": case["source"], "media_kind": case["media_kind"], "tags": case["tags"],
                 "trainee_id": case["trainee_id"], "owner_id": case["owner_id"]},
        "procedure": _proc_json(c.proc), "duration": a.duration, "dense": a.dense, "media": media,
        "complete_operation": bool(a.params.get("complete_operation", False)),
        "phase_source": a.params.get("phase_source", "annotation" if c.phases else None),
        "frames": frames,
        "intervals": [{"i": iv.instrument, "start": round(iv.start, 2), "end": round(iv.end, 2)} for iv in c.intervals],
        "phases": [_seg_json(s) for s in c.phases],
        "usage": [{k: _nan(v) for k, v in row.items()} for row in c.usage.to_dict("records")],
        "metrics": c.metrics,
        "notes": [{"id": n["id"], "t": n["t_seconds"], "text": n["text"], "author": n["display_name"], "author_id": n["author_id"]} for n in c.notes],
        "can_ai": user["role"] in DOCTORS,
        "can_manage": user["role"] in DOCTORS or user["id"] == case["owner_id"],
    }


@app.get("/api/cases/{case_id}/analytics")
def analytics(case_id: int, user: dict = Depends(current_user)) -> dict:
    """Operation-phase analytics: time per phase (vs. the library median), tool-by-phase heatmap, per-phase table."""
    import numpy as np
    case = _get_case(case_id, user)
    c = Ctx(case)
    nph, ni = c.proc.n_phases, c.proc.n_instruments
    dur = np.zeros(nph)
    for s in c.phases:
        if s.phase < nph:
            dur[s.phase] += max(0.0, s.end - s.start)
    ref = []
    for other in db.list_cases(user):
        if other["id"] == case_id or procedures.resolve(other["procedure"]).id != c.proc.id:
            continue
        d2 = np.zeros(nph)
        for s in timeline.phase_segments(_analysis(other)):
            if s.phase < nph:
                d2[s.phase] += max(0.0, s.end - s.start)
        if d2.sum() > 0:
            ref.append(d2)
    frames = sorted(c.a.frames, key=lambda f: f.t)
    phase_of = np.array([f.phase if f.phase is not None else -1 for f in frames])
    heat = np.zeros((ni, nph))
    if ni and len(c.m) == len(frames):
        for ph in range(nph):
            sel = phase_of == ph
            if sel.any():
                heat[:, ph] = c.m[sel].mean(axis=0) * 100
    rows = []
    t_arr = np.array([f.t for f in frames]) if frames else np.zeros(0)
    for s in c.phases:
        sel = (t_arr >= s.start) & (t_arr < s.end) if len(t_arr) == len(c.m) else np.zeros(len(c.m), bool)
        main = []
        if ni and sel.any():
            share = c.m[sel].mean(axis=0)
            main = [int(i) for i in np.argsort(-share)[:2] if share[i] > 0]
        rows.append({**_seg_json(s), "main_instruments": main})
    return {"time_per_phase": [round(float(x), 1) for x in dur],
            "library_median": [round(float(x), 1) for x in np.median(ref, axis=0)] if len(ref) >= 3 else None, "library_n": len(ref),
            "heatmap": [[round(float(x), 1) for x in row] for row in heat], "rows": rows}


@app.get("/api/cases/{case_id}/video")
def video(case_id: int, user: dict = Depends(current_user)) -> FileResponse:
    case = _get_case(case_id, user)
    p = Path(case["media_path"])
    if case["media_kind"] != "video" or not p.is_file():
        raise HTTPException(404)
    return FileResponse(p, media_type="video/mp4")


@app.get("/api/cases/{case_id}/frame")
def frame(case_id: int, t: float = 0.0, user: dict = Depends(current_user)) -> Response:
    case = _get_case(case_id, user)
    im = _frame_image(case, _analysis(case), t)
    if im is None:
        raise HTTPException(404, "frame not available")
    im.thumbnail((960, 540))
    return _jpeg(im)


class NoteIn(BaseModel):
    t: float
    text: str


@app.post("/api/cases/{case_id}/notes")
def add_note(case_id: int, body: NoteIn, user: dict = Depends(current_user)) -> dict:
    _get_case(case_id, user)
    if not body.text.strip():
        raise HTTPException(422, "empty note")
    nid = db.add_note(case_id, user["id"], body.t, body.text[:4000])
    db.log(user["id"], "add_note", case_id)
    return {"id": nid}


@app.delete("/api/cases/{case_id}/notes/{note_id}")
def del_note(case_id: int, note_id: int, user: dict = Depends(current_user)) -> dict:
    _get_case(case_id, user)
    db.delete_note(note_id, user)
    return {"ok": True}


@app.get("/api/cases/{case_id}/export.pdf")
def export_pdf(case_id: int, lang: str = "en", user: dict = Depends(current_user)) -> Response:
    case = _get_case(case_id, user)
    c = Ctx(case)
    with tempfile.TemporaryDirectory() as d:
        out = Path(d) / "report.pdf"
        report.build_report(out, case=dict(case), duration=c.a.duration, intervals=c.intervals, usage_df=c.usage, phases=c.phases,
                            flags=c.flags, notes=c.notes, clips=c.clips, metrics=c.metrics, dense=c.a.dense, lang=lang, proc=c.proc)
        data = out.read_bytes()
    db.log(user["id"], "export_pdf", case_id)
    return Response(data, media_type="application/pdf", headers={"Content-Disposition": f'attachment; filename="case{case_id}_report.pdf"'})


# ------------------------------------------------------------------ AI report
def _need_doctor(user: dict) -> None:
    if user["role"] not in DOCTORS:
        raise HTTPException(403, "AI tools are for instructors and admins")


def _reviewer(row) -> str:
    if row is None or row["status"] != "final" or not row["reviewed_by"]:
        return ""
    u = auth.get_user(row["reviewed_by"])
    return u["display_name"] if u else ""


def _report_json(row, user: dict) -> dict | None:
    if row is None or (user["role"] not in DOCTORS and row["status"] != "final"):
        return None
    return {"id": row["id"], "status": row["status"], "content": json.loads(row["content_json"]), "model": row["model"],
            "tokens_in": row["tokens_in"], "tokens_out": row["tokens_out"], "reviewer": _reviewer(row), "updated_at": row["updated_at"]}


@app.get("/api/cases/{case_id}/report")
def get_report(case_id: int, user: dict = Depends(current_user)) -> dict:
    _get_case(case_id, user)
    ok, why = llm.status()
    return {"report": _report_json(db.latest_report(case_id), user), "ai": {"ok": ok, "reason": why}}


class GenIn(BaseModel):
    lang: str = "en"
    with_ai: bool = True


@app.post("/api/cases/{case_id}/report/generate")
def generate_report(case_id: int, body: GenIn, user: dict = Depends(current_user)) -> dict:
    _need_doctor(user)
    case = _get_case(case_id, user)
    c = Ctx(case)
    row = db.latest_report(case_id)
    if row is not None and row["status"] == "final":
        raise HTTPException(409, "report is final; reopen it first")
    ai, res = None, None
    if body.with_ai:
        try:
            ai, res = case_report.generate_ai(c.facts, body.lang)
        except llm.LLMError as e:
            raise HTTPException(502, str(e))
    if row is None:
        content = case_report.new_content(c.notes, c.phases, c.a.duration, body.lang)
        if ai:
            content["ai"] = ai
        db.add_report(case_id, content, user["id"], model=res.model if res else "", tokens_in=res.tokens_in if res else 0,
                      tokens_out=res.tokens_out if res else 0)
    else:                                        # regenerate: keeps the doctor's comments and frames
        content = json.loads(row["content_json"])
        content["ai"] = ai
        db.update_report(row["id"], content)
    db.log(user["id"], "report_generate" if ai else "report_create", case_id, f"model={res.model if res else '-'}")
    return _report_json(db.latest_report(case_id), user) or {}


class SaveIn(BaseModel):
    content: dict
    approve: bool = False
    confirmed: bool = False


@app.put("/api/cases/{case_id}/report")
def save_report(case_id: int, body: SaveIn, user: dict = Depends(current_user)) -> dict:
    _need_doctor(user)
    _get_case(case_id, user)
    row = db.latest_report(case_id)
    if row is None:
        raise HTTPException(404)
    if row["status"] == "final":
        raise HTTPException(409, "report is final; reopen it first")
    if body.approve and not body.confirmed:
        raise HTTPException(422, "confirm that you reviewed the report")
    old = json.loads(row["content_json"])
    new = {**old, "doctor_comments": str(body.content.get("doctor_comments", ""))[:8000],
           "frames": body.content.get("frames", old.get("frames", []))}
    if old.get("ai") and body.content.get("ai"):         # AI text stays AI-labelled; edits are flagged
        ai = body.content["ai"]
        valid = {"summary": str(ai.get("summary", ""))[:6000], "limitations": str(ai.get("limitations", ""))[:3000],
                 "observations": [{"text": str(o.get("text", ""))[:1500], "evidence": [str(e) for e in o.get("evidence", [])]}
                                  for o in ai.get("observations", []) if str(o.get("text", "")).strip()]}
        old_ai = old["ai"]
        edited = old_ai.get("edited") or any(valid[k] != old_ai.get(k) for k in valid)
        new["ai"] = {**old_ai, **valid, "edited": bool(edited)}
    if body.approve:
        db.update_report(row["id"], new, status="final", reviewed_by=user["id"])
        db.log(user["id"], "report_approve", case_id)
    else:
        db.update_report(row["id"], new)
        db.log(user["id"], "report_edit", case_id)
    return _report_json(db.latest_report(case_id), user) or {}


@app.post("/api/cases/{case_id}/report/reopen")
def reopen_report(case_id: int, user: dict = Depends(current_user)) -> dict:
    _need_doctor(user)
    _get_case(case_id, user)
    row = db.latest_report(case_id)
    if row is None:
        raise HTTPException(404)
    db.update_report(row["id"], json.loads(row["content_json"]), status="draft", reviewed_by=None)
    db.log(user["id"], "report_reopen", case_id)
    return _report_json(db.latest_report(case_id), user) or {}


@app.get("/api/cases/{case_id}/report/frame")
def report_frame(case_id: int, t: float, user: dict = Depends(current_user)) -> Response:
    case = _get_case(case_id, user)
    im = _frame_image(case, _analysis(case), t)
    if im is None:
        raise HTTPException(404)
    im.thumbnail((900, 520))
    return _jpeg(im, 82)


@app.get("/api/cases/{case_id}/report.pdf")
def report_pdf(case_id: int, lang: str = "en", user: dict = Depends(current_user)) -> Response:
    case = _get_case(case_id, user)
    row = db.latest_report(case_id)
    if row is None or (user["role"] not in DOCTORS and row["status"] != "final"):
        raise HTTPException(404)
    c = Ctx(case)
    content = json.loads(row["content_json"])
    frames = []
    for fr in content.get("frames", []):
        im = _frame_image(case, c.a, fr["t"])
        if im is not None:
            im.thumbnail((900, 520))
            buf = io.BytesIO()
            im.save(buf, "JPEG", quality=82)
            frames.append((fr["t"], buf.getvalue(), fr["caption"]))
    with tempfile.TemporaryDirectory() as d:
        out = Path(d) / "r.pdf"
        used = case_report.build_pdf(out, case=dict(case), facts=c.facts, notes=c.notes, content=content, frames=frames,
                                     status=row["status"], reviewer=_reviewer(row), lang=lang)
        data = out.read_bytes()
    db.log(user["id"], "report_export_pdf", case_id)
    return Response(data, media_type="application/pdf",
                    headers={"X-PDF-Lang": used, "Content-Disposition": f'attachment; filename="case{case_id}_ai_report.pdf"'})


# ------------------------------------------------------------------ related literature
class RefsIn(BaseModel):
    custom: str = ""
    refresh: bool = True


def _refs_json(case_id: int) -> dict:
    cached = db.load_refs(case_id)
    items = cached[0] if cached else None
    for d in items or []:
        d["summary"] = references.short_summary(references.Reference.from_dict(d))
    return {"items": items, "fetched_at": cached[1] if cached else None}


@app.get("/api/cases/{case_id}/refs")
def get_refs(case_id: int, user: dict = Depends(current_user)) -> dict:
    _get_case(case_id, user)
    return _refs_json(case_id)


@app.post("/api/cases/{case_id}/refs/search")
def search_refs(case_id: int, body: RefsIn, user: dict = Depends(current_user)) -> dict:
    _need_doctor(user)
    case = _get_case(case_id, user)
    c = Ctx(case)
    f = c.facts
    top_phases = [p["name"] for p in sorted(f["phases"], key=lambda p: p["start_s"] - p["end_s"])]
    top_instr = [i["name"] for i in sorted(f["instruments"], key=lambda i: -i["active_s"]) if i["active_s"] > 0]
    qs = references.build_queries(c.proc.id, c.proc.label("en"), top_phases, top_instr) if body.refresh else []
    custom = deid.deidentify(body.custom, deid.user_names()).strip()
    if custom:
        qs = [(custom, custom)] + qs
    terms = [p["name"] for p in f["phases"]][:4] + [i["name"] for i in f["instruments"] if i["active_s"] > 0][:4]
    try:
        found = references.retrieve(qs, terms)
    except requests.RequestException as e:
        raise HTTPException(502, f"PubMed could not be reached: {str(e)[:150]}")
    old = [references.Reference.from_dict(d) for d in ((db.load_refs(case_id) or ([], 0))[0] if custom else [])]
    merged = {r.pmid: r for r in old + found}
    db.save_refs(case_id, [r.to_dict() for r in merged.values()])
    db.log(user["id"], "refs_search", case_id, f"n={len(merged)}")
    return _refs_json(case_id)


# ------------------------------------------------------------------ research assistant
class ChatIn(BaseModel):
    question: str


def _chat_json(case_id: int, user: dict) -> list[dict]:
    return [{"id": m["id"], "role": m["role"], "content": m["content"], "sources": json.loads(m["sources_json"] or "[]"),
             "tokens_in": m["tokens_in"], "tokens_out": m["tokens_out"]} for m in db.list_chat(case_id, user["id"])]


@app.get("/api/cases/{case_id}/chat")
def get_chat(case_id: int, user: dict = Depends(current_user)) -> dict:
    _need_doctor(user)
    _get_case(case_id, user)
    refs = (db.load_refs(case_id) or ([], 0))[0]
    return {"messages": _chat_json(case_id, user), "has_refs": bool(refs)}


@app.post("/api/cases/{case_id}/chat")
def ask(case_id: int, body: ChatIn, user: dict = Depends(current_user)) -> dict:
    _need_doctor(user)
    case = _get_case(case_id, user)
    q = body.question.strip()[:2000]
    if not q:
        raise HTTPException(422, "empty question")
    ok, _ = llm.status()
    if not ok:
        raise HTTPException(503, "external AI is not enabled on this server")
    c = Ctx(case)
    refs = (db.load_refs(case_id) or ([], 0))[0]
    hist = [{"role": m["role"], "content": m["content"]} for m in db.list_chat(case_id, user["id"])]
    db.add_chat(case_id, user["id"], "user", q)
    try:
        r = assistant.ask(c.facts, refs, hist, q)
    except llm.LLMError as e:
        db.add_chat(case_id, user["id"], "assistant", f"⚠️ {e}")
    else:
        db.add_chat(case_id, user["id"], "assistant", r["text"], r["sources"], r["tokens_in"], r["tokens_out"])
        db.log(user["id"], "assistant_ask", case_id, f"in={r['tokens_in']} out={r['tokens_out']}")
    return {"messages": _chat_json(case_id, user)}


@app.delete("/api/cases/{case_id}/chat")
def clear_chat(case_id: int, user: dict = Depends(current_user)) -> dict:
    _need_doctor(user)
    _get_case(case_id, user)
    db.clear_chat(case_id, user["id"])
    return {"ok": True}


@app.exception_handler(HTTPException)
async def _http_err(_: Request, exc: HTTPException) -> JSONResponse:
    return JSONResponse({"detail": exc.detail}, status_code=exc.status_code)


from .live import router as _live_router  # noqa: E402  (registered last: it imports helpers defined above)

app.include_router(_live_router)
