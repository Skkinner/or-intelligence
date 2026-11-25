# Model card: OR Intelligence instrument detector v1 (Owner: Member B, WBS 3.3.2)

## Model

| | |
|---|---|
| Architecture | YOLOv8s (Ultralytics 8.4.218), 11.1 M parameters, 28.4 GFLOPs (fused) |
| Start point | COCO-pretrained `yolov8s.pt`, fine-tuned on 6 classes |
| Input | RGB frame, resized to 640 px |
| Output | boxes `[x1,y1,x2,y2]` (normalised) with class and confidence, see contract C4 |
| Classes | 0 grasper · 1 bipolar · 2 hook · 3 scissors · 4 clipper · 5 irrigator (`contracts/classes.json`) |
| Training | 38 epochs (best epoch 28, early stopping, patience 10), batch 16, seed 42, Google Colab NVIDIA L4, 2.26 h |
| Selection | best validation mAP@0.5 (see `experiments.md`) |

## Files

| File | Where | SHA-256 |
|---|---|---|
| `best.pt` (21.5 MB) | Team Drive `MyDrive/or-intelligence/weights/` | `02ac6525516efda1c628edf4c2dd1677cb7d79ff0aed52e31aaf9de1c3ed3741` |
| `best.onnx` (42.7 MB, exported from `best.pt`) | same folder | not recorded |

To use in the app: copy `best.pt` to `models/weights/best.pt` (gitignored). Weights are **never** committed to Git.
Check the file with `sha256sum models/weights/best.pt` (Windows: `certutil -hashfile models\weights\best.pt SHA256`).

## Training data

CholecInstanceSeg (frames from Cholec80, CholecT50 and CholecSeg8k), converted to boxes by Member A.
85 surgeries, 41,933 frames, 64,712 boxes; split by surgery (train 45 / val 18 / test 22 surgeries).
Licence **CC BY-NC-SA 4.0**, non-commercial research and education only. Details and citations:
`docs/data/LICENSES_AND_ETHICS.md`. Class imbalance: grasper 59.4% of boxes, scissors 1.1%.

## Metrics (held-out test split, 22 unseen surgeries, conf 0.25)

| | grasper | bipolar | hook | scissors | clipper | irrigator | **all** |
|---|---|---|---|---|---|---|---|
| Precision | 0.923 | 0.926 | 0.990 | 0.787 | 0.965 | 0.974 | **0.927** |
| Recall | 0.858 | 0.897 | 0.973 | 0.711 | 0.855 | 0.849 | **0.857** |
| AP@0.5 | 0.885 | 0.918 | 0.983 | 0.711 | 0.908 | 0.881 | **0.881** |

mAP@0.5:0.95 = 0.786. Full report: `EVALUATION.md`.
Speed: about 3 ms per frame on an NVIDIA L4. CPU speed: `BENCHMARK.md`.

## Known failure modes

- **Scissors is the weakest class** (AP 0.71). 23% of scissors are labelled grasper, because there are 54× fewer
  scissors examples than grasper examples. Timelines can show a scissors segment as grasper.
- **Grasper at the edge of the view** or behind tissue is missed in about 9% of cases.
- **Irrigator shaft only** (no tip in view) is missed in about 6% of cases.
- Most false positives are labelled grasper (thin metallic objects, other tools' shafts).
- Not tested on: smoke-heavy scenes as a separate group, other camera systems, robotic surgery, other procedures.

## Intended use

Educational review of **recorded laparoscopic cholecystectomy** videos: building the instrument timeline in
OR Intelligence so trainees and instructors can find moments quickly.

## Out of scope

- **Diagnosis or any clinical decision.** This is an educational tool, not a medical device. A human instructor
  always makes the judgment.
- Real-time use during surgery.
- Other procedures or instruments not in the 6 classes (e.g. specimen bag, snare, which were dropped).
- Commercial use (dataset licence is non-commercial).
- Real patient recordings without consent, ethics approval and de-identification (Saudi PDPL, see the licences doc).
