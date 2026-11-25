"""AI features: de-identification, PubMed parsing, grounded assistant, report draft + PDF, privacy gate."""
import json

import pytest
from PIL import Image

from conftest import make_analysis
from or_intelligence import assistant, auth, case_report, casecontext, db, deid, llm, procedures, references, service, timeline

PUBMED_XML = """<PubmedArticleSet><PubmedArticle><MedlineCitation><PMID>111</PMID><Article>
<Journal><Title>Surg Endosc</Title><JournalIssue><PubDate><Year>2023</Year><Month>May</Month></PubDate></JournalIssue></Journal>
<ArticleTitle>Critical view of safety in laparoscopic cholecystectomy.</ArticleTitle>
<Abstract><AbstractText>Clipping and Calot triangle dissection were studied.</AbstractText></Abstract>
<AuthorList><Author><LastName>Smith</LastName><Initials>J</Initials></Author><Author><LastName>Lee</LastName><Initials>K</Initials></Author></AuthorList>
<PublicationTypeList><PublicationType>Practice Guideline</PublicationType></PublicationTypeList></Article></MedlineCitation>
<PubmedData><ArticleIdList><ArticleId IdType="doi">10.1/abc</ArticleId></ArticleIdList></PubmedData></PubmedArticle></PubmedArticleSet>"""


def _case(tmp_platform):
    uid = auth.create_user("doc", "pw12345678", "instructor", "Dr. Amal Zahrani")
    a = make_analysis({0: [(10, 60)], 4: [(30, 40)]}, duration=100)
    path = service._store(a, "t")
    cid = db.add_case(title="Mohammed Ali MRN 4455667", media_kind="frames", media_path=str(tmp_platform), analysis_path=str(path),
                      source="model", owner_id=uid, duration=100, n_frames=len(a.frames))
    db.add_note(cid, uid, 12.0, "Dr. Amal Zahrani called 0551234567 about patient@mail.com, DOB 12/03/1980")
    return uid, cid, a


def _facts(cid, a):
    case = db.get_case(cid)
    proc = procedures.get("lap-chole")
    p = {**{"conf": 0.25, "smooth": 3, "max_gap": 15.0}}
    _, _, iv = timeline.build_intervals(a, **service.timeline_params(p))
    usage = timeline.usage_stats(iv, a.duration, proc)
    return casecontext.build_facts(case, a, db.list_notes(cid), [], proc, timeline.phase_segments(a), usage, [],
                                   timeline.case_metrics(iv, a.duration)), case


def test_deidentify_masks_identifiers():
    out = deid.deidentify("Dr. Amal Zahrani, MRN 4455667, phone 0551234567, a@b.com, DOB 12/03/1980, patient Sara", ["Sara"])
    for leak in ("Amal", "4455667", "0551234567", "a@b.com", "12/03/1980", "Sara"):
        assert leak not in out


def test_facts_never_contain_title_or_names(tmp_platform):
    uid, cid, a = _case(tmp_platform)
    facts, _ = _facts(cid, a)
    blob = json.dumps(facts)
    assert "Mohammed" not in blob and "4455667" not in blob and "Amal" not in blob and "0551234567" not in blob
    assert facts["case_ref"] == f"Case #{cid}"
    assert any(n["author"].startswith("Clinician") for n in facts["doctor_notes"])


def test_external_ai_gate(monkeypatch):
    monkeypatch.delenv("ORI_ALLOW_EXTERNAL_AI", raising=False)
    monkeypatch.setenv("ANTHROPIC_API_KEY", "x")
    assert llm.status() == (False, "not_approved")
    monkeypatch.setenv("ORI_ALLOW_EXTERNAL_AI", "1")
    monkeypatch.delenv("ANTHROPIC_API_KEY")
    assert llm.status() == (False, "no_key")
    with pytest.raises(llm.LLMError):
        llm.complete("s", [{"role": "user", "content": "hi"}])
    monkeypatch.setenv("ANTHROPIC_API_KEY", "x")
    assert llm.status() == (True, "")


def test_parse_pubmed_xml():
    (r,) = references.parse_articles(PUBMED_XML)
    assert r.pmid == "111" and r.authors == ["Smith J", "Lee K"] and r.date == "2023 May" and r.doi == "10.1/abc"
    assert r.category == "guideline" and r.url.endswith("/111/")


