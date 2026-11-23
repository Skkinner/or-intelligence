# contracts/ — shared interfaces (Owner: Member D)

These files are the **only** coupling between members. Build and test against them plus `tests/fixtures/`, never against another member's unfinished code.

| ID | File | Producer → Consumers | What it fixes |
|---|---|---|---|
| C1 | `classes.json` | D → everyone | class ids 0–5, names, UI colours |
| C2 | `dataset_layout.md` | A → B | YOLO folders, label format, `dataset.yaml`, `splits.json` |
| C3 | `presence.schema.md` | A → C | 1 fps tool-presence CSV for timeline evaluation |
| C4 | `detections.schema.json` | B → C | one JSON line per sampled frame + `detect_video()` signature |
| C5 | `timeline.schema.json` | C → C, D, A | per-video intervals + statistics |
| C6 | `openapi.yaml` | D/C → D, A | every HTTP endpoint |

## Python signatures fixed by the contracts

```python
# C4 — Member B, src/inference/detect_video.py
detect_video(video_path: str, out_path: str, sample_fps: float = 5.0, conf: float = 0.25,
             weights: str = "models/weights/best.pt",
             on_progress: Callable[[float], None] | None = None) -> dict   # {"frames": int, "seconds": float}

# C5 — Member C, src/timeline/builder.py
build_timeline(dets_path: str, video_id: str, params: dict) -> dict      # validates against timeline.schema.json

# Member C, src/reports/pdf_report.py
render_report(timeline: dict, notes: list[dict], lang: str, out_path: str) -> str

# Member C, src/timeline/evaluate.py (Member B calls it read-only in 6.1.1)
evaluate_video(timeline: dict, presence_csv: str) -> dict
```

Validated in CI by `tests/contracts/test_schemas.py`. Change process: see `CHANGELOG.md`.
