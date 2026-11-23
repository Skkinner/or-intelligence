# Team Tasks

> **OR Intelligence** · Computer Vision Final Project · Deadline **Wednesday 25 Nov 2026, 23:59**  
> Generated from `docs/planning/wbs_data.json` by `scripts/github/generate.mjs`. Names/usernames live in `.github/team.json`.

Each member owns a disjoint set of files. **Edit only your own paths**; everything else is read-only for you.
Every task is a GitHub Issue titled `[WBS x.y.z] …` with the label `member:<a|b|c|d>`.

## Overview

| Member | Role | Tasks | Hours | Branch prefix | Issues |
|---|---|---|---|---|---|
| Member A | Data Engineer & UX Research | 10 | 23 | `feature/member-a-` | label `member:a` |
| Member B | ML Engineer | 8 | 24 | `feature/member-b-` | label `member:b` |
| Member C | Backend & Timeline Engineer | 8 | 25 | `feature/member-c-` | label `member:c` |
| Member D | Frontend Lead & Integration Owner | 12 | 31 | `feature/member-d-` | label `member:d` |

Work blocks: **1** Mon 23 Nov Evening (18:00–23:00) · **2** Tue 24 Nov Morning (09:00–13:00) · **3** Tue 24 Nov Afternoon (14:00–18:00) · **4** Tue 24 Nov Evening (19:00–23:00) · **5** Wed 25 Nov Morning (09:00–13:00) · **6** Wed 25 Nov Afternoon (14:00–18:00) · **7** Wed 25 Nov Evening (19:00–23:59)

---

## Member A: Data Engineer & UX Research

Owns all data: acquisition, licences, YOLO-format conversion, the video-level split and the timeline ground truth. Later owns the analytics page, Arabic localisation and the usability study.

**Load:** 10 tasks · 23 h

### Start here

```bash
git clone <repo-url> && cd or-intelligence
git switch develop
git switch -c feature/member-a-1.3.1-licensing
```

### Your files (edit only these)

- `data/splits/splits.json`
- `docs/data/`
- `docs/data/EDA.md`
- `docs/data/figures/`
- `docs/data/qa_notes.md`
- `docs/data/timeline_eval_set.md`
- `docs/report/01_data.md`
- `docs/usability/`
- `notebooks/01_Data.ipynb`
- `requirements/data.txt`
- `src/data/extract_frames.py`
- `src/data/presence_labels.py`
- `web/src/i18n/ar.json`
- `web/src/i18n/parity.test.ts`
- `web/src/pages/Analytics/`
- `web/src/styles/rtl.css`

### Do not modify

- src/models/
- src/inference/
- src/timeline/
- src/api/
- src/reports/
- contracts/ (propose changes by PR to Member D)
- web/src/ except the Analytics page, ar.json and rtl.css

### You receive

- **1.2.1** Repository scaffold, branch protection & CI skeleton from Member D (Mon 23 Nov Evening)
- **1.2.2** Interface contracts & shared test fixtures from Member D (Mon 23 Nov Evening)
- **5.1.1** Web app shell, API client & upload flow from Member D (Tue 24 Nov Morning)
- **7.1.1** One-command local run & integration from Member D (Wed 25 Nov Morning → Wed 25 Nov Afternoon)

### Your tasks

| WBS | Task | When | h | Priority | Branch | Depends on |
|---|---|---|---|---|---|---|
| 1.3.1 | Dataset licensing & ethics checklist | Mon 23 Nov Evening | 1 | High | `feature/member-a-1.3.1-licensing` | — |
| 2.1.1 | Download & verify datasets | Mon 23 Nov Evening | 2 | High | `feature/member-a-2.1.1-download` | 1.3.1, 1.2.1 |
| 2.2.1 | VOC → YOLO conversion & class mapping | Mon 23 Nov Evening → Tue 24 Nov Morning | 3 | High | `feature/member-a-2.2.1-voc-to-yolo` | 2.1.1, 1.2.2 |
| 2.2.2 ⚠ | Video-level train/val/test split | Tue 24 Nov Morning | 1 | High | `feature/member-a-2.2.2-split` | 2.2.1 |
| 2.3.1 | Timeline ground truth from Cholec80 presence labels | Tue 24 Nov Morning → Tue 24 Nov Afternoon | 3 | High | `feature/member-a-2.3.1-presence-gt` | 2.1.1 |
| 2.4.1 | EDA & class-balance report | Tue 24 Nov Afternoon | 2 | Medium | `feature/member-a-2.4.1-eda` | 2.2.2 |
| 5.2.2 | Analytics dashboard page | Tue 24 Nov Evening → Wed 25 Nov Morning | 4 | Medium | `feature/member-a-5.2.2-analytics` | 5.1.1 |
| 5.2.3 | Arabic localisation & RTL styling | Wed 25 Nov Morning | 2 | Medium | `feature/member-a-5.2.3-arabic` | 5.1.1 |
| 6.2.1 | Usability study: scrubbing vs timeline | Wed 25 Nov Afternoon → Wed 25 Nov Evening | 3 | High | `feature/member-a-6.2.1-usability` | 7.1.1 |
| 8.1.1 | Report section: Data | Wed 25 Nov Evening | 2 | Medium | `feature/member-a-8.1.1-report-data` | 2.4.1, 6.2.1 |

#### 1.3.1 Dataset licensing & ethics checklist

Confirm which datasets may be used, under what licence, how to cite them, and record the educational/non-diagnostic scope. Blocks any data download.

**Files:** `docs/data/`  
**Deliverables:** docs/data/LICENSES_AND_ETHICS.md  
**Inputs:** Dataset web pages / licence texts

