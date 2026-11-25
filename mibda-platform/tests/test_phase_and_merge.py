import numpy as np
import yaml

from conftest import make_analysis
from or_intelligence import procedures
from or_intelligence.data import merge
from or_intelligence.phase_estimator import PhaseEstimator, left_to_right_transitions, viterbi


def test_viterbi_is_left_to_right_and_removes_blips():
    k = 4
    truth = np.repeat([0, 1, 2, 3], 10)
    log_p = np.full((40, k), np.log(0.1))
    log_p[np.arange(40), truth] = np.log(0.7)
    log_p[15, 3] = np.log(0.9)            # one-sample blip pointing at a later phase
    log_p[15, 1] = np.log(0.05)
    path = viterbi(log_p, left_to_right_transitions(k))
    assert list(path) == list(truth)      # the blip is smoothed away, order is preserved
    assert np.all(np.diff(path) >= 0)


def test_estimator_roundtrip_and_apply(tmp_path):
    k, f = 7, 19
    rng = np.random.default_rng(0)
    est = PhaseEstimator(range(k), np.zeros(f), np.ones(f), rng.normal(size=(k, f)), np.zeros(k), {"x": 1})
    est.save(tmp_path / "m.json")
    est2 = PhaseEstimator.load(tmp_path / "m.json")
    x = rng.normal(size=(5, f))
    assert np.allclose(est.predict_proba(x), est2.predict_proba(x)) and est2.meta == {"x": 1}
    a = make_analysis({0: [(0, 50)], 2: [(30, 80)]}, duration=100)
    out = est2.apply(a)
    assert len(out.frames) == len(a.frames) and all(0 <= fr.phase < k for fr in out.frames)
    assert out.params["phase_source"] == "estimated" and a.params.get("phase_source") is None   # original untouched


def _make_yolo(root, names, items):
    for split, stem, cls_lines in items:
        (root / "images" / split).mkdir(parents=True, exist_ok=True)
        (root / "labels" / split).mkdir(parents=True, exist_ok=True)
        (root / "images" / split / f"{stem}.png").write_bytes(b"png")
        (root / "labels" / split / f"{stem}.txt").write_text("\n".join(cls_lines) + "\n")
    (root / "data.yaml").write_text(yaml.safe_dump({"names": dict(enumerate(names))}))


def test_merge_maps_renames_and_drops_classes(tmp_path):
    a, b = tmp_path / "a", tmp_path / "b"
    _make_yolo(a, ["grasper", "hook"], [("train", "x", ["0 0.5 0.5 0.1 0.1", "1 0.2 0.2 0.1 0.1"])])
    _make_yolo(b, ["Grasper", "needle"], [("train", "x", ["0 0.4 0.4 0.2 0.2", "1 0.1 0.1 0.1 0.1"]),
                                          ("val", "y", ["0 0.3 0.3 0.1 0.1"])])
    st = merge.merge({"a": a, "b": b}, tmp_path / "out", rename={"Grasper": "grasper", "needle": None})
    assert st["classes"] == ["grasper", "hook"] and st["dropped_instances"] == 1
    assert st["images"]["train"] == 2 and st["images"]["val"] == 1
    out = tmp_path / "out" / "labels" / "train"
    assert (out / "a__x.txt").exists() and (out / "b__x.txt").exists()        # same stem, no collision
    assert (out / "b__x.txt").read_text().split("\n")[0].startswith("0 ")     # renamed class maps to id 0
    assert len((out / "b__x.txt").read_text().strip().split("\n")) == 1       # dropped class removed
    assert yaml.safe_load((tmp_path / "out" / "data.yaml").read_text())["names"] == {0: "grasper", 1: "hook"}


def test_procedure_library_is_consistent():
    procs = procedures.load_all()
    reg = procedures.dataset_registry()
    assert {p.id for p in procs} >= {"lap-chole", "lap-hysterectomy"}
    assert {p.id for p in procs if p.status == "ready"} == {"lap-chole", "cataract"}   # only these have real data here
    for p in procs:
        assert p.name["en"] and p.name["ar"] and p.specialty["ar"]
        missing = [d for d in p.datasets if d not in reg]
        assert not missing, f"{p.id} references unknown datasets {missing}"