def test_queries_use_procedure_not_case_data():
    qs = references.build_queries("lap-chole", "Laparoscopic cholecystectomy", ["Calot triangle dissection"], ["clipper"])
    assert any("Calot triangle dissection" in q for _, q in qs) and all("cholecystectomy" in q for _, q in qs)


def test_rank_keeps_overview_and_best_match(tmp_platform):
    uid, cid, a = _case(tmp_platform)
    facts, _ = _facts(cid, a)
    chunks = casecontext.facts_to_chunks(facts, [{"pmid": "111", "title": "Critical view of safety", "authors": ["Smith J"], "journal": "J", "date": "2023", "abstract": "clipping study"}])
    picked = casecontext.rank_chunks("what does the reference say about clipping", chunks, k=3)
    labels = [c[0] for c in picked]
    assert "C1" in labels and "R1" in labels


def test_assistant_returns_only_real_sources(tmp_platform, monkeypatch):
    uid, cid, a = _case(tmp_platform)
    facts, _ = _facts(cid, a)
    seen = {}

    def fake(system, messages, max_tokens=0):
        seen["msgs"] = messages
        return llm.Result("The case lasted 1:40 [C1]. See also [Z9].", 10, 5, "m")
    monkeypatch.setattr(llm, "complete", fake)
    r = assistant.ask(facts, [], [], "How long was this case? my number is 0551234567")
    assert [s["label"] for s in r["sources"]] == ["C1"]          # invented [Z9] is not shown as a source
    assert "0551234567" not in json.dumps(seen["msgs"])            # de-identified before leaving


def test_generate_ai_drops_unsupported_observations(tmp_platform, monkeypatch):
    uid, cid, a = _case(tmp_platform)
    facts, _ = _facts(cid, a)
    payload = {"summary": "S", "observations": [{"text": "ok", "evidence": ["C1"]}, {"text": "made up", "evidence": ["Q9"]},
                                                {"text": "no evidence", "evidence": []}], "limitations": "L"}
    monkeypatch.setattr(llm, "complete", lambda *a, **k: llm.Result("```json\n" + json.dumps(payload) + "\n```", 1, 1, "m"))
    ai, _ = case_report.generate_ai(facts)
    assert [o["text"] for o in ai["observations"]] == ["ok"]


def test_report_pdf_and_db_roundtrip(tmp_platform, tmp_path):
    uid, cid, a = _case(tmp_platform)
    facts, case = _facts(cid, a)
    notes = db.list_notes(cid)
    content = case_report.new_content(notes, timeline.phase_segments(a), a.duration)
    content["ai"] = {"summary": "Summary", "observations": [{"text": "Obs", "evidence": ["C1"]}], "limitations": "Lim", "model": "m"}
    rid = db.add_report(cid, content, uid, model="m", tokens_in=3, tokens_out=4)
    assert json.loads(db.latest_report(cid)["content_json"])["ai"]["summary"] == "Summary"
    db.update_report(rid, content, status="final", reviewed_by=uid)
    assert db.latest_report(cid)["status"] == "final"
    img = Image.new("RGB", (320, 180), (80, 30, 30))
    import io
    b = io.BytesIO(); img.save(b, "JPEG")
    out = tmp_path / "r.pdf"
    used = case_report.build_pdf(out, case=dict(case), facts=facts, notes=notes, content=content, frames=[(12.0, b.getvalue(), "Doctor's note")],
                                 status="final", reviewer="Dr. A", lang="en")
    assert used == "en" and out.read_bytes()[:4] == b"%PDF" and out.stat().st_size > 2000


def test_refs_and_chat_storage_and_privacy_between_doctors(tmp_platform):
    uid, cid, a = _case(tmp_platform)
    other = auth.create_user("doc2", "pw12345678", "instructor", "Dr. Other")
    db.save_refs(cid, [{"pmid": "1"}])
    assert db.load_refs(cid)[0] == [{"pmid": "1"}]
    db.add_chat(cid, uid, "user", "q")
    assert len(db.list_chat(cid, uid)) == 1 and db.list_chat(cid, other) == []
    db.delete_case(cid)
    assert db.list_chat(cid, uid) == [] and db.load_refs(cid) is None