Completion checklist:
- [ ] Document lists licence, citation and allowed use for every dataset used.
- [ ] Reviewed and approved by D in PR.
- [ ] Explicit rule: no raw video or frames committed to Git.
- [ ] PR merged into `develop`; issue closed

#### 2.1.1 Download & verify datasets

Get the m2cai16-tool-locations dataset (frames + VOC XML boxes) into the team Google Drive and check it in notebooks/01_Data.ipynb (step 3). Cholec80 only if access already exists (decided in 1.3.1).

**Files:** `notebooks/01_Data.ipynb`, `requirements/data.txt`  
**Deliverables:** Dataset zip in the shared Drive folder; Counts + SHA-256 recorded in docs/data/LICENSES_AND_ETHICS.md  
**Inputs:** docs/data/LICENSES_AND_ETHICS.md (approved)

Completion checklist:
- [ ] 01_Data.ipynb step 3 runs and the printed counts match the dataset documentation.
- [ ] The whole team can open the shared Drive folder.
- [ ] Nothing under data/ is tracked by Git.
- [ ] PR merged into `develop`; issue closed

#### 2.2.1 VOC → YOLO conversion & class mapping

Convert the Pascal-VOC boxes into YOLO labels for the 6 instruments (drop SpecimenBag) with visual spot-checks, in notebooks/01_Data.ipynb (step 4).

**Files:** `notebooks/01_Data.ipynb`, `docs/data/qa_notes.md`  
**Deliverables:** YOLO labels (inside the notebook run); docs/data/qa_notes.md  
**Inputs:** Dataset zip in Drive (2.1.1); contracts/classes.json

Completion checklist:
- [ ] Every image has exactly one label (possibly empty).
- [ ] The notebook's checks pass: class ids ∈ {0..5}, coordinates ∈ [0,1].
- [ ] ≥50 visual spot-checks recorded in qa_notes.md with <2% label errors.
- [ ] PR merged into `develop`; issue closed

#### 2.2.2 Video-level train/val/test split

Split by source video (never by frame) so the test set measures generalisation to unseen surgeries, then hand the ready dataset to B through Drive (01_Data.ipynb steps 5 and 7).

**Files:** `notebooks/01_Data.ipynb`, `data/splits/splits.json`  
**Deliverables:** MyDrive/or-intelligence/data/yolo_dataset.zip; data/splits/splits.json; Split summary table in PR  
**Inputs:** Converted labels (2.2.1)

Completion checklist:
- [ ] Leakage check in the notebook passes (no video in two splits).
- [ ] Each split contains every class at least 20 times.
- [ ] 02_Model.ipynb step 3 loads yolo_dataset.zip without errors.
- [ ] PR merged into `develop`; issue closed

Hand-off: tag Member B in the PR (needed for 3.1.1).

#### 2.3.1 Timeline ground truth from Cholec80 presence labels

Prepare a held-out set of full surgery videos with per-second tool-presence labels, used to measure timeline agreement (success measure 2). Videos must not overlap with the detector's training videos. Source is Cholec80 or the m2cai16-tool fallback (decided in 1.3.1).

**Files:** `src/data/presence_labels.py`, `src/data/extract_frames.py`, `docs/data/timeline_eval_set.md`  
**Deliverables:** data/processed/presence/<video_id>.csv; docs/data/timeline_eval_set.md; src/data/presence_labels.py; src/data/extract_frames.py  
**Inputs:** data/raw/cholec80/

Completion checklist:
- [ ] Each CSV matches contract C3 (header + 0/1 values).
- [ ] Row counts within ±2 s of video length.
- [ ] Overlap check with training videos documented.
- [ ] PR merged into `develop`; issue closed

Hand-off: tag Member C in the PR (needed for 4.1.3).

#### 2.4.1 EDA & class-balance report

Quantify the dataset so B can plan augmentation and class weighting, and so the report has a data section (01_Data.ipynb step 6).

