# Inference benchmark (Owner: Member B, WBS 6.1.1)

`python -m src.models.benchmark <clip>.mp4 --fps 1 2 5 --cpu`. Times `detect_video` end to end: video decoding,
frame sampling, YOLO with `best.pt` (sha256 `02ac6525…3741`), JSON writing. The model is loaded and warmed up first,
so the numbers do not include start-up (≈ 5 s once per job).

**Test clip:** 2 min, 1920×1080, 25 fps, built locally from 32 test-split frames (each shown for 1 s; not committed
because of the dataset licence). Speed depends on the frame size and the number of sampled frames, not on the
content, so this clip is representative for timing. It says nothing about accuracy.

## Measured (2026-11-25)

| Device | sample_fps | Video length (min) | Frames | Wall time (s) | s per video-minute |
|---|---|---|---|---|---|
| CPU Intel Core i7-1165G7 (4 cores / 8 threads, laptop) | 1 | 2.0 | 120 | 12.0 | **6.0** |
| CPU Intel Core i7-1165G7 | 2 | 2.0 | 250 | 26.8 | **13.4** |
| CPU Intel Core i7-1165G7 | 5 | 2.0 | 600 | 71.4 | **35.7** |

(At 25 fps source, "2 fps" samples every 12th frame = 2.08 fps, hence 250 frames.)

## GPU (from the test evaluation, not an end-to-end run)

During test evaluation on the Colab **NVIDIA L4** the model took 0.4 ms pre-processing + 1.9 ms inference + 0.8 ms
post-processing = **3.1 ms per frame** (batched, 640 px). At 5 fps that is ≈ 1 s of model time per video-minute;
in practice video decoding of 1080p will dominate. An end-to-end GPU run of `src.models.benchmark` was not done
(no GPU on the team laptops; Colab time went to training).

## What it means for a full surgery

| Surgery length | CPU 1 fps | CPU 2 fps | CPU 5 fps |
|---|---|---|---|
| 30 min | 3 min | 7 min | 18 min |
| 60 min | 6 min | 13 min | 36 min |

## Recommended default `sample_fps`

- **GPU server: 5 fps** (contract default). Fast, and gives the smoothing step 5 votes per second.
- **CPU-only laptop (demo): 1 fps.** A 30-min video finishes in about 3 minutes, and 1 fps matches the
  1 fps ground truth used for timeline evaluation. Use 2 fps if time allows.

Not measured: the effect of `sample_fps` on timeline macro-F1 (optional step; needs Member C's
`src/timeline/evaluate.py`, which is not finished).
