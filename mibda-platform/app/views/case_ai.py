"""Case tabs for the AI features: report (generate, edit, approve, PDF), related literature, research assistant."""
from __future__ import annotations

import io
import json
import tempfile
import time
from pathlib import Path

import requests
import streamlit as st

from app import ui
from app.ui import T
from or_intelligence import assistant, case_report, casecontext, db, llm, references
from or_intelligence.analysis import read_video_frame
from or_intelligence.timeline import fmt_time, frame_at

DOCTOR_ROLES = ("admin", "instructor")


class Ctx:
    """Everything the three tabs need about the open case (built once by the review page)."""

    def __init__(self, case, analysis, proc, usage, phases, flags, metrics, user, tkey):
        self.case, self.a, self.proc, self.user, self.tkey = case, analysis, proc, user, tkey
        self.id = case["id"]
        self.notes = db.list_notes(self.id)
        self.clips = db.list_clips(self.id)
        self.facts = casecontext.build_facts(case, analysis, self.notes, self.clips, proc, phases, usage, flags, metrics)
        self.phases = phases


def _llm_banner() -> bool:
    ok, why = llm.status()
    if not ok:
        st.warning(T({"not_approved": "ai_off_not_approved", "no_key": "ai_off_no_key", "no_package": "ai_off_no_package"}[why]))
    else:
        st.caption("🔒 " + T("ai_privacy_note"))
    return ok


def frame_bytes(c: Ctx, t: float) -> bytes | None:
    """The frame at time t as JPEG with detection boxes. Faces are blurred; this image stays on the server (PDF/preview)."""
    f = frame_at(c.a, t)
    img = None
    if c.case["media_kind"] == "frames":
        if f is not None and f.image:
            p = Path(c.case["media_path"]) / f.image
            if p.is_file():
                img = ui.load_image(str(p))
    else:
        bgr = read_video_frame(Path(c.case["media_path"]), t, privacy=True)
        if bgr is not None:
            img = ui.bgr_to_pil(bgr)
    if img is None:
        return None
    if f is not None and f.boxes:
        img = ui.draw_boxes(img, f.boxes, proc=c.proc)
    img = img.copy()
    img.thumbnail((900, 520))
    buf = io.BytesIO()
    img.save(buf, "JPEG", quality=82)
    return buf.getvalue()


# ---------------------------------------------------------------- report
def _store(c: Ctx, rid: int, content: dict, **kw) -> None:
    db.update_report(rid, content, **kw)


