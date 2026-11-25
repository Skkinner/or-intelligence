"""Train the phase estimator on CholecT50 videos and report leave-one-video-out accuracy.

  pip install scikit-learn
  python scripts/train_phase_estimator.py --src <.../cholect50-challenge-val>
Writes models/phase_estimator.json and models/phase_metrics.json.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from or_intelligence.constants import PHASE_EN  # noqa: E402
from or_intelligence.data import cholect50  # noqa: E402
from or_intelligence.phase_estimator import PhaseEstimator, features  # noqa: E402
from or_intelligence.timeline import presence  # noqa: E402


def build(analyses: dict, noise: float = 0.0, seed: int = 0):
    rng = np.random.default_rng(seed)
    out = {}
    for vid, a in analyses.items():
        frames = sorted((f for f in a.frames if f.phase is not None), key=lambda f: f.t)
        a2 = type(a)(a.video_id, a.source, a.duration, frames, a.detector, a.params)
        times, m = presence(a2)
        if noise:                                    # simulate detector errors: drops and false alarms
            drop = rng.random(m.shape) < noise
            fake = rng.random(m.shape) < noise / 3
            m = (m & ~drop) | fake
        y = np.array([f.phase for f in frames])
        out[vid] = (times, m, y, a.duration)
    return out


def fit(data: dict, vids: list[str]):
    from sklearn.linear_model import LogisticRegression
    from sklearn.preprocessing import StandardScaler
    x = np.vstack([features(*[data[v][i] for i in (0, 1)], data[v][3]) for v in vids])
    y = np.concatenate([data[v][2] for v in vids])
    sc = StandardScaler().fit(x)
    clf = LogisticRegression(max_iter=2000, C=0.5).fit(sc.transform(x), y)
    # make sure every phase has a row, even if a class never appears in the training videos
    k = 7
    coef = np.zeros((k, x.shape[1]))
    inter = np.full(k, -20.0)
    for row, c in enumerate(clf.classes_):
        coef[int(c)], inter[int(c)] = clf.coef_[row], clf.intercept_[row]
    return PhaseEstimator(range(k), sc.mean_, sc.scale_, coef, inter)


def evaluate(data: dict, noise_eval: dict) -> dict:
    res = {"clean": [], "noisy": []}
    for held in data:
        train = [v for v in data if v != held]
        est = fit(data, train)
        for key, d in (("clean", data), ("noisy", noise_eval)):
            times, m, y, dur = d[held]
            pred = est.estimate_matrix(times, m, dur, complete=True)[0]   # held-out videos are complete operations
            res[key].append({"video": held, "frames": int(len(y)), "accuracy": float((pred == y).mean()),
                             "phases_in_truth": sorted({int(v) for v in y})})
    return {k: {"per_video": v, "mean_accuracy": float(np.mean([r["accuracy"] for r in v]))} for k, v in res.items()}


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--src", required=True)
    ap.add_argument("--noise", type=float, default=0.15, help="simulated detector error rate for the noisy check")
    a = ap.parse_args()

    cases = cholect50.load_root(a.src)
    analyses = {v: c[0] for v, c in cases.items()}
    if len(analyses) < 3:
        sys.exit("Need at least 3 videos for leave-one-video-out evaluation.")
    clean = build(analyses)
    noisy = build(analyses, noise=a.noise)
    metrics = evaluate(clean, noisy)
    est = fit(clean, list(clean))
    est.meta = {"trained_on": sorted(clean), "n_frames": int(sum(len(v[2]) for v in clean.values())),
                "phases": PHASE_EN, "trained_at": time.strftime("%Y-%m-%d %H:%M")}
    (ROOT / "models").mkdir(exist_ok=True)
    est.save(ROOT / "models" / "phase_estimator.json")
    metrics["noise_rate_for_noisy_check"] = a.noise
    metrics["majority_class_baseline"] = float(np.mean([
        max(np.bincount(clean[v][2], minlength=7)) / len(clean[v][2]) for v in clean]))
    metrics["note"] = "Leave-one-video-out on the training videos; tiny dataset, offline use only."
    (ROOT / "models" / "phase_metrics.json").write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    print(json.dumps({k: (v if not isinstance(v, dict) else v["mean_accuracy"]) for k, v in metrics.items()}, indent=2))
    for key in ("clean", "noisy"):
        print(key, [f'{r["video"]}:{r["accuracy"]:.2f}' for r in metrics[key]["per_video"]])


if __name__ == "__main__":
    main()
