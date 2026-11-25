import cv2
import numpy as np
import pytest

from conftest import make_analysis
from or_intelligence import auth, db, procedures, service, timeline
from or_intelligence.data import cataract101 as cat
from or_intelligence.models import CaseAnalysis


def write_csv(path, text):
    path.write_text(text, encoding="utf-8")
    return path


# ---- parser: the layouts it claims to understand -----------------------------------------------------
def test_per_frame_labels_with_header_and_one_based_ids(tmp_path):
    rows = ["frame,phase"] + [f"{f},{1 + f // 100}" for f in range(0, 300)]       # phases 1,2,3 -> 0,1,2
    cps = cat.parse_phase_csv(write_csv(tmp_path / "a.csv", "\n".join(rows)))
    assert cps == [(0, 0), (100, 1), (200, 2)]


def test_interval_rows_semicolon_no_header(tmp_path):
    cps = cat.parse_phase_csv(write_csv(tmp_path / "b.csv", "0;99;0\n100;199;1\n200;299;9\n"))
    assert cps == [(0, 0), (100, 1), (200, 9)]          # includes phase 0 and 9: 0-based, so left as is


def test_phase_start_boundaries(tmp_path):
    cps = cat.parse_phase_csv(write_csv(tmp_path / "c.csv", "phase,start_frame\n1,0\n2,500\n3,900\n"))
    assert cps == [(0, 0), (500, 1), (900, 2)]


def test_unrecognised_layouts_raise_instead_of_guessing(tmp_path):
    with pytest.raises(cat.AnnotationFormatError):
        cat.parse_phase_csv(write_csv(tmp_path / "d.csv", "1,2,3,4\n5,6,7,8\n"))
    with pytest.raises(cat.AnnotationFormatError):
        cat.parse_phase_csv(write_csv(tmp_path / "e.csv", "frame,phase\n0,50\n10,60\n"))   # ids do not fit 10 phases
    with pytest.raises(cat.AnnotationFormatError):
        cat.parse_phase_csv(write_csv(tmp_path / "f.csv", ""))


def test_phase_at():
    cps = [(0, 0), (100, 1), (200, 2)]
    assert [cat.phase_at(cps, f) for f in (0, 99, 100, 250)] == [0, 0, 1, 2]
    assert cat.phase_at([(50, 3)], 10) is None


# ---- end to end on a synthetic folder -------------------------------------------------------------------
def make_video(path, seconds=12, fps=10):
    w = cv2.VideoWriter(str(path), cv2.VideoWriter_fourcc(*"MJPG"), fps, (64, 48))
    for i in range(seconds * fps):
        w.write(np.full((48, 64, 3), (i * 2) % 255, np.uint8))
    w.release()


def test_build_analysis_and_import(tmp_path, monkeypatch):
    from or_intelligence import config
    data = tmp_path / "data"
    monkeypatch.setattr(config, "DATA_DIR", data)
    monkeypatch.setattr(config, "DB_PATH", data / "app.db")
    monkeypatch.setattr(config, "UPLOAD_DIR", data / "uploads")
    monkeypatch.setattr(config, "ANALYSIS_DIR", data / "analysis")
    db.init_db()
    root = tmp_path / "cat101"
    (root / "videos").mkdir(parents=True)
    (root / "annotations").mkdir()
    make_video(root / "videos" / "case_1.avi")
    make_video(root / "videos" / "case_2.avi")                                   # no annotation
    write_csv(root / "annotations" / "case_1.csv", "frame,phase\n" + "\n".join(f"{f},{1 + f // 40}" for f in range(120)))
    sc = cat.scan(root)
    assert len(sc.videos) == 2 and len(sc.matched) == 1 and len(sc.unmatched) == 1

    a = cat.build_analysis(root / "videos" / "case_1.avi", root / "annotations" / "case_1.csv")
    assert a.procedure == "cataract" and abs(a.duration - 12.0) < 0.2 and a.dense
    assert [f.phase for f in a.frames][:12] == [0, 0, 0, 0, 1, 1, 1, 1, 2, 2, 2, 2]      # 40 frames = 4 s at 10 fps
    segs = timeline.phase_segments(a)
    assert [s.phase for s in segs] == [0, 1, 2]

    adm = auth.create_user("adm", "password-adm", "admin")
    res = service.import_cataract101(root, adm)
    assert len(res["ids"]) == 1 and res["unmatched"] == ["case_2.avi"] and not res["skipped"]
    case = db.get_case(res["ids"][0])
    assert case["procedure"] == "cataract" and case["media_kind"] == "video"
    assert service.import_cataract101(root, adm)["ids"] == []                       # idempotent
    # the video file is only referenced: purging must never delete a file outside the platform's folders
    video = root / "videos" / "case_1.avi"
    db.delete_case(case["id"])
    assert video.exists()


# ---- the engine handles a procedure with no instrument labels ----------------------------------------------
def test_engine_with_zero_instruments():
    p = procedures.get("cataract")
    assert p.n_phases == 10 and p.n_instruments == 0 and p.phase_label(4) == "Phacoemulsification"
    a = make_analysis({}, duration=30)
    a.procedure = "cataract"
    for i, f in enumerate(a.frames):
        f.phase = i // 3
    times, m, ivs = timeline.build_intervals(a)
    assert m.shape == (len(a.frames), 0) and ivs == []
    s = timeline.summary(a)
    assert s["usage"] == {} and s["phases"] == list(range(10))
    assert CaseAnalysis.from_dict(a.to_dict()).procedure == "cataract"


def test_legacy_procedure_text_and_old_files_still_resolve():
    assert procedures.resolve("laparoscopic cholecystectomy").id == "lap-chole"
    assert procedures.resolve("Cataract surgery").id == "cataract"
    assert procedures.resolve(None).id == "lap-chole"
    d = make_analysis({}, duration=5).to_dict()
    d.pop("procedure")                                     # a file written before procedures existed
    assert CaseAnalysis.from_dict(d).procedure == "lap-chole"
