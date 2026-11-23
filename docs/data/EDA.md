# Exploratory data analysis (Owner: Member A, WBS 2.4.1)

Dataset: CholecInstanceSeg → YOLO boxes (one box per tool instance, Snare dropped), split by surgery as in
`data/splits/splits.json` (the dataset's recommended split; no surgery in two splits).

Regenerate figures: re-run `notebooks/01_Data.ipynb` step 6 (saved to `MyDrive/or-intelligence/results/eda/`, or
`data/local_out/results/eda/` when run locally; copy into `figures/`). Numbers below are from the local run of 2026-11-23.

## Split summary

| Split | Surgeries | Images | Images with no tool | Boxes |
|---|---|---|---|---|
| train | 45 | 26,830 | 2,542 (9.5%) | 42,673 |
| val | 18 | 4,284 | 542 (12.7%) | 6,380 |
| test | 22 | 10,819 | 1,830 (16.9%) | 15,659 |
| **total** | 85 | 41,933 | 4,914 (11.7%) | 64,712 |

(55 train folders are 45 surgeries: 10 surgeries appear both as a CholecSeg8k and a CholecT50 folder.)

## Boxes per class per split

| Class | train | val | test | total | share |
|---|---|---|---|---|---|
| grasper | 25,698 | 4,017 | 8,701 | 38,416 | 59.4% |
| bipolar | 1,762 | 270 | 526 | 2,558 | 4.0% |
| hook | 12,675 | 1,759 | 4,848 | 19,282 | 29.8% |
| scissors | 450 | 113 | 149 | 712 | 1.1% |
| clipper | 899 | 99 | 326 | 1,324 | 2.0% |
| irrigator | 1,189 | 122 | 1,109 | 2,420 | 3.7% |

## Figures

- `figures/boxes_per_class_per_split.png` (+ `boxes_per_class_per_split.csv`)
- `figures/images_per_video.png`
- `figures/box_size_distribution.png`
- `figures/class_cooccurrence.png`

## Key numbers

- Imbalance ratio (max/min class): **53.96** (grasper 38,416 vs scissors 712)
- Small-object share: **7.8%** of boxes cover < 1% of the image; grasper has the smallest median box (~5% of the image), the other tools ~10–15%.
- Images per surgery are very uneven: the 15 densely annotated CholecT50 videos have 1,000–3,100 frames each, the sparse ones 55–240. A few surgeries dominate train (VID01, VID43, VID52, VID27, VID25 ≈ 13.8k of 26.8k frames).
- Co-occurrence: grasper + hook is the usual pair (13,253 images); hook never appears with clipper or scissors, and bipolar with hook only once. Tools are mostly used one at a time besides the grasper.
- Label sources: 40,172 grasper polygons became 38,416 boxes (several polygons of one occluded instance are merged); 43 Snare instances dropped.

## Recommendations for Member B (3.1.2)

- **Rare classes:** scissors (450 train boxes) and clipper (899) are the weak spots. Oversample images containing them (e.g. repeat ×5 / ×3, or a class-balanced sampler) rather than reweighting the loss only, and report per-class AP: overall mAP will be driven by grasper and hook.
- **Validation is thin for rare classes** (val: 99 clipper, 113 scissors, 122 irrigator boxes) → per-class val AP will be noisy; pick the checkpoint on overall mAP50-95, not on a single rare class.
- **Frame redundancy:** the dense 1 fps videos give many near-duplicate frames. Consider subsampling them (e.g. every 2nd–3rd frame) per epoch so the sparse surgeries are not drowned out; the full set is still available for the final run.
- **Small objects:** 7.8% of boxes < 1% of the image (mostly grasper tips at the edge) → keep input size ≥ 640 and do not crop aggressively.
- **Background images** (11.7%) are kept with empty labels; they help against false positives on the specimen bag and gauze, which are not classes.
- **Do not tune on test** — VID14/15/22/29 in test are also the timeline reporting videos (2.3.1).
