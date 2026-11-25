"""The HTTP API used by the React app: sign-in, per-case access, phases, notes, privacy of previews, AI gate."""
import pytest
from fastapi.testclient import TestClient

from conftest import make_analysis
from or_intelligence import auth, db, service


@pytest.fixture
def client(tmp_platform, monkeypatch):
    monkeypatch.delenv("ORI_ALLOW_EXTERNAL_AI", raising=False)
    monkeypatch.setenv("ORI_API_SECRET", "test-secret")
    from api.main import app, _analysis_cached
    _analysis_cached.cache_clear()
    with TestClient(app) as c:
        yield c


def _case(tmp_platform, owner, trainee=None):
    a = make_analysis({0: [(10, 60)], 4: [(30, 40)]}, duration=100)
    path = service._store(a, "t")
    return db.add_case(title="Case A", media_kind="frames", media_path=str(tmp_platform), analysis_path=str(path), source="annotations",
                       owner_id=owner, trainee_id=trainee, duration=100, n_frames=len(a.frames))


def _login(client, name, pw="pw12345678"):
    r = client.post("/api/login", json={"username": name, "password": pw})
    assert r.status_code == 200, r.text
    return r.json()


def test_requires_sign_in_and_rejects_bad_login(client):
    assert client.get("/api/cases").status_code == 401
    auth.create_user("doc", "pw12345678", "instructor")
    assert client.post("/api/login", json={"username": "doc", "password": "wrong-pass"}).status_code == 401
    assert client.get("/api/cases").status_code == 401
    client.cookies.set("mibda_session", "forged.token")
    assert client.get("/api/me").status_code == 401


def test_case_payload_has_phases_and_status(client, tmp_platform):
    uid = auth.create_user("doc", "pw12345678", "instructor", "Dr Doc")
    cid = _case(tmp_platform, uid)
    _login(client, "doc")
    d = client.get(f"/api/cases/{cid}").json()
    assert d["duration"] == 100 and d["phases"] and all(p["verified"] for p in d["phases"])
    assert d["phases"][0]["start"] == 0.0 and d["phases"][-1]["end"] <= 100
    assert len(d["procedure"]["phases"]) == 7 and d["frames"] and d["can_ai"]
    assert client.get("/api/dashboard").json()["kpis"]["cases"] == 1


def test_trainee_only_sees_own_cases_and_no_ai(client, tmp_platform):
    doc = auth.create_user("doc", "pw12345678", "instructor")
    tr = auth.create_user("tr", "pw12345678", "trainee")
    other = auth.create_user("tr2", "pw12345678", "trainee")
    mine, theirs = _case(tmp_platform, doc, tr), _case(tmp_platform, doc, other)
    _login(client, "tr")
    assert [c["id"] for c in client.get("/api/cases").json()] == [mine]
    assert client.get(f"/api/cases/{theirs}").status_code == 403
    assert client.get(f"/api/cases/{mine}/chat").status_code == 403
    assert client.post(f"/api/cases/{mine}/report/generate", json={"with_ai": False}).status_code == 403
    assert client.get(f"/api/cases/{mine}/report").json()["report"] is None


def test_notes_roundtrip_and_delete_rules(client, tmp_platform):
    doc = auth.create_user("doc", "pw12345678", "instructor", "Dr Doc")
    cid = _case(tmp_platform, doc)
    _login(client, "doc")
    assert client.post(f"/api/cases/{cid}/notes", json={"t": 12, "text": "  "}).status_code == 422
    nid = client.post(f"/api/cases/{cid}/notes", json={"t": 12, "text": "clip applied"}).json()["id"]
    assert client.get(f"/api/cases/{cid}").json()["notes"][0]["text"] == "clip applied"
    client.delete(f"/api/cases/{cid}/notes/{nid}")
    assert client.get(f"/api/cases/{cid}").json()["notes"] == []


def test_ai_is_gated_and_report_without_ai_can_be_approved(client, tmp_platform):
    doc = auth.create_user("doc", "pw12345678", "instructor", "Dr Doc")
    cid = _case(tmp_platform, doc)
    _login(client, "doc")
    assert client.get(f"/api/cases/{cid}/report").json()["ai"] == {"ok": False, "reason": "not_approved"}
    assert client.post(f"/api/cases/{cid}/report/generate", json={"with_ai": True}).status_code == 502
    assert client.post(f"/api/cases/{cid}/chat", json={"question": "hi"}).status_code == 503
    rep = client.post(f"/api/cases/{cid}/report/generate", json={"with_ai": False}).json()
    assert rep["status"] == "draft"
    r = client.put(f"/api/cases/{cid}/report", json={"content": {"doctor_comments": "ok"}, "approve": True})
    assert r.status_code == 422                                           # needs the review confirmation
    r = client.put(f"/api/cases/{cid}/report", json={"content": {"doctor_comments": "ok"}, "approve": True, "confirmed": True}).json()
    assert r["status"] == "final" and r["reviewer"] == "Dr Doc"
    assert client.put(f"/api/cases/{cid}/report", json={"content": {}}).status_code == 409
    assert client.post(f"/api/cases/{cid}/report/reopen").json()["status"] == "draft"
    assert client.get(f"/api/cases/{cid}/report.pdf").content[:4] == b"%PDF"


