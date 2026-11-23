# Label QA notes (Owner: Member A, WBS 2.2.1)

Rendered by `notebooks/01_Data.ipynb` step 4 into `MyDrive/or-intelligence/results/qa/` (local run: `data/local_out/results/qa/`).
50 random images (seed 42) across all three splits, each checked for missing, wrong-class and badly placed boxes.

| # | Image | Issue | Severity |
|---|---|---|---|
| 1 | seg8k_video12_019982 | Hook shaft visible at the top right has no box (missing label in the source annotation) | Medium |
| 2 | t50_VID06_001817 | Only a specimen bag / white drain in view, no box — correct (bag is not a class), noted as a likely false-positive source | Info |
| 3 | t50_VID15_001846 | Specimen bag only, empty label — correct | Info |
| 4 | t50_VID15_000927, seg8k_video43_000405 | Boxes from long, diagonal shafts cover a large area (box = full instance outline) — expected for polygon → box, not an error | Info |
| 5 | t50_VID48_001202 | Hook under strong glare, box still correct | Info |

Checked: 50 / 50 · Label errors: 1 image with a missing box (2% of images; about 1 of ~75 boxes, ≈1.3% of boxes) — on the target (< 2%).

Conversion checks (all passed): every annotation has its frame (41,933/41,933), all class ids in 0–5, all coordinates in [0, 1],
no degenerate boxes, no malformed JSON; only label strings found were the 6 classes + `snare` (43, dropped).
