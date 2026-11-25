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

- [x] Works with `best.pt` (sha256 `02ac6525…3741`, Drive `weights/best.pt`): 2-min 1080p clip at 5 fps →
      600 records, **all valid against `contracts/detections.schema.json`**, progress callback reaches 1.0 (2026-11-25).
- [x] CPU tested (Intel i7-1165G7 laptop): 2-min 1080p clip at 5 fps in **71 s** (35.7 s per video-minute);
      at 1 fps in 12 s. Full table: `docs/model/BENCHMARK.md`.
- [ ] End-to-end GPU timing: not run. Model time on an NVIDIA L4 is 3.1 ms per frame (test evaluation), so a
      2-min clip at 5 fps needs ≈ 2 s of model time plus video decoding.
- [ ] `tests/fixtures/sample_video.mp4` does not exist yet (Member D, 1.2.2), so `tests/unit/inference` still skips.

Use: copy `best.pt` from the team Drive to `models/weights/best.pt` (gitignored). Recommended `sample_fps`:
5 on a GPU, 1 on a CPU-only laptop. Confidence threshold: 0.25 (see `docs/model/EVALUATION.md`).