def test_export_pdf_and_thumbnail_is_blurred(client, tmp_platform):
    from PIL import Image
    import io
    doc = auth.create_user("doc", "pw12345678", "instructor")
    a = make_analysis({0: [(0, 9)]}, duration=10)
    for f in a.frames:
        f.image = "f.png"
    Image.effect_noise((200, 120), 90).convert("RGB").save(tmp_platform / "f.png")
    path = service._store(a, "img")
    cid = db.add_case(title="x", media_kind="frames", media_path=str(tmp_platform), analysis_path=str(path), source="annotations",
                      owner_id=doc, duration=10, n_frames=len(a.frames))
    _login(client, "doc")
    assert client.get(f"/api/cases/{cid}/export.pdf").content[:4] == b"%PDF"
    sharp = Image.open(io.BytesIO(client.get(f"/api/cases/{cid}/frame?t=1").content)).convert("L")
    soft = Image.open(io.BytesIO(client.get(f"/api/cases/{cid}/thumb").content)).convert("L")
    import numpy as np
    assert np.asarray(soft, float).std() < np.asarray(sharp, float).std() / 3      # the preview carries no sharp detail


# ------------------------------------------------------------------ live analysis, class mapping, phase analytics
def test_class_map_matches_by_name_not_position():
    from or_intelligence.detector import class_map
    assert class_map({0: "grasper", 1: "bipolar", 2: "hook", 3: "scissors", 4: "clipper", 5: "irrigator"}) == {i: i for i in range(6)}
    assert class_map({0: "Hook", 1: "Grasper", 2: "needle"}) == {0: 2, 1: 0}            # retrained order, unknown class dropped
    assert class_map(None) == {i: i for i in range(6)}


def _tiny_video(path, seconds=4, fps=10):
    import cv2
    import numpy as np
    w = cv2.VideoWriter(str(path), cv2.VideoWriter_fourcc(*"mp4v"), fps, (160, 120))
    for i in range(seconds * fps):
        w.write(np.full((120, 160, 3), (40 + i % 50, 90, 120), np.uint8) + np.random.randint(0, 40, (120, 160, 3), dtype=np.uint8))
    w.release()


def test_live_analysis_end_to_end(client, tmp_platform, tmp_path, monkeypatch):
    import time
    from api import live
    from or_intelligence import detector
    from or_intelligence.models import Box

    class Fake:
        name = "fake"
        def __init__(self, *a, **k): pass
        def detect(self, frame): return [Box(2, 0.1, 0.05, 0.3, 0.3, 0.91)]
    monkeypatch.setattr(detector, "YoloDetector", Fake)
    monkeypatch.setattr(live, "ready", lambda: True)
    monkeypatch.setattr(live, "UPLOAD_TMP", tmp_path / "up")
    auth.create_user("doc", "pw12345678", "instructor")
    _login(client, "doc")
    vid = tmp_path / "v.mp4"
    _tiny_video(vid)
    up = client.post("/api/live/upload?name=v.mp4", content=vid.read_bytes()).json()
    assert client.post("/api/live/upload?name=evil.exe", content=b"x").status_code == 415
    jid = client.post("/api/live/start", json={"token": up["token"], "name": up["name"], "rate": 2, "conf": 0.3}).json()["id"]
    for _ in range(100):
        s = client.get(f"/api/live/{jid}").json()
        if s["status"] != "running":
            break
        time.sleep(0.1)
    assert s["status"] == "done" and s["n_frames"] >= 6 and s["latest"]["boxes"][0][0] == 2     # real class id, not a label
    assert s["chart"]["intervals"] and client.get(f"/api/live/{jid}/frame").content[:2] == b"\xff\xd8"
    assert client.post(f"/api/live/{jid}/save", json={"title": "x", "consent": False}).status_code == 422
    cid = client.post(f"/api/live/{jid}/save", json={"title": "Live test", "consent": True}).json()["case_id"]
    assert db.get_case(cid)["title"] == "Live test"
    other = auth.create_user("doc2", "pw12345678", "instructor")
    client.post("/api/logout")
    _login(client, "doc2")
    assert client.get(f"/api/live/{jid}").status_code == 404                                   # jobs are private to their owner


def test_case_analytics(client, tmp_platform):
    doc = auth.create_user("doc", "pw12345678", "instructor")
    cid = _case(tmp_platform, doc)
    _login(client, "doc")
    a = client.get(f"/api/cases/{cid}/analytics").json()
    assert len(a["time_per_phase"]) == 7 and abs(sum(a["time_per_phase"]) - 100) < 5
    assert a["library_median"] is None and len(a["heatmap"]) == 6 and a["rows"]