def report_tab(c: Ctx) -> None:
    user = c.user
    row = db.latest_report(c.id)
    is_doc = user["role"] in DOCTOR_ROLES
    if not is_doc:                                   # trainees: only the approved report, read-only PDF
        if row is None or row["status"] != "final":
            st.info(T("rep_trainee_none"))
            return
    else:
        st.info(T("ai_privacy_note"))
    ok, _ = llm.status()
    if is_doc and not ok:
        _llm_banner()

    if row is None:
        st.write(T("rep_none"))
        b1, b2, _ = st.columns([1.3, 1.3, 2])
        if b1.button(T("rep_generate_ai"), type="primary", disabled=not ok, key=f"gen_{c.id}"):
            _generate(c, None)
        if b2.button(T("rep_draft_no_ai"), key=f"nogen_{c.id}"):
            content = case_report.new_content(c.notes, c.phases, c.a.duration, ui.lang())
            db.add_report(c.id, content, user["id"])
            db.log(user["id"], "report_create", c.id, "no AI")
            st.rerun()
        return

    rid, content, final = row["id"], json.loads(row["content_json"]), row["status"] == "final"
    reviewer = ""
    if final and row["reviewed_by"]:
        from or_intelligence import auth
        reviewer = next((u["display_name"] for u in auth.list_users() if u["id"] == row["reviewed_by"]), "")
    st.markdown(f"**{T('rep_status_final', name=reviewer) if final else T('rep_status_draft')}**")
    if row["tokens_in"] or row["tokens_out"]:
        st.caption(T("rep_tokens", i=row["tokens_in"], o=row["tokens_out"]))

    # --- system analysis + doctor notes (read-only here: they come from the platform and from the notes tab)
    with st.expander(T("rep_analysis_title"), expanded=False):
        f = c.facts
        for p in f["phases"]:
            st.write(f"{p['name']}: {fmt_time(p['start_s'])} - {fmt_time(p['end_s'])}")
        for i in f["instruments"]:
            st.write(f"{i['name']}: {i['active_s']:.0f} s ({i['pct_of_case']}%)")
        if not f["phases"] and not f["instruments"]:
            st.write(T("none"))
    with st.expander(T("rep_notes_title"), expanded=bool(c.notes)):
        for n in c.notes:
            st.write(f"`{fmt_time(n['t_seconds'])}` **{n['display_name']}**: {n['text']}")
        if not c.notes:
            st.write(T("none"))

    ai = content.get("ai")
    key = f"{rid}_{row['updated_at']}"
    with st.form(f"repform_{key}"):
        comments = st.text_area(T("rep_doctor_comments"), value=content.get("doctor_comments", ""), height=100, disabled=final)
        st.markdown(f"##### 🤖 {T('rep_ai_section')}")
        new_ai = ai
        if ai:
            st.caption(T("rep_ai_label", model=ai.get("model", "")))
            summ = st.text_area(T("rep_summary"), value=ai.get("summary", ""), height=120, disabled=final)
            obs_new = []
            st.markdown(f"**{T('rep_observations')}**")
            for k, o in enumerate(ai.get("observations", [])):
                cc = st.columns([8, 1])
                txt = cc[0].text_input(f"{T('rep_evidence')}: {', '.join(o['evidence'])}", value=o["text"], key=f"obs_{key}_{k}", disabled=final)
                drop = cc[1].checkbox(T("rep_remove"), key=f"obsx_{key}_{k}", disabled=final)
                if not drop and txt.strip():
                    obs_new.append({"text": txt.strip(), "evidence": o["evidence"]})
            lim = st.text_area(T("rep_limitations"), value=ai.get("limitations", ""), height=70, disabled=final)
            edited = ai.get("edited") or summ != ai.get("summary") or lim != ai.get("limitations") or obs_new != ai.get("observations")
            new_ai = {**ai, "summary": summ.strip(), "observations": obs_new, "limitations": lim.strip(), "edited": bool(edited)}
        else:
            st.caption(T("rep_no_ai_yet"))

        st.markdown(f"##### 🖼️ {T('rep_frames')}")
        keep = []
        cols = st.columns(3)
        for k, fr in enumerate(content.get("frames", [])):
            with cols[k % 3]:
                b = frame_bytes(c, fr["t"])
                if b:
                    st.image(b, caption=f"{fmt_time(fr['t'])}  {fr['caption']}", width="stretch")
                else:
                    st.caption(f"{fmt_time(fr['t'])}: {T('frame_missing')}")
                if not st.checkbox(T("rep_remove"), key=f"frx_{key}_{k}", disabled=final):
                    keep.append(fr)
        agree = False if final else st.checkbox(T("rep_approve_check"), key=f"agree_{key}")
        s1, s2, _ = st.columns([1, 1.6, 2])
        save = s1.form_submit_button(T("rep_save"), disabled=final)
        approve = s2.form_submit_button(T("rep_approve"), type="primary", disabled=final)
    if (save or approve) and not final:
        if approve and not agree:
            st.error(T("rep_need_review"))
        else:
            new = {**content, "doctor_comments": comments.strip(), "ai": new_ai, "frames": keep}
            if approve:
                db.update_report(rid, new, status="final", reviewed_by=user["id"])
                db.log(user["id"], "report_approve", c.id)
            else:
                db.update_report(rid, new)
                db.log(user["id"], "report_edit", c.id)
            st.rerun()

    b = st.columns([1.5, 1.5, 1.5, 2])
    if is_doc and not final:
        if b[0].button(T("rep_regenerate"), disabled=not ok, key=f"regen_{rid}"):
            _generate(c, (rid, content))
        tcur = st.session_state.get(c.tkey, 0)
        if b[1].button(T("rep_add_frame", t=fmt_time(tcur)), key=f"addfr_{rid}"):
            content["frames"] = sorted(content.get("frames", []) + [{"t": round(float(tcur), 1), "caption": "Selected by doctor"}], key=lambda x: x["t"])
            db.update_report(rid, content)
            st.rerun()
    if is_doc and final and b[0].button(T("rep_reopen"), key=f"reopen_{rid}"):
        db.update_report(rid, content, status="draft", reviewed_by=None)
        db.log(user["id"], "report_reopen", c.id)
        st.rerun()

    pkey = f"repdf_{rid}_{row['updated_at']}_{ui.lang()}"
    if b[2].button(T("rep_export"), key=f"pdfb_{rid}"):
        frames = [(fr["t"], fb, fr["caption"]) for fr in content.get("frames", []) if (fb := frame_bytes(c, fr["t"]))]
        with tempfile.TemporaryDirectory() as d:
            out = Path(d) / "report.pdf"
            used = case_report.build_pdf(out, case=dict(c.case), facts=c.facts, notes=c.notes, content=content, frames=frames,
                                         status=row["status"], reviewer=reviewer, lang=ui.lang())
            st.session_state[pkey] = (out.read_bytes(), used)
        db.log(user["id"], "report_export_pdf", c.id)
    if pkey in st.session_state:
        data, used = st.session_state[pkey]
        if used != ui.lang():
            st.warning(T("pdf_lang_fallback"))
        st.download_button(T("rep_download"), data, file_name=f"case{c.id}_ai_report.pdf", mime="application/pdf", key=f"dl_{pkey}")


