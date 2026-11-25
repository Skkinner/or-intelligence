# Experiments log (Owner: Member B, WBS 3.1.1 / 3.1.2)

Selection uses the **validation** split only. The test split was not touched until 3.2.1.
All runs: `notebooks/02_Model.ipynb`, Google Colab, NVIDIA L4 (22.5 GB), Ultralytics 8.4.218, torch 2.14.1 + CUDA 13.0.

## Data

`yolo_dataset.zip` from Member A (`01_Data.ipynb`): CholecInstanceSeg converted to YOLO boxes, video-level split.

| Split | Images | Boxes |
|---|---|---|
| train | 26,830 | 42,673 |
| val | 4,284 | 6,380 |
| test | 10,819 | 15,659 |

## Runs

| Run | Change vs baseline | Epochs (best) | val mAP@0.5 | val mAP@0.5:0.95 | min per-class AP@0.5 | Train time | Weights |
|---|---|---|---|---|---|---|---|
| **baseline** | (none) | 38 (best 28, early stop) | **0.868** | **0.772** | 0.442 (scissors) | 2.26 h | `runs/baseline/weights/best.pt` → `weights/best.pt` |
| exp01 oversample scissors/clipper | not run (see below) | n/a | n/a | n/a | n/a | n/a | n/a |

Baseline settings: `yolov8s.pt` (COCO-pretrained, 11.1 M parameters, 28.7 GFLOPs), `imgsz=640`, `epochs=50`,
`batch=16`, `patience=10`, `seed=42`, `deterministic=True`, all other Ultralytics defaults
(SGD/auto optimiser, mosaic, HSV and flip augmentation, `close_mosaic=10`, AMP).

Validation curve per epoch: [`baseline_val_per_epoch.csv`](baseline_val_per_epoch.csv). mAP@0.5 rises from 0.767
(epoch 1) to 0.868 (epoch 28) and then stays flat (0.855–0.867), so early stopping at epoch 38 lost nothing.

### Baseline, per class on val (best.pt)

| Instrument | Boxes | Precision | Recall | AP@0.5 | AP@0.5:0.95 |
|---|---|---|---|---|---|
| grasper | 4,017 | 0.936 | 0.892 | 0.944 | 0.794 |
| bipolar | 270 | 0.967 | 0.856 | 0.919 | 0.757 |
| hook | 1,759 | 0.986 | 0.977 | 0.993 | 0.904 |
| scissors | 113 | 0.814 | 0.310 | 0.442 | 0.402 |
| clipper | 99 | 0.958 | 0.949 | 0.972 | 0.923 |
| irrigator | 122 | 0.926 | 0.836 | 0.936 | 0.851 |
| **all** | 6,380 | 0.931 | 0.803 | **0.868** | **0.772** |

## Selection rationale

`02_Model.ipynb` step 6 compared all candidate runs on **val mAP@0.5** and chose **baseline**
(saved to `results/model_selection.json` in Drive).

The planned experiment (3.1.2) was to **oversample images that contain scissors or clipper**, following Member A's
EDA (scissors has 450 train boxes vs. 25,698 for grasper, an imbalance ratio of 54). The validation results confirm
scissors is the weak class (val recall 0.31). **It was not run.** One training run takes about 2.3 h on the L4, and
the time was used for the test evaluation, the weights release and integration before the Wednesday deadline.
Because the test split has already been used once (3.2.1), no new model can be chosen and re-reported on test now.

**Consequence:** WBS 3.1.2's "baseline + at least one experiment" acceptance criterion is **not met**. The
oversampling cell is already in the notebook (step 5, `RUN_EXPERIMENT`) and is the first item of future work.

## Note: the stray run in the notebook

Cell "RESUME after a disconnect" in the notebook shows a 100-epoch run on a 4-image dataset with mAP 0. It was
run after training had already finished; `last.pt` was no longer resumable, so Ultralytics started a new run on its
default `coco8.yaml` sample. That run saved to `/content/runs/detect/train` (not Drive), is not part of the
experiments and did not touch the baseline weights.