**Files:** `notebooks/01_Data.ipynb`, `docs/data/EDA.md`, `docs/data/figures/`  
**Deliverables:** docs/data/EDA.md; docs/data/figures/*.png  
**Inputs:** Split dataset (2.2.2)

Completion checklist:
- [ ] EDA.md contains per-class counts per split and at least 4 figures.
- [ ] Recommendations section addressed to B is present.
- [ ] Figures regenerate by re-running 01_Data.ipynb.
- [ ] PR merged into `develop`; issue closed

Hand-off: tag Member B in the PR (needed for 3.1.2, 8.2.1).

#### 5.2.2 Analytics dashboard page

Use case 5: compare per-case statistics (time per instrument, total time, switches) across selected videos.

**Files:** `web/src/pages/Analytics/`  
**Deliverables:** web/src/pages/Analytics/  
**Inputs:** contracts/openapi.yaml (analytics); tests/fixtures/sample_timeline.json

Completion checklist:
- [ ] Selecting 3 fixture cases shows correct per-tool totals (match API JSON).
- [ ] CSV export opens in Excel with correct columns.
- [ ] No files outside web/src/pages/Analytics/ changed in the PR.
- [ ] PR merged into `develop`; issue closed

Hand-off: tag Member D in the PR (needed for 7.1.1).

#### 5.2.3 Arabic localisation & RTL styling

Complete Arabic translation of all UI strings and RTL layout fixes, matching the bilingual product promise.

**Files:** `web/src/i18n/ar.json`, `web/src/styles/rtl.css`, `web/src/i18n/parity.test.ts`  
**Deliverables:** web/src/i18n/ar.json; web/src/styles/rtl.css; web/src/i18n/parity.test.ts  
**Inputs:** web/src/i18n/en.json (D)

Completion checklist:
- [ ] Key parity test passes (en ↔ ar).
- [ ] All pages usable in Arabic with no clipped or mirrored-wrong elements (screenshots in PR).
- [ ] Arabic PDF reviewed and approved.
- [ ] PR merged into `develop`; issue closed

Hand-off: tag Member D in the PR (needed for 7.1.1).

#### 6.2.1 Usability study: scrubbing vs timeline

Success measure 3. Within-subject test: participants find specific moments (e.g. first clipper use) by manual scrubbing vs with the OR Intelligence timeline.

**Files:** `docs/usability/`  
**Deliverables:** docs/usability/PROTOCOL.md; docs/usability/results.csv; docs/usability/RESULTS.md  
**Inputs:** Running release candidate (7.1.1)

Completion checklist:
- [ ] ≥3 participants completed both conditions.
- [ ] Median time-to-find reported for both conditions, labelled as a pilot.
- [ ] Data anonymous.
- [ ] PR merged into `develop`; issue closed

#### 8.1.1 Report section: Data

Final report chapter on datasets, licences, preprocessing, split, EDA and timeline ground truth.

**Files:** `docs/report/01_data.md`  
**Deliverables:** docs/report/01_data.md  
**Inputs:** docs/data/*; docs/usability/RESULTS.md

Completion checklist:
- [ ] Section complete, figures referenced, citations present.
- [ ] Reviewed by D.
- [ ] PR merged into `develop`; issue closed

Hand-off: tag Member D in the PR (needed for 8.1.4).

---

## Member B: ML Engineer

Owns the detector: training, tuning, evaluation, the video inference module that produces detections.jsonl, the model card, the performance benchmark and the slide deck.

**Load:** 8 tasks · 24 h

### Start here

```bash
git clone <repo-url> && cd or-intelligence
git switch develop
git switch -c feature/member-b-3.1.1-baseline
```

### Your files (edit only these)

- `docs/model/BENCHMARK.md`
- `docs/model/EVALUATION.md`
- `docs/model/MODEL_CARD.md`
- `docs/model/experiments.md`
- `docs/model/figures/`
- `docs/model/test_metrics.json`
- `docs/report/02_model.md`
- `docs/slides/`
- `models/weights/`
- `notebooks/02_Model.ipynb`
- `requirements/ml.txt`
- `src/inference/`
- `src/models/benchmark.py`
- `tests/unit/inference/`

### Do not modify

- src/data/ and data/ (read-only consumer)
- src/timeline/
- src/api/
- src/reports/
- web/
- contracts/ (propose changes by PR)

### You receive

- **2.2.2** Video-level train/val/test split from Member A (Tue 24 Nov Morning)
- **2.4.1** EDA & class-balance report from Member A (Tue 24 Nov Afternoon)
- **1.2.2** Interface contracts & shared test fixtures from Member D (Mon 23 Nov Evening)
- **4.1.3** Timeline evaluation vs ground truth from Member C (Wed 25 Nov Morning → Wed 25 Nov Afternoon)

### Your tasks

| WBS | Task | When | h | Priority | Branch | Depends on |
|---|---|---|---|---|---|---|
| 3.1.1 | Baseline YOLO training | Tue 24 Nov Morning → Tue 24 Nov Afternoon | 4 | High | `feature/member-b-3.1.1-baseline` | 2.2.2 |
| 3.1.2 | Augmentation & hyper-parameter experiments | Tue 24 Nov Evening | 4 | High | `feature/member-b-3.1.2-tuning` | 3.1.1, 2.4.1 |
| 3.2.1 | Held-out test evaluation report | Wed 25 Nov Morning | 3 | High | `feature/member-b-3.2.1-eval` | 3.1.2 |
| 3.3.1 ⚠ | Video inference module (detections.jsonl) | Mon 23 Nov Evening → Tue 24 Nov Afternoon | 5 | High | `feature/member-b-3.3.1-inference` | 1.2.2 |
| 3.3.2 | Model card & weights release | Wed 25 Nov Morning | 1 | Medium | `feature/member-b-3.3.2-model-card` | 3.2.1 |
| 6.1.1 | Inference performance benchmark | Wed 25 Nov Afternoon | 1 | Low | `feature/member-b-6.1.1-benchmark` | 3.3.2, 4.1.3 |
| 8.1.2 | Report section: Model | Wed 25 Nov Afternoon | 2 | Medium | `feature/member-b-8.1.2-report-model` | 3.2.1, 6.1.1 |
| 8.2.1 | Presentation slide deck | Wed 25 Nov Afternoon → Wed 25 Nov Evening | 4 | High | `feature/member-b-8.2.1-slides` | 2.4.1, 3.2.1, 4.1.3 |

#### 3.1.1 Baseline YOLO training

Fine-tune a COCO-pretrained YOLO (yolov8s) on the 6-class dataset in notebooks/02_Model.ipynb (steps 1–4) to establish a baseline.

**Files:** `notebooks/02_Model.ipynb`, `requirements/ml.txt`, `docs/model/experiments.md`  
**Deliverables:** MyDrive/or-intelligence/runs/baseline/weights/best.pt; docs/model/experiments.md  
**Inputs:** MyDrive/or-intelligence/data/yolo_dataset.zip (2.2.2); contracts/classes.json

Completion checklist:
- [ ] Baseline val mAP@0.5 recorded in experiments.md.
- [ ] Weights are in the shared Drive folder.
- [ ] Re-running the notebook with the same settings reproduces the run (seed 42).
- [ ] PR merged into `develop`; issue closed

#### 3.1.2 Augmentation & hyper-parameter experiments

Improve on the baseline using A's EDA (02_Model.ipynb steps 5–6). Select the final model on the validation split only.

**Files:** `notebooks/02_Model.ipynb`, `models/weights/`  
**Deliverables:** Chosen model (results/model_selection.json in Drive); Experiment table in docs/model/experiments.md  
**Inputs:** Baseline run (3.1.1); docs/data/EDA.md

Completion checklist:
- [ ] Baseline + at least 1 experiment logged with settings and results.
- [ ] Final model's val mAP@0.5 ≥ baseline.
- [ ] Chosen by Tue 23:00; selection rationale written; test split untouched.
- [ ] PR merged into `develop`; issue closed

#### 3.2.1 Held-out test evaluation report

One-time evaluation of the chosen model on the video-level test split (02_Model.ipynb step 7): mAP@0.5, mAP@0.5:0.95, per-instrument precision/recall, failure analysis.

**Files:** `docs/model/EVALUATION.md`, `docs/model/test_metrics.json`, `docs/model/figures/`  
**Deliverables:** docs/model/EVALUATION.md; docs/model/test_metrics.json; docs/model/figures/  
**Inputs:** Chosen model (3.1.2); Test split in yolo_dataset.zip

Completion checklist:
- [ ] Report includes mAP@0.5 and P/R for all 6 instruments on the test split.
- [ ] Test split evaluated exactly once (stated in report).
- [ ] Recommended conf threshold communicated to C in the PR.
- [ ] PR merged into `develop`; issue closed

Hand-off: tag Member D in the PR (needed for 7.2.1).

#### 3.3.1 Video inference module (detections.jsonl)

detect_video(): samples a video at N fps, runs the detector and writes detections in contract C4 format. Implemented in src/inference/detect_video.py (used by the app) and in 02_Model.ipynb step 9 (for Colab).

**Files:** `src/inference/`, `tests/unit/inference/`  
**Deliverables:** src/inference/detect_video.py; src/inference/README.md; tests/unit/inference/  
**Inputs:** yolov8n.pt (stand-in), later best.pt; contracts/detections.schema.json; tests/fixtures/sample_video.mp4

Completion checklist:
- [ ] Output for the fixture video validates against the schema.
- [ ] Progress callback reaches 1.0.
- [ ] Processes a 2-min 1080p clip at 5 fps in < 2 min on the target GPU (documented).
- [ ] PR merged into `develop`; issue closed

Hand-off: tag Member C in the PR (needed for 4.1.3).

#### 3.3.2 Model card & weights release

Publish the final weights to the team (Drive + optionally a GitHub Release) with a model card describing data, metrics, limits and intended (educational) use.

**Files:** `docs/model/MODEL_CARD.md`  
**Deliverables:** MyDrive/or-intelligence/weights/best.pt (+ .onnx, .sha256); docs/model/MODEL_CARD.md  
**Inputs:** docs/model/EVALUATION.md; Chosen model (3.1.2)

Completion checklist:
- [ ] best.pt and its SHA-256 are in the shared Drive folder and C can load it.
- [ ] Model card states non-diagnostic, educational scope.
- [ ] PR merged into `develop`; issue closed

Hand-off: tag Member D in the PR (needed for 7.1.1).

#### 6.1.1 Inference performance benchmark

Measure processing time and resource use for realistic video lengths to set user expectations and choose sample_fps.

**Files:** `src/models/benchmark.py`, `docs/model/BENCHMARK.md`  
**Deliverables:** docs/model/BENCHMARK.md; src/models/benchmark.py  
**Inputs:** models/weights/best.pt; src/inference/; src/timeline/evaluate.py

Completion checklist:
- [ ] Table of processing seconds per video-minute for each fps setting.
- [ ] Recommended default sample_fps stated.
- [ ] PR merged into `develop`; issue closed

Hand-off: tag Member D in the PR (needed for 8.1.4).

#### 8.1.2 Report section: Model

Chapter on detector choice, training, experiments, test results, failure analysis and benchmark.

**Files:** `docs/report/02_model.md`  
**Deliverables:** docs/report/02_model.md  
**Inputs:** docs/model/*

Completion checklist:
- [ ] mAP@0.5 and per-class P/R table present.
- [ ] Reviewed by D.
- [ ] PR merged into `develop`; issue closed

Hand-off: tag Member D in the PR (needed for 8.1.4).

#### 8.2.1 Presentation slide deck

10–15 minute presentation: problem, approach, results (3 success measures), demo screenshots, business model, limits.

**Files:** `docs/slides/`  
**Deliverables:** docs/slides/OR_Intelligence.pptx (or PDF)  
**Inputs:** docs/data/EDA.md; docs/model/EVALUATION.md; docs/timeline/TIMELINE_EVAL.md; 1.1.1 page

Completion checklist:
- [ ] Deck covers problem, solution, 3 success-measure results, demo, business model, limits.
- [ ] Rehearsal within time limit.
- [ ] PR merged into `develop`; issue closed

---

## Member C: Backend & Timeline Engineer

Owns everything between detections and the browser: temporal smoothing, interval building and statistics, timeline evaluation, the FastAPI service, notes/search/analytics endpoints and the PDF report.

**Load:** 8 tasks · 25 h

### Start here

```bash
git clone <repo-url> && cd or-intelligence
git switch develop
git switch -c feature/member-c-4.1.1-smoothing
```

### Your files (edit only these)

- `configs/timeline.yaml`
- `docs/demo/`
- `docs/report/03_system.md`
- `docs/timeline/`
- `requirements/api.txt`
- `src/api/db.py`
- `src/api/jobs.py`
- `src/api/main.py`
- `src/api/routes/analytics.py`
- `src/api/routes/notes.py`
- `src/api/routes/reports.py`
- `src/api/routes/search.py`
- `src/api/routes/videos.py`
- `src/reports/`
- `src/timeline/builder.py`
- `src/timeline/evaluate.py`
- `src/timeline/smoothing.py`
- `tests/unit/api/`
- `tests/unit/reports/`
- `tests/unit/timeline/`

### Do not modify

- src/data/
- src/models/
- src/inference/ (call it, never edit it)
- web/
- contracts/ (propose changes by PR)
- docker/ and docker-compose.yml

### You receive

- **1.2.2** Interface contracts & shared test fixtures from Member D (Mon 23 Nov Evening)
- **2.3.1** Timeline ground truth from Cholec80 presence labels from Member A (Tue 24 Nov Morning → Tue 24 Nov Afternoon)
- **3.3.1** Video inference module (detections.jsonl) from Member B (Mon 23 Nov Evening → Tue 24 Nov Afternoon)
- **7.2.1** Release candidate v1.0.0 & demo freeze from Member D (Wed 25 Nov Evening)

### Your tasks

| WBS | Task | When | h | Priority | Branch | Depends on |
|---|---|---|---|---|---|---|
| 4.1.1 | Temporal smoothing | Mon 23 Nov Evening | 3 | High | `feature/member-c-4.1.1-smoothing` | 1.2.2 |
| 4.1.2 | Interval builder & per-case statistics | Tue 24 Nov Morning | 3 | High | `feature/member-c-4.1.2-builder` | 4.1.1 |
| 4.1.3 | Timeline evaluation vs ground truth | Wed 25 Nov Morning → Wed 25 Nov Afternoon | 3 | High | `feature/member-c-4.1.3-timeline-eval` | 4.1.2, 2.3.1, 3.3.1 |
| 4.2.1 ⚠ | FastAPI service & background processing jobs | Mon 23 Nov Evening → Tue 24 Nov Afternoon | 5 | High | `feature/member-c-4.2.1-api` | 1.2.2 |
| 4.2.2 | Notes, search & analytics endpoints | Tue 24 Nov Evening | 3 | Medium | `feature/member-c-4.2.2-notes-search` | 4.2.1 |
| 4.3.1 | PDF report generator (English & Arabic) | Tue 24 Nov Evening → Wed 25 Nov Morning | 4 | Medium | `feature/member-c-4.3.1-pdf` | 4.1.2, 4.2.2 |
| 8.1.3 | Report section: Timeline & System | Wed 25 Nov Afternoon | 2 | Medium | `feature/member-c-8.1.3-report-system` | 4.1.3, 4.3.1 |
| 8.2.2 | Demo video | Wed 25 Nov Evening | 2 | Medium | `feature/member-c-8.2.2-demo` | 7.2.1 |

#### 4.1.1 Temporal smoothing

Turn noisy per-frame detections into stable per-tool presence signals: confidence threshold, per-tool max-confidence per frame, sliding-window vote / hysteresis.

**Files:** `src/timeline/smoothing.py`, `configs/timeline.yaml`, `tests/unit/timeline/`, `requirements/api.txt`  
**Deliverables:** src/timeline/smoothing.py; configs/timeline.yaml; tests/unit/timeline/test_smoothing.py  
**Inputs:** tests/fixtures/sample_detections.jsonl; contracts/detections.schema.json

Completion checklist:
- [ ] Unit tests pass.
- [ ] On the fixture, number of segments drops by ≥50% versus raw thresholding with no segment >2 s lost.
- [ ] PR merged into `develop`; issue closed

#### 4.1.2 Interval builder & per-case statistics

Convert smoothed presence into contract C5 timeline: intervals per tool (merge small gaps, drop tiny segments), per-tool time, segment counts, tool switches.

**Files:** `src/timeline/builder.py`  
**Deliverables:** src/timeline/builder.py; timeline.json (per video)  
**Inputs:** src/timeline/smoothing.py; contracts/timeline.schema.json

Completion checklist:
- [ ] Output validates against schema.
- [ ] Hand-computed stats for the fixture match the module output.
- [ ] Switch definition documented.
- [ ] PR merged into `develop`; issue closed

#### 4.1.3 Timeline evaluation vs ground truth

Measure success measure 2: agreement between predicted tool intervals and Cholec80 presence labels on the timeline evaluation videos; tune smoothing params on a subset.

**Files:** `src/timeline/evaluate.py`, `docs/timeline/`  
**Deliverables:** src/timeline/evaluate.py; docs/timeline/TIMELINE_EVAL.md; Tuned configs/timeline.yaml  
**Inputs:** data/processed/presence/*.csv (2.3.1); src/inference/detect_video.py (3.3.1); models/weights/best.pt or baseline.pt

Completion checklist:
- [ ] Per-tool F1 table for raw vs smoothed on held-out timeline videos.
- [ ] Tuning and reporting videos are disjoint (stated).
- [ ] Smoothed macro-F1 ≥ raw macro-F1.
- [ ] PR merged into `develop`; issue closed

Hand-off: tag Member B, Member D in the PR (needed for 6.1.1, 7.2.1, 8.2.1).

#### 4.2.1 FastAPI service & background processing jobs

HTTP service implementing upload, status, video streaming and timeline endpoints from contracts/openapi.yaml, with a background worker that runs inference → timeline.

**Files:** `src/api/main.py`, `src/api/db.py`, `src/api/jobs.py`, `src/api/routes/videos.py`, `tests/unit/api/`  
**Deliverables:** src/api/main.py; src/api/db.py; src/api/jobs.py; src/api/routes/videos.py; tests/unit/api/  
**Inputs:** contracts/openapi.yaml; src/timeline/builder.py; src/inference/detect_video.py (via import)

Completion checklist:
- [ ] All video endpoints in openapi.yaml implemented; responses validate.
- [ ] Fixture-mode upload reaches status done in tests.
- [ ] Real mode works with best.pt on the sample video.
- [ ] PR merged into `develop`; issue closed

#### 4.2.2 Notes, search & analytics endpoints

Endpoints for timestamped notes (use case 2), instrument search across the library (use case 3) and per-case stats comparison (use case 5).

**Files:** `src/api/routes/notes.py`, `src/api/routes/search.py`, `src/api/routes/analytics.py`  
**Deliverables:** src/api/routes/notes.py; src/api/routes/search.py; src/api/routes/analytics.py  
**Inputs:** src/api/ (4.2.1); contracts/openapi.yaml

Completion checklist:
- [ ] Searching tool=clipper on fixtures returns exactly the clipper segments.
- [ ] Notes persist across server restart.
- [ ] Route tests pass in CI.
- [ ] PR merged into `develop`; issue closed

Hand-off: tag Member D in the PR (needed for 7.1.1).

#### 4.3.1 PDF report generator (English & Arabic)

Generate a session report: case info, timeline bar chart, per-tool stats, instructor notes with timestamps, disclaimer; in EN or AR (RTL).

**Files:** `src/reports/`, `src/api/routes/reports.py`, `tests/unit/reports/`  
**Deliverables:** src/reports/pdf_report.py; src/reports/strings.py; src/reports/fonts/; src/api/routes/reports.py  
**Inputs:** contracts/timeline.schema.json; tests/fixtures/sample_timeline.json

Completion checklist:
- [ ] EN and AR PDFs render with correct Arabic shaping and RTL layout (visual check by A).
- [ ] Report includes timeline chart, stats, notes and the 'educational, not diagnostic' disclaimer.
- [ ] Endpoint returns application/pdf.
- [ ] PR merged into `develop`; issue closed

Hand-off: tag Member D in the PR (needed for 7.1.1).

#### 8.1.3 Report section: Timeline & System

Chapter on smoothing method, timeline evaluation, system architecture, API and PDF reporting.

**Files:** `docs/report/03_system.md`  
**Deliverables:** docs/report/03_system.md  
**Inputs:** docs/timeline/TIMELINE_EVAL.md; contracts/

Completion checklist:
- [ ] Raw vs smoothed table present; architecture diagram present.
- [ ] Reviewed by D.
- [ ] PR merged into `develop`; issue closed

Hand-off: tag Member D in the PR (needed for 8.1.4).

#### 8.2.2 Demo video

3–4 minute recorded walkthrough of the 5 use cases on the v1.0.0 build (backup if the live demo fails).

**Files:** `docs/demo/`  
**Deliverables:** docs/demo/README.md with link; Demo video file (Release)  
**Inputs:** v1.0.0 build; Demo data

Completion checklist:
- [ ] Shows all 5 use cases in ≤4 min.
- [ ] Plays on the presentation laptop offline.
- [ ] PR merged into `develop`; issue closed

---

## Member D: Frontend Lead & Integration Owner

Team lead and integration owner. Owns the repo scaffold, interface contracts and fixtures, the web review workspace and library, the one-command local run, smoke tests, merging to develop/main and final report assembly.

**Load:** 12 tasks · 31 h

### Start here

```bash
git clone <repo-url> && cd or-intelligence
git switch develop
git switch -c feature/member-d-1.2.1-scaffold
```

### Your files (edit only these)

- `.github/`
- `.gitignore`
- `CHANGELOG.md`
- `README.md`
- `contracts/`
- `docker-compose.yml`
- `docker/`
- `docs/integration/`
- `docs/problem/`
- `docs/report/00_intro.md`
- `docs/report/04_frontend_conclusion.md`
- `docs/report/build.sh`
- `docs/report/main.md`
- `pyproject.toml`
- `requirements/base.txt`
- `scripts/`
- `tests/contracts/`
- `tests/e2e/`
- `tests/fixtures/`
- `web/package.json`
- `web/src/api/`
- `web/src/app/`
- `web/src/components/NotesPanel/`
- `web/src/components/Timeline/`
- `web/src/components/VideoPlayer/`
- `web/src/i18n/en.json`
- `web/src/i18n/index.ts`
- `web/src/pages/Library/`
- `web/src/pages/Review/`
- `web/src/pages/Upload/`
- `web/vite.config.ts`

### Do not modify

- src/ (all Python modules belong to A, B, C)
- web/src/pages/Analytics/, web/src/i18n/ar.json, web/src/styles/rtl.css (Member A)
- Other members' report sections in docs/report/

### You receive

- **4.2.2** Notes, search & analytics endpoints from Member C (Tue 24 Nov Evening)
- **4.3.1** PDF report generator (English & Arabic) from Member C (Tue 24 Nov Evening → Wed 25 Nov Morning)
- **3.3.2** Model card & weights release from Member B (Wed 25 Nov Morning)
- **5.2.2** Analytics dashboard page from Member A (Tue 24 Nov Evening → Wed 25 Nov Morning)
- **5.2.3** Arabic localisation & RTL styling from Member A (Wed 25 Nov Morning)
- **4.1.3** Timeline evaluation vs ground truth from Member C (Wed 25 Nov Morning → Wed 25 Nov Afternoon)
- **3.2.1** Held-out test evaluation report from Member B (Wed 25 Nov Morning)
- **8.1.1** Report section: Data from Member A (Wed 25 Nov Evening)
- **8.1.2** Report section: Model from Member B (Wed 25 Nov Afternoon)
- **8.1.3** Report section: Timeline & System from Member C (Wed 25 Nov Afternoon)
- **6.1.1** Inference performance benchmark from Member B (Wed 25 Nov Afternoon)

### Your tasks

| WBS | Task | When | h | Priority | Branch | Depends on |
|---|---|---|---|---|---|---|
| 1.1.1 | Problem statement, use cases & business model page | Mon 23 Nov Evening | 6 | High | `feature/member-d-1.1.1-problem-page` | — |
| 1.2.1 | Repository scaffold, branch protection & CI skeleton | Mon 23 Nov Evening | 1 | High | `feature/member-d-1.2.1-scaffold` | — |
| 1.2.2 ⚠ | Interface contracts & shared test fixtures | Mon 23 Nov Evening | 2 | High | `feature/member-d-1.2.2-contracts` | 1.2.1 |
| 5.1.1 | Web app shell, API client & upload flow | Tue 24 Nov Morning | 3 | High | `feature/member-d-5.1.1-shell` | 1.2.2 |
| 5.1.2 ⚠ | Video player + interactive instrument timeline | Tue 24 Nov Morning → Tue 24 Nov Evening | 5 | High | `feature/member-d-5.1.2-timeline-ui` | 5.1.1 |
| 5.1.3 | Timestamped notes panel & report download | Tue 24 Nov Evening | 2 | Medium | `feature/member-d-5.1.3-notes-ui` | 5.1.2 |
| 5.2.1 | Library search page | Wed 25 Nov Morning | 2 | Medium | `feature/member-d-5.2.1-library` | 5.1.1 |
| 6.3.1 | End-to-end smoke tests (5 use cases) | Wed 25 Nov Afternoon | 2 | High | `feature/member-d-6.3.1-e2e` | 7.1.1 |
| 7.1.1 ⚠ | One-command local run & integration | Wed 25 Nov Morning → Wed 25 Nov Afternoon | 3 | High | `feature/member-d-7.1.1-compose` | 4.2.2, 4.3.1, 3.3.2, 5.1.3, 5.2.1, 5.2.2, 5.2.3 |
| 7.1.2 | Deployment files: Dockerfiles & docker-compose | Wed 25 Nov Afternoon | 1 | High | `feature/member-d-7.1.2-docker` | 7.1.1 |
| 7.2.1 ⚠ | Release candidate v1.0.0 & demo freeze | Wed 25 Nov Evening | 1 | High | `feature/member-d-7.2.1-release` | 6.3.1, 4.1.3, 3.2.1, 7.1.2 |
| 8.1.4 | Final report assembly & README | Wed 25 Nov Evening | 3 | High | `feature/member-d-8.1.4-report` | 8.1.1, 8.1.2, 8.1.3, 6.1.1 |

#### 1.1.1 Problem statement, use cases & business model page (plan status: Completed)

Bilingual (EN/AR) page defining the problem, objective, success measures, proposed solution, top-5 use cases and business model. This already exists as or_intelligence_problem_usecases.html.

**Files:** `docs/problem/`  
**Deliverables:** docs/problem/or_intelligence_problem_usecases.html  
**Inputs:** Course brief; Domain research on laparoscopic training

Completion checklist:
- [ ] Page states problem, objective, success measures, 5 use cases and business model in EN and AR.
- [ ] Page committed under docs/problem/.
- [ ] PR merged into `develop`; issue closed

#### 1.2.1 Repository scaffold, branch protection & CI skeleton

Create the GitHub repository with the agreed folder tree, empty package stubs for every owner, CODEOWNERS that encodes file ownership, protected main/develop branches and a CI workflow that runs lint + tests.

**Files:** `.github/`, `.gitignore`, `pyproject.toml`, `requirements/base.txt`  
**Deliverables:** GitHub repo with develop + main; .github/CODEOWNERS; .github/workflows/ci.yml; PR template  
**Inputs:** PROJECT_STRUCTURE.md

Completion checklist:
- [ ] A test PR from each member triggers CI and requests the correct CODEOWNER review.
- [ ] Direct push to main/develop is rejected.
- [ ] CI passes on the empty scaffold.
- [ ] PR merged into `develop`; issue closed

Hand-off: tag Member A in the PR (needed for 2.1.1).

#### 1.2.2 Interface contracts & shared test fixtures

Freeze the data contracts (class map, detections, timeline, HTTP API) and ship small fixture files so every member can build and test their module in parallel without waiting for upstream work.

**Files:** `contracts/`, `tests/fixtures/`, `tests/contracts/`  
**Deliverables:** contracts/classes.json; contracts/detections.schema.json; contracts/timeline.schema.json; contracts/openapi.yaml; tests/fixtures/*; contracts/CHANGELOG.md  
**Inputs:** Project page (instrument list); PROJECT_STRUCTURE.md

Completion checklist:
- [ ] Fixtures validate against schemas in CI.
- [ ] A, B and C have signed off in contracts/CHANGELOG.md.
- [ ] openapi.yaml lints with no errors (e.g. `npx @redocly/cli lint`).
- [ ] PR merged into `develop`; issue closed

Hand-off: tag Member A, Member B, Member C in the PR (needed for 2.2.1, 3.3.1, 4.1.1, 4.2.1).

#### 5.1.1 Web app shell, API client & upload flow

React + Vite + TypeScript shell: routing, layout, typed API client generated from openapi.yaml, i18n loader, upload page with processing status polling.

**Files:** `web/package.json`, `web/vite.config.ts`, `web/src/app/`, `web/src/api/`, `web/src/pages/Upload/`, `web/src/i18n/index.ts`, `web/src/i18n/en.json`  
**Deliverables:** web/ app shell; web/src/api/; web/src/pages/Upload/; web/src/i18n/index.ts; web/src/i18n/en.json  
**Inputs:** contracts/openapi.yaml; tests/fixtures/

Completion checklist:
- [ ] `npm run build` passes in CI.
- [ ] Upload in mock mode reaches Review page.
- [ ] Adding a new folder under web/src/pages/ or a new locale JSON requires no edit to D's files (verified with a throwaway test page).
- [ ] PR merged into `develop`; issue closed

Hand-off: tag Member A in the PR (needed for 5.2.2, 5.2.3).

#### 5.1.2 Video player + interactive instrument timeline

The core review screen: HTML5 video player synced with a colour-coded, zoomable timeline; clicking a bar seeks the video; playhead follows playback.

**Files:** `web/src/components/Timeline/`, `web/src/components/VideoPlayer/`, `web/src/pages/Review/`  
**Deliverables:** web/src/components/Timeline/; web/src/components/VideoPlayer/; web/src/pages/Review/  
**Inputs:** tests/fixtures/sample_timeline.json; web/src/api/

Completion checklist:
- [ ] Clicking any bar seeks within ±0.5 s of segment start.
- [ ] Renders a 90-min timeline at 60 fps scroll without lag (Chrome performance check).
- [ ] Component tests pass.
- [ ] PR merged into `develop`; issue closed

#### 5.1.3 Timestamped notes panel & report download

Instructor notes at the current playhead time, listed and clickable; download PDF report in EN/AR.

**Files:** `web/src/components/NotesPanel/`  
**Deliverables:** web/src/components/NotesPanel/  
**Inputs:** web/src/pages/Review/; contracts/openapi.yaml

Completion checklist:
- [ ] Note added at 12:34 appears at 12:34 on the timeline and in the list.
- [ ] Clicking a note seeks the video.
- [ ] PDF downloads in both languages against the real API.
- [ ] PR merged into `develop`; issue closed

#### 5.2.1 Library search page

Use case 3: list all processed videos and search segments by instrument and minimum duration; each result opens Review at that timestamp.

**Files:** `web/src/pages/Library/`  
**Deliverables:** web/src/pages/Library/  
**Inputs:** /api/videos; /api/search

Completion checklist:
- [ ] 'clipper' search on fixtures lists exactly the clipper segments.
- [ ] Clicking a result opens Review at the right time.
- [ ] PR merged into `develop`; issue closed

#### 6.3.1 End-to-end smoke tests (5 use cases)

Scripted smoke checklist covering the 5 use cases on the integrated stack, plus one automated Playwright test for the core flow.

**Files:** `tests/e2e/`  
**Deliverables:** tests/e2e/SMOKE_CHECKLIST.md (ticked); tests/e2e/core.spec.ts  
**Inputs:** Integrated local stack (7.1.1)

Completion checklist:
- [ ] All 5 checklist scenarios pass on the release candidate.
- [ ] Core Playwright test passes.
- [ ] Every failure routed to exactly one owner.
- [ ] PR merged into `develop`; issue closed

#### 7.1.1 One-command local run & integration

Integrate API (with real model), web app and storage into a single local start command. Integration owner merges feature branches into develop (merge windows Mon/Tue 21:00, Wed 12:00) and resolves conflicts. Docker is optional and only if time remains.

**Files:** `scripts/`, `docs/integration/`  
**Deliverables:** scripts/run_local.ps1; scripts/run_local.sh; docs/integration/INTEGRATION_LOG.md  
**Inputs:** src/api (4.2.x, 4.3.1); src/inference (3.3.1); web (5.x); models/weights/best.pt (3.3.2)

Completion checklist:
- [ ] The run script on a clean clone serves the app on http://localhost:8080.
- [ ] A real video processes end-to-end; timeline and PDF work.
- [ ] develop CI green by Wed 18:00.
- [ ] PR merged into `develop`; issue closed

Hand-off: tag Member A in the PR (needed for 6.2.1).

#### 7.1.2 Deployment files: Dockerfiles & docker-compose

Added during repository setup: the course brief (docs/planning/Unit7_Project_brief.pdf) lists "Deployment Files" as a mandatory deliverable, while the WBS only had Docker as an optional stretch inside 7.1.1. Finish the starter Dockerfiles so the integrated app (API + web) also starts with `docker compose up`.

**Files:** `docker/`, `docker-compose.yml`  
**Deliverables:** docker/Dockerfile.api; docker/Dockerfile.web; docker-compose.yml  
**Inputs:** scripts/run_local.* (7.1.1); requirements/*.txt; web/

Completion checklist:
- [ ] `docker compose up --build` on a clean clone serves the app on http://localhost:8080.
- [ ] A video uploaded in the container stack reaches status done.
- [ ] No secrets or weights baked into the images.
- [ ] PR merged into `develop`; issue closed

#### 7.2.1 Release candidate v1.0.0 & demo freeze

Freeze features, merge develop → main, tag v1.0.0, prepare the demo machine.

**Files:** `CHANGELOG.md`  
**Deliverables:** Tag v1.0.0; CHANGELOG.md; Demo data  
**Inputs:** 6.3.1 results; 4.1.3; 3.2.1

Completion checklist:
- [ ] v1.0.0 tag on main; CI green.
- [ ] Demo runs offline from the tagged build.
- [ ] PR merged into `develop`; issue closed

Hand-off: tag Member C in the PR (needed for 8.2.2).

#### 8.1.4 Final report assembly & README

Assemble introduction, use cases, sections 01–03, frontend chapter, conclusion and limitations into the final report; write the repository README.

**Files:** `docs/report/main.md`, `docs/report/00_intro.md`, `docs/report/04_frontend_conclusion.md`, `docs/report/build.sh`, `README.md`  
**Deliverables:** docs/report/main.md; docs/report/00_intro.md; docs/report/04_frontend_conclusion.md; docs/report/build.sh; Final report PDF; README.md  
**Inputs:** docs/report/01–03; docs/usability/RESULTS.md; docs/model/BENCHMARK.md

Completion checklist:
- [ ] Report PDF builds from source.
- [ ] All 3 success measures reported with numbers.
- [ ] README quick start works on a clean clone.
- [ ] PR merged into `develop`; issue closed