def _generate(c: Ctx, existing: tuple[int, dict] | None) -> None:
    """Call Claude for the AI part. A new report keeps nothing; a regeneration keeps the doctor's comments and frames."""
    with st.spinner(T("rep_generating")):
        try:
            ai, res = case_report.generate_ai(c.facts, ui.lang())
        except llm.LLMError as e:
            st.error(str(e))
            return
    if existing:
        rid, content = existing
        content["ai"] = ai
        db.update_report(rid, content)
    else:
        content = case_report.new_content(c.notes, c.phases, c.a.duration, ui.lang())
        content["ai"] = ai
        db.add_report(c.id, content, c.user["id"], model=res.model, tokens_in=res.tokens_in, tokens_out=res.tokens_out)
    db.log(c.user["id"], "report_generate", c.id, f"model={res.model} in={res.tokens_in} out={res.tokens_out}")
    st.rerun()


# ---------------------------------------------------------------- resources
def _case_terms(c: Ctx) -> list[str]:
    return [p["name"] for p in c.facts["phases"]][:4] + [i["name"] for i in c.facts["instruments"] if i["active_s"] > 0][:4]


def _queries(c: Ctx) -> list[tuple[str, str]]:
    top_phases = [p["name"] for p in sorted(c.facts["phases"], key=lambda p: p["start_s"] - p["end_s"])]
    top_instr = [i["name"] for i in sorted(c.facts["instruments"], key=lambda i: -i["active_s"]) if i["active_s"] > 0]
    return references.build_queries(c.proc.id, c.proc.label("en"), top_phases, top_instr)


