# src/inference — video inference module (Owner: Member B)

WBS 3.3.1 / 3.3.2. Consumers: Member C (`src/api/jobs.py`, `src/timeline/evaluate.py`), Member D (run scripts).
**Call it, never edit it.** Signature changes need a contract PR first (see `contracts/README.md`).

## Python API (contract C4)

```python
from src.inference.detect_video import detect_video

result = detect_video("video.mp4", "detections.jsonl", sample_fps=5.0, conf=0.25,
                      weights="models/weights/best.pt", on_progress=lambda f: print(f))
# result == {"frames": <int>, "seconds": <float>}
```

## CLI

```bash
python -m src.inference.detect_video in.mp4 out.jsonl --fps 5
python -m src.inference.fetch_weights
```

## Status (fill in as you go — Member B)

- [ ] Works with stand-in `yolov8n.pt` (Mon)
- [ ] Works with `baseline.pt` (Tue)
- [ ] Works with `best.pt` (Tue 23:00, milestone M4)
- [ ] Speed on target GPU for a 2-min 1080p clip at 5 fps: `TODO s`
- [ ] CPU fallback tested
