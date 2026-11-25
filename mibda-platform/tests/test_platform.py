import json
import time

import pytest

from conftest import make_analysis, write_fake_cholect50
from or_intelligence import auth, config, db, report, service, timeline
from or_intelligence.constants import INSTRUMENTS


def test_auth_roundtrip_and_validation(tmp_platform):
    uid = auth.create_user("Dr.X", "longenough1", "instructor", "Dr X")
    assert auth.authenticate("dr.x", "longenough1")["id"] == uid          # username is case-insensitive
    assert auth.authenticate("dr.x", "wrong-password") is None
    assert auth.authenticate("nobody", "whatever123") is None
    with pytest.raises(ValueError):
        auth.create_user("a", "short", "trainee")
    with pytest.raises(ValueError):
        auth.create_user("b", "longenough1", "superuser")
    with pytest.raises(Exception):
        auth.create_user("dr.x", "longenough1", "trainee")                # duplicate


def _case(owner, trainee=None, **kw):
    a = make_analysis({0: [(0, 30)]}, duration=60)
    path = config.ANALYSIS_DIR / f"{owner}_{kw.get('name', 'c')}.json"
    a.save(path)
    return db.add_case(title=kw.get("name", "c"), media_kind="frames", media_path=str(config.UPLOAD_DIR / "x"),
                       analysis_path=str(path), source="model", owner_id=owner, trainee_id=trainee,
                       retention_days=kw.get("retention"), duration=60, stats=timeline.summary(a))


def test_case_visibility_by_role(tmp_platform):
    t1 = auth.create_user("t1", "password-one", "trainee")
    t2 = auth.create_user("t2", "password-two", "trainee")
    ins = auth.create_user("ins", "password-ins", "instructor")
    c1 = _case(ins, t1, name="for-t1")
    c2 = _case(ins, t2, name="for-t2")
    users = {u["id"]: u for u in auth.list_users()}
    assert [c["id"] for c in db.list_cases(users[t1])] == [c1]
    assert {c["id"] for c in db.list_cases(users[ins])} == {c1, c2}
    assert not db.can_view(users[t1], db.get_case(c2))


def test_notes_permissions(tmp_platform):
    a = auth.create_user("a1", "password-aaa", "trainee")
    b = auth.create_user("b1", "password-bbb", "trainee")
    adm = auth.create_user("adm", "password-adm", "admin")
    cid = _case(adm, a)
    nid = db.add_note(cid, a, 12.0, "check this clip")
    users = {u["id"]: u for u in auth.list_users()}
    db.delete_note(nid, users[b])                       # someone else cannot delete it
    assert len(db.list_notes(cid)) == 1
    db.delete_note(nid, users[a])
    assert db.list_notes(cid) == []


def test_delete_and_purge_only_remove_files_inside_data_dirs(tmp_platform, tmp_path):
    adm = auth.create_user("adm", "password-adm", "admin")
    outside = tmp_path / "precious.mp4"
    outside.write_bytes(b"do not delete")
    upload = config.UPLOAD_DIR / "u.mp4"
    upload.parent.mkdir(parents=True, exist_ok=True)
    upload.write_bytes(b"x")
    a = make_analysis({0: [(0, 10)]}, duration=20)
    ap = config.ANALYSIS_DIR / "a.json"
    a.save(ap)
    cid = db.add_case(title="up", media_kind="video", media_path=str(upload), analysis_path=str(ap), source="model",
                      owner_id=adm, retention_days=1, duration=20)
    cid2 = db.add_case(title="ext", media_kind="video", media_path=str(outside), analysis_path=str(ap), source="model",
                       owner_id=adm, retention_days=1, duration=20)
    assert db.purge_expired(now_ts=int(time.time()) + 3 * 86400) == 2
    assert db.get_case(cid) is None and db.get_case(cid2) is None
    assert not upload.exists()
    assert outside.exists()                              # a file outside the data folders is never deleted


def test_import_cholect50_creates_cases_once(tmp_platform, tmp_path):
    root = write_fake_cholect50(tmp_path / "ds", ("VID01", "VID02"))
    adm = auth.create_user("adm", "password-adm", "admin")
    assert len(service.import_cholect50(root, adm)) == 2
    assert service.import_cholect50(root, adm) == []     # idempotent
    c = db.list_cases(auth.get_user(adm))[0]
    stats = json.loads(c["stats_json"])
    assert stats["usage"]["grasper"] > 0 and c["source"] == "annotations"


def test_pdf_report_english_and_arabic(tmp_path):
    a = make_analysis({INSTRUMENTS.index("hook"): [(5, 50)], INSTRUMENTS.index("clipper"): [(60, 62)]}, duration=90)
    _, _, ivs = timeline.build_intervals(a, smooth_window=1)
    usage = timeline.usage_stats(ivs, a.duration)
    kw = dict(case={"title": "Demo", "procedure": "chole", "video_id": "V1", "source": "annotations",
                    "detector": "d", "tags": "t", "created_at": time.time()},
              duration=a.duration, intervals=ivs, usage_df=usage, phases=timeline.phase_segments(a), flags=[],
              notes=[{"t_seconds": 3, "display_name": "Dr", "text": "note"}], clips=[],
              metrics=timeline.case_metrics(ivs, a.duration), dense=False)
    for lang in ("en", "ar"):
        out = tmp_path / f"r_{lang}.pdf"
        used = report.build_report(out, lang=lang, **kw)
        assert used in ("en", "ar") and out.stat().st_size > 2000
        assert out.read_bytes()[:4] == b"%PDF"
