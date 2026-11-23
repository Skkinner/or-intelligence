"""Generate the SYNTHETIC shared test fixtures (no real surgery data, no model output).

Owner: Member D (WBS 1.2.2). Re-run after changing a contract:  python tests/fixtures/make_fixtures.py

Writes:
    sample_detections.jsonl        600 frames = 2 min at 5 fps, contract C4, with deliberate 1-frame flicker
    sample_timeline.json           contract C5 for the same clean (pre-flicker) segments
    sample_timeline_case02.json    a second case for search/analytics tests
    sample_notes.json              3 instructor notes
    sample_presence.csv            contract C3 ground truth for case 01 (1 fps)

The "clean" segments below are invented test data. They are NOT results of any model.
tests/fixtures/sample_video.mp4 (synthetic, <= 10 MB) is still TODO for Member D (see README.md).
"""

from __future__ import annotations

import json
import random
from pathlib import Path

OUT = Path(__file__).resolve().parent
NAMES = ["grasper", "bipolar", "hook", "scissors", "clipper", "irrigator"]
FPS = 5.0
DURATION = 120.0
PARAMS = {"conf": 0.4, "window_s": 2.0, "min_segment_s": 1.5, "merge_gap_s": 2.0, "method": "majority"}

CASES = {
    "fixture_case_01": {
        "grasper": [(0.0, 48.0), (70.0, 120.0)],
        "hook": [(10.0, 45.0), (80.0, 100.0)],
        "clipper": [(50.0, 58.0), (61.0, 66.0)],
        "scissors": [(66.0, 70.0)],
        "irrigator": [(100.0, 115.0)],
    },
    "fixture_case_02": {
        "grasper": [(0.0, 120.0)],
        "bipolar": [(20.0, 30.0)],
        "hook": [(30.0, 75.0)],
        "clipper": [(76.0, 90.0)],
        "irrigator": [(95.0, 110.0)],
    },
}


def active(case: dict, t: float) -> set[str]:
    return {tool for tool, segs in case.items() for s, e in segs if s <= t < e}


def stats_for(case: dict) -> dict:
    per_tool_s = {tool: round(sum(e - s for s, e in segs), 3) for tool, segs in case.items()}
    per_tool_segments = {tool: len(segs) for tool, segs in case.items()}
    switches, prev = 0, active(case, 0.0)
    t = 1.0 / FPS
    while t < DURATION:
        cur = active(case, t)
        if cur != prev:
            switches += 1
        prev, t = cur, t + 1.0 / FPS
    return {"total_s": DURATION, "switches": switches, "per_tool_s": per_tool_s,
            "per_tool_segments": per_tool_segments}


def timeline_for(video_id: str, case: dict, rng: random.Random) -> dict:
    tools = {tool: [{"start": s, "end": e, "mean_conf": round(rng.uniform(0.6, 0.9), 2)} for s, e in segs]
             for tool, segs in case.items()}
    return {"video_id": video_id, "duration_s": DURATION, "sample_fps": FPS, "tools": tools,
            "stats": stats_for(case), "params": PARAMS}


def detections_for(video_id: str, case: dict, rng: random.Random) -> list[dict]:
    rows = []
    for frame_idx in range(int(DURATION * FPS)):
        t = frame_idx / FPS
        dets = []
        for tool in sorted(active(case, t)):
            if rng.random() < 0.08:          # deliberate flicker: missed detection
                continue
            x1, y1 = rng.uniform(0.05, 0.5), rng.uniform(0.05, 0.5)
            dets.append({"cls": NAMES.index(tool), "name": tool, "conf": round(rng.uniform(0.45, 0.95), 3),
                         "box": [round(x1, 3), round(y1, 3), round(x1 + 0.3, 3), round(y1 + 0.3, 3)]})
        if rng.random() < 0.03:              # deliberate flicker: spurious low-confidence false positive
            tool = rng.choice(NAMES)
            dets.append({"cls": NAMES.index(tool), "name": tool, "conf": round(rng.uniform(0.25, 0.5), 3),
                         "box": [0.6, 0.6, 0.8, 0.8]})
        rows.append({"video_id": video_id, "frame": frame_idx * 5, "t": round(t, 3), "w": 1280, "h": 720,
                     "dets": dets})
    return rows


def presence_csv(case: dict) -> str:
    lines = ["t_sec," + ",".join(NAMES)]
    for sec in range(int(DURATION)):
        act = active(case, float(sec))
        lines.append(",".join([str(sec)] + ["1" if n in act else "0" for n in NAMES]))
    return "\n".join(lines) + "\n"


def main() -> None:
    rng = random.Random(42)
    case1 = CASES["fixture_case_01"]
    with open(OUT / "sample_detections.jsonl", "w", encoding="utf-8", newline="\n") as fh:
        for row in detections_for("fixture_case_01", case1, rng):
            fh.write(json.dumps(row, separators=(",", ":")) + "\n")
    (OUT / "sample_timeline.json").write_text(
        json.dumps(timeline_for("fixture_case_01", case1, rng), indent=2) + "\n", encoding="utf-8")
    (OUT / "sample_timeline_case02.json").write_text(
        json.dumps(timeline_for("fixture_case_02", CASES["fixture_case_02"], rng), indent=2) + "\n",
        encoding="utf-8")
    notes = [
        {"id": 1, "video_id": "fixture_case_01", "t_sec": 12.0, "text": "Good hook angle during dissection",
         "author": "instructor", "created_at": "2026-11-23T20:00:00Z"},
        {"id": 2, "video_id": "fixture_case_01", "t_sec": 52.5, "text": "Check clip placement before cutting",
         "author": "instructor", "created_at": "2026-11-23T20:01:00Z"},
        {"id": 3, "video_id": "fixture_case_01", "t_sec": 101.0, "text": "Irrigation could be shorter",
         "author": "instructor", "created_at": "2026-11-23T20:02:00Z"},
    ]
    (OUT / "sample_notes.json").write_text(json.dumps(notes, indent=2) + "\n", encoding="utf-8")
    (OUT / "sample_presence.csv").write_text(presence_csv(case1), encoding="utf-8", newline="\n")
    print(f"fixtures written to {OUT}")


if __name__ == "__main__":
    main()
