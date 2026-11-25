# Held-out test evaluation (Owner: Member B, WBS 3.2.1)

The test split was evaluated **exactly once**, on 2026-11-24, with `notebooks/02_Model.ipynb` step 7. The cell
refuses to run a second time once `results/test_metrics.json` exists.

- **Model:** baseline YOLOv8s (chosen on validation only, see [`experiments.md`](experiments.md))
- **Weights:** `weights/best.pt`, sha256 `02ac6525516efda1c628edf4c2dd1677cb7d79ff0aed52e31aaf9de1c3ed3741`
- **Test split:** 22 surgeries, 10,819 frames, 15,659 tool boxes; no surgery is shared with train or val
- **Settings:** `imgsz=640`, `conf=0.25`, IoU 0.7 NMS (Ultralytics default)
- **Machine-readable copy:** [`test_metrics.json`](test_metrics.json)

## Results

| Instrument | Test boxes | Precision | Recall | AP@0.5 | AP@0.5:0.95 |
|---|---|---|---|---|---|
| grasper | 8,701 | 0.923 | 0.858 | 0.885 | 0.743 |
| bipolar | 526 | 0.926 | 0.897 | 0.918 | 0.779 |
| hook | 4,848 | 0.990 | 0.973 | 0.983 | 0.886 |
| scissors | 149 | 0.787 | 0.711 | 0.711 | 0.655 |
| clipper | 326 | 0.965 | 0.855 | 0.908 | 0.846 |
| irrigator | 1,109 | 0.974 | 0.849 | 0.881 | 0.806 |
| **all** | 15,659 | **0.927** | **0.857** | **mAP@0.5 = 0.881** | **mAP@0.5:0.95 = 0.786** |

Validation for comparison: mAP@0.5 0.868, mAP@0.5:0.95 0.772. Test is slightly *higher* than val, so the model
generalises to unseen surgeries and was not overfitted to the validation set.

Note: the test metrics were computed at `conf=0.25` (the threshold the app uses), not Ultralytics' usual
`conf=0.001`. That makes the AP values slightly conservative compared with numbers in papers.

Speed on the L4 GPU: 1.9 ms inference + 1.2 ms pre/post-processing per 640 px image (≈ 320 images/s).

## Confidence threshold for the timeline (handed to Member C)

**`conf = 0.25`.** All metrics above use it. The validation F1–confidence curve
([`figures/val_F1_curve.png`](figures/val_F1_curve.png)) is flat between 0.2 and 0.7 (all-class F1 ≈ 0.84–0.85,
peak 0.85 at 0.53), so 0.25 loses almost nothing in F1 while keeping more recall for the timeline. Scissors is the
exception: its F1 peaks near conf 0.1 (≈ 0.52) and falls as the threshold rises, so a higher threshold hurts it
most. At 0.25 the test precision is ≥ 0.92 for every tool except scissors. The timeline smoothing (`configs/timeline.yaml`, Member C) then removes the
remaining single-frame false positives. Member C may raise the timeline `conf` (e.g. 0.4) during 4.1.3 tuning; the
detector output keeps everything ≥ 0.25 so that is possible without re-running inference.

## Failure analysis

From the normalised test confusion matrix ([`figures/test_confusion_matrix_normalized.png`](figures/test_confusion_matrix_normalized.png)):

| Failure | Size | Likely cause |
|---|---|---|
| **Scissors predicted as grasper** | 23% of scissors boxes | Both are thin two-jawed tools on a long shaft; scissors has only 450 training boxes vs 25,698 for grasper (imbalance ×54). When the jaws are closed or half hidden, the model picks the frequent class. |
| **Grasper missed** (predicted background) | 9% of grasper boxes | Grasper tips at the image edge or partly hidden behind tissue: 7.8% of all boxes cover < 1% of the image (EDA), mostly grasper. |
| **Irrigator missed** | 6% of irrigator boxes | Irrigator is a plain tube with no tip features; when only the shaft is visible it looks like background. |
| **False positives are mostly "grasper"** | 80% of all false positives | Any thin metallic object (part of another tool, the specimen bag, gauze edges, reflections) is most often called grasper, the dominant class. |
| Bipolar / clipper missed | 3% / 2% | Small numbers; mostly partly visible tools. |
| Hook | 98% correct | Best class: distinctive L-shaped tip and 12,675 training boxes. |

**What it means for the app:** hook, clipper, bipolar and irrigator timelines will be reliable. Scissors segments
can be shown as grasper, and short grasper gaps can appear when the tool is at the edge of the view. Temporal
smoothing (WBS 4.1.1) fills short gaps. Scissors needs the oversampling experiment (future work).

Validation-set view: scissors recall was only 0.31 on val (113 boxes, from few surgeries) against 0.71 on test
(149 boxes). Both splits are small for this class, so its numbers have a wide uncertainty.

### Example-image gallery

The 20 individual failure images (`figures/failures/`) were **not produced**. That needs the dataset unpacked in
Colab, and the time went to the other deliverables. The class-level analysis above comes from the full
15,659-box test set. The licence (see `docs/data/LICENSES_AND_ETHICS.md`) also forbids committing frames, so such a
gallery would stay in Drive.

## Figures

| File | What |
|---|---|
| `figures/test_PR_curve.png` | Precision–recall curve per class, test |
| `figures/test_P_curve.png` | Precision vs confidence, test |
| `figures/test_confusion_matrix_normalized.png` | Normalised confusion matrix, test (conf 0.25) |
| `figures/val_F1_curve.png` | F1 vs confidence, val (used to check the 0.25 threshold) |
| `figures/val_R_curve.png` | Recall vs confidence, val |
| `figures/val_confusion_matrix_normalized.png` | Normalised confusion matrix, val |
