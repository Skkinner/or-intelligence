# 3. Detection Model

<!-- Owner: Member B (WBS 8.1.2). Synthesises docs/model/experiments.md, EVALUATION.md, MODEL_CARD.md and BENCHMARK.md. -->

## 3.1 Model Choice

The detector finds the 6 instruments of Contract C1 (grasper, bipolar, hook, scissors, clipper, irrigator) in each
sampled video frame. We use **YOLOv8s** (Ultralytics), a one-stage detector, fine-tuned from COCO-pretrained weights:

- **Speed:** a full surgery (30–90 min) has to be processed in minutes so a reviewer can use the timeline the same
  day. YOLOv8s runs at about 3 ms per frame on a single GPU.
- **Size:** the "s" model (11.1 M parameters) is a good balance for ~27k training images; the "n" model is faster
  but weaker on small tools, and the "m" model would take roughly twice as long to train (the "s" run already took 2.3 h).
- **Tooling:** Ultralytics gives training, evaluation plots and ONNX export in one library, which fits our
  Google Colab workflow (`notebooks/02_Model.ipynb`).

Boxes (not segmentation masks) are enough: the timeline only needs to know *which* tool is visible *when*.

## 3.2 Training and Experiments

The model was trained on Member A's YOLO dataset (Section 2): 26,830 training and 4,284 validation frames from
different surgeries. Settings: input 640 px, batch 16, up to 50 epochs with early stopping (patience 10),
seed 42, deterministic mode, Ultralytics' default augmentation (mosaic, HSV colour, horizontal flip).
Training ran on an NVIDIA L4 GPU in Google Colab.

Training stopped after **38 epochs** (2.26 h); the best epoch was **28**. Validation mAP@0.5 rose from 0.767 after
the first epoch to **0.868** at epoch 28 and then stayed flat (0.855–0.867), so more epochs would not help.

| Run | val mAP@0.5 | val mAP@0.5:0.95 | Weakest class (val AP@0.5) |
|---|---|---|---|
| Baseline YOLOv8s | **0.868** | **0.772** | scissors 0.442 |

The model was selected on the validation split only. The planned second experiment, **oversampling frames that
contain scissors or clipper** (recommended by the EDA, imbalance ratio 54), was prepared in the notebook but **not
run** because of the time limit. It is the first item of future work.

## 3.3 Test Results

The chosen model was evaluated **once** on the held-out test split: 22 surgeries that were never used for training
or model selection (10,819 frames, 15,659 tool boxes), at the confidence threshold the app uses (0.25).

| Instrument | Test boxes | Precision | Recall | AP@0.5 | AP@0.5:0.95 |
|---|---|---|---|---|---|
| grasper | 8,701 | 0.923 | 0.858 | 0.885 | 0.743 |
| bipolar | 526 | 0.926 | 0.897 | 0.918 | 0.779 |
| hook | 4,848 | 0.990 | 0.973 | 0.983 | 0.886 |
| scissors | 149 | 0.787 | 0.711 | 0.711 | 0.655 |
| clipper | 326 | 0.965 | 0.855 | 0.908 | 0.846 |
| irrigator | 1,109 | 0.974 | 0.849 | 0.881 | 0.806 |
| **All** | **15,659** | **0.927** | **0.857** | **0.881** | **0.786** |

**Success measure 1 (instrument detection): mAP@0.5 = 0.881 on unseen surgeries.** Five of six instruments reach
AP@0.5 ≥ 0.88. The test score is slightly higher than validation (0.868), so the model generalises to new surgeries
and did not overfit the validation set.

![Precision–recall curve per instrument on the test split](figures/test_PR_curve.png)

**Confidence threshold.** On validation, the all-class F1 score is flat between confidence 0.2 and 0.7
(≈ 0.84–0.85). We use **0.25** for the app and hand all detections ≥ 0.25 to the timeline engine (Section 4),
where temporal smoothing removes isolated false positives.

## 3.4 Failure Analysis

![Normalised confusion matrix on the test split (columns = true class)](figures/test_confusion_matrix_normalized.png)

- **Scissors → grasper (23% of scissors).** Both are thin, two-jawed tools on a long shaft. With 54× fewer
  training examples, the model falls back to the frequent class when the jaws are closed or partly hidden.
  Scissors is also the most uncertain number: val has 113 and test 149 scissors boxes (val recall 0.31, test 0.71).
- **Missed graspers (9%).** Mostly small grasper tips at the edge of the view or behind tissue; 7.8% of all boxes
  cover less than 1% of the image.
- **Missed irrigators (6%).** When only the plain shaft is visible, the tool has few distinctive features.
- **False positives** are mostly labelled grasper (80% of them), the dominant class.
- **Hook** is almost perfect (98% correct): it has a distinctive tip and many training examples.

For the product this means: timelines for hook, clipper, bipolar and irrigator are reliable; a scissors segment
may appear as grasper; short grasper gaps are filled by the smoothing step.

## 3.5 Inference and Speed

`src/inference/detect_video.py` samples a video at a chosen rate (default 5 fps), runs the detector on each sampled
frame and writes one JSON line per frame (Contract C4). The API (Section 4) imports this function.

On an NVIDIA L4, the model needs about **3.1 ms per frame** (1.9 ms inference + 1.2 ms pre/post-processing,
measured during test evaluation). On a CPU-only laptop (Intel i7-1165G7) the full pipeline, including 1080p
video decoding, needs **6 s per video-minute at 1 fps** and 36 s at 5 fps, so a 30-minute surgery is ready in about
3 minutes at 1 fps. The output for a 1080p test clip validated against the Contract C4 schema. We recommend 5 fps on
a GPU and 1 fps on a CPU (`docs/model/BENCHMARK.md`).

## 3.6 Limitations and Future Work

- **One experiment was not run.** Oversampling scissors/clipper (already in the notebook) should raise scissors
  recall; a larger input size (832 px) may help small grasper tips.
- **One procedure only.** Trained and tested on laparoscopic cholecystectomy from the Strasbourg-based Cholec
  datasets; other hospitals' cameras or other procedures are untested.
- **Non-commercial data licence** (CC BY-NC-SA 4.0): the weights inherit this restriction.
- **Educational, not diagnostic.** The model card (`docs/model/MODEL_CARD.md`) lists intended and out-of-scope uses.
