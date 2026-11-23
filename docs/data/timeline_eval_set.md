# Timeline evaluation set (Owner: Member A, WBS 2.3.1)

Built by `py scripts/build_presence.py` from the CholecInstanceSeg annotation zip → `data/processed/presence/<video>.csv` (contract C3).

| Video | Role | Duration (s) | CSV rows | Source |
|---|---|---|---|---|
| VID23 | tuning | 1636 | 1636 | CholecInstanceSeg `val/VID23_t50_full` (CholecT50, 1 fps) |
| VID14 | reporting | 1709 | 1709 | CholecInstanceSeg `test/VID14_t50_full` |
| VID15 | reporting | 2059 | 2059 | CholecInstanceSeg `test/VID15_t50_full` |
| VID22 | reporting | 1533 | 1533 | CholecInstanceSeg `test/VID22_t50_full` |
| VID29 | reporting | 2351 | 2351 | CholecInstanceSeg `test/VID29_t50_full` |

How it is built: frame `<prefix>_VIDxx_<n>.json` is second `n` (CholecT50 is released at 1 fps and these folders
have every frame 0…N−1, no gaps). A tool is `1` in a second if that frame has at least one instance of it. Snare is ignored.

Share of seconds with each tool:

| Video | grasper | bipolar | hook | scissors | clipper | irrigator |
|---|---|---|---|---|---|---|
| VID23 | 61% | 14% | 53% | 6% | 3% | 3% |
| VID14 | 67% | 14% | 38% | 2% | 1% | 17% |
| VID15 | 73% | 4% | 43% | 2% | 2% | 5% |
| VID22 | 73% | 6% | 48% | 2% | 7% | 15% |
| VID29 | 49% | 2% | 55% | 2% | 5% | 16% |

Scissors and clipper are present in only 1–7% of seconds, so their timeline scores will be noisy; report them separately.

## Overlap check with detector training videos

Method: CholecInstanceSeg's recommended split is by surgery, and `01_Data.ipynb` step 5 groups frames by surgery
number (`VIDxx`) across all sources (Cholec80 / CholecT50 / CholecSeg8k folders). Checked with the metadata CSV:
no surgery number appears in more than one split. VID14/15/22/29 are in **test** and VID23 in **val**, so none of these
surgeries contributed a training frame. VID23 is also the detector's validation data (used for early stopping), which
is acceptable for tuning but means it must not be used for reported numbers.

Risks: durations come from the annotations (1 frame = 1 s). If Member C runs on the original Cholec80 25 fps videos
instead of the 1 fps frames, check that the video length matches the CSV row count (±2 s, contract C3); the
CholecT50 release may trim the start/end of the original videos.

Hand-off: CSVs in `data/processed/presence/` (contract C3) → Member C (4.1.3). The matching frames are
`img_dir/` of the same folders in the image set (also inside `yolo_dataset.zip` under `images/val|test/t50_VIDxx_*`).