def resources_tab(c: Ctx) -> None:
    st.caption(T("res_source_note"))
    cached = db.load_refs(c.id)
    cols = st.columns([1.4, 1, 3])
    go = cols[0].button(T("res_refresh") if cached else T("res_find"), type="primary", key=f"refs_{c.id}")
    custom = st.text_input(T("res_custom"), key=f"refq_{c.id}")
    go_custom = st.button(T("res_custom_btn"), key=f"refqb_{c.id}", disabled=not custom.strip())
    if go or go_custom:
        from or_intelligence import deid
        qs = _queries(c) if go else []
        if go_custom:
            qs = [(deid.deidentify(custom, deid.user_names()), deid.deidentify(custom, deid.user_names()))] + qs
        with st.spinner(T("res_searching")):
            try:
                found = references.retrieve(qs, _case_terms(c))
            except requests.RequestException as e:
                st.error(T("res_error", e=str(e)[:150]))
                return
        old = [references.Reference.from_dict(d) for d in (cached[0] if (cached and go_custom) else [])]
        merged = {r.pmid: r for r in old + found}
        db.save_refs(c.id, [r.to_dict() for r in merged.values()])
        db.log(c.user["id"], "refs_search", c.id, f"n={len(merged)}")
        st.rerun()
    cached = db.load_refs(c.id)
    if not cached:
        st.info(T("res_none"))
        return
    items, ts = cached
    if not items:
        st.info(T("res_empty"))
        return
    st.caption(T("res_fetched", n=len(items), d=time.strftime("%Y-%m-%d %H:%M", time.localtime(ts))))
    cats = sorted({i["category"] for i in items})
    show = st.multiselect(T("res_filter"), cats, default=cats, format_func=lambda k: T("res_cat_" + k), key=f"refcat_{c.id}")
    for d in items:
        if d["category"] not in show:
            continue
        r = references.Reference.from_dict(d)
        with st.container(border=True):
            st.markdown(f"**[{r.title}]({r.url})**")
            au = ", ".join(r.authors[:5]) + (" et al." if len(r.authors) > 5 else "")
            st.caption(f"{au}  ·  {r.journal}  ·  {r.date}  ·  PMID {r.pmid}  ·  {T('res_cat_' + r.category)}")
            st.write(references.short_summary(r) or T("res_no_abstract"))
            rel = T("res_found_for", topic=r.topic) + ". " + (T("res_matched", terms=", ".join(r.matched)) if r.matched else T("res_no_match"))
            st.caption(f"**{T('res_relevance')}:** {rel}")
            st.markdown(f"[{T('res_open')}]({r.url})" + (f"  ·  [DOI](https://doi.org/{r.doi})" if r.doi else ""))


# ---------------------------------------------------------------- assistant
def _ask(c: Ctx, question: str) -> None:
    refs = (db.load_refs(c.id) or ([], 0))[0]
    hist = [{"role": m["role"], "content": m["content"]} for m in db.list_chat(c.id, c.user["id"])]
    db.add_chat(c.id, c.user["id"], "user", question)
    with st.spinner(T("chat_thinking")):
        try:
            r = assistant.ask(c.facts, refs, hist, question)
        except llm.LLMError as e:
            db.add_chat(c.id, c.user["id"], "assistant", f"⚠️ {e}")
            return
    db.add_chat(c.id, c.user["id"], "assistant", r["text"], r["sources"], r["tokens_in"], r["tokens_out"])
    db.log(c.user["id"], "assistant_ask", c.id, f"in={r['tokens_in']} out={r['tokens_out']}")


def _pick(key: str, text: str) -> None:
    st.session_state[key] = text


def assistant_tab(c: Ctx) -> None:
    if c.user["role"] not in DOCTOR_ROLES:
        st.info(T("ai_doctors_only"))
        return
    ok = _llm_banner()
    st.caption(T("chat_disclaimer"))
    if not (db.load_refs(c.id) or ([], 0))[0]:
        st.caption(T("chat_no_refs"))
    qkey = f"pending_q_{c.id}"
    sc = st.columns(4)
    for k, col in enumerate(sc, 1):
        col.button(T(f"chat_s{k}"), key=f"sug{k}_{c.id}", disabled=not ok, width="stretch", on_click=_pick, args=(qkey, T(f"chat_s{k}")))
    q = st.session_state.pop(qkey, None)
    typed = st.chat_input(T("chat_input"), key=f"chat_in_{c.id}", disabled=not ok)
    question = typed or q
    if question and ok:
        _ask(c, question.strip())
    msgs = db.list_chat(c.id, c.user["id"])
    for m in msgs:
        with st.chat_message(m["role"]):
            st.markdown(m["content"])
            if m["role"] == "assistant":
                src = json.loads(m["sources_json"])
                if src:
                    with st.expander(T("chat_sources")):
                        for s in src:
                            st.markdown(f"**[{s['label']}]** {s['text']}")
                elif not m["content"].startswith("⚠️"):
                    st.caption(T("chat_uncited"))
                if m["tokens_in"]:
                    st.caption(T("chat_tokens", i=m["tokens_in"], o=m["tokens_out"]))
    if msgs and st.button(T("chat_clear"), key=f"chat_clr_{c.id}"):
        db.clear_chat(c.id, c.user["id"])
        st.rerun()
