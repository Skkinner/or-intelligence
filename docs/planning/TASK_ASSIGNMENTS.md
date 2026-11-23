# Task Assignments

> **OR Intelligence** · Computer Vision Final Project · Deadline **Wednesday 25 Nov 2026, 23:59**  
> Generated from the same data as `project_wbs_dashboard.html`. Member names are placeholders (A–D); rename them in the dashboard.

## Quick reference

| Member | Role | Tasks | Hours | Branch prefix |
|---|---|---|---|---|
| Member A | Data Engineer & UX Research | 10 | 23 | `a/` |
| Member B | ML Engineer | 8 | 24 | `b/` |
| Member C | Backend & Timeline Engineer | 8 | 25 | `c/` |
| Member D | Frontend Lead & Integration Owner | 11 | 30 | `d/` |

Work blocks: **1** Mon 23 Nov Evening (18:00–23:00) · **2** Tue 24 Nov Morning (09:00–13:00) · **3** Tue 24 Nov Afternoon (14:00–18:00) · **4** Tue 24 Nov Evening (19:00–23:00) · **5** Wed 25 Nov Morning (09:00–13:00) · **6** Wed 25 Nov Afternoon (14:00–18:00) · **7** Wed 25 Nov Evening (19:00–23:59)

---

## Member A: Data Engineer & UX Research

Owns all data: acquisition, licences, YOLO-format conversion, the video-level split and the timeline ground truth. Later owns the analytics page, Arabic localisation and the usability study.

**Load:** 10 tasks · 23 h · branch prefix `a/`

### Files and folders you own

- `configs/data.yaml`
- `data/splits/splits.json`
- `docs/data/`
- `docs/data/EDA.md`
- `docs/data/figures/`
- `docs/data/qa_notes.md`
- `docs/data/timeline_eval_set.md`
- `docs/report/01_data.md`
- `docs/usability/`
- `notebooks/eda.ipynb`
- `requirements/data.txt`
- `src/data/convert_voc_to_yolo.py`
- `src/data/download.py`
- `src/data/eda.py`
- `src/data/extract_frames.py`
- `src/data/presence_labels.py`
- `src/data/split.py`
- `src/data/verify.py`
- `src/data/visualize.py`
- `tests/unit/data/`
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

### You receive from teammates

- **1.2.1** Repository scaffold, branch protection & CI skeleton from Member D (Mon 23 Nov Evening)
- **1.2.2** Interface contracts & shared test fixtures from Member D (Mon 23 Nov Evening)
- **5.1.1** Web app shell, API client & upload flow from Member D (Tue 24 Nov Morning)
- **7.1.1** One-command local run & integration from Member D (Wed 25 Nov Morning → Wed 25 Nov Afternoon)

### You hand off

- **2.2.2** → Member B for 3.1.1 (Baseline YOLO training): data/splits/splits.json, data/processed/dataset.yaml
- **2.3.1** → Member C for 4.1.3 (Timeline evaluation vs ground truth): data/processed/presence/<video_id>.csv, docs/data/timeline_eval_set.md
- **2.4.1** → Member B for 3.1.2 (Augmentation & hyper-parameter experiments): docs/data/EDA.md, docs/data/figures/*.png
- **2.4.1** → Member B for 8.2.1 (Presentation slide deck): docs/data/EDA.md, docs/data/figures/*.png
- **5.2.2** → Member D for 7.1.1 (One-command local run & integration): web/src/pages/Analytics/
- **5.2.3** → Member D for 7.1.1 (One-command local run & integration): web/src/i18n/ar.json, web/src/styles/rtl.css
- **8.1.1** → Member D for 8.1.4 (Final report assembly & README): docs/report/01_data.md

### Tasks

#### 1.3.1 Dataset licensing & ethics checklist

| When | Effort | Priority | Status | Branch |
|---|---|---|---|---|
| Mon 23 Nov Evening | 1 h | High | Not Started | `a/1.3.1-licensing` |

Confirm which datasets may be used, under what licence, how to cite them, and record the educational/non-diagnostic scope. Blocks any data download.

**Steps**

1. Read the licence and access terms of m2cai16-tool-locations, m2cai16-tool and Cholec80 (CAMMA research licences, non-commercial).
2. Decide tonight (Mon) on the timeline ground truth: Cholec80 only if a team member already has access; otherwise m2cai16-tool presence labels on held-out videos. Record the decision in the doc and tell C.
3. List allowed uses (academic project, no redistribution of raw videos in the repo, no commercial use).
4. Write the BibTeX citations required by each dataset.
5. Write docs/data/LICENSES_AND_ETHICS.md: licences, citations, storage rule (data/ is gitignored), 'educational tool, not diagnostic' statement, PDPL note for any future real-patient data.

**Inputs**

- Dataset web pages / licence texts

**Outputs (deliverables)**

- docs/data/LICENSES_AND_ETHICS.md

**Owned files**: `docs/data/`

**Depends on**: none, start immediately

**Acceptance criteria**

- [ ] Document lists licence, citation and allowed use for every dataset used.
- [ ] Reviewed and approved by D in PR.
- [ ] Explicit rule: no raw video or frames committed to Git.

#### 2.1.1 Download & verify datasets

| When | Effort | Priority | Status | Branch |
|---|---|---|---|---|
| Mon 23 Nov Evening | 2 h | High | Not Started | `a/2.1.1-download` |

Scripted, reproducible download of m2cai16-tool-locations (frames + VOC XML boxes) and the Cholec80 videos/tool annotations needed for timeline evaluation, with checksums.

**Steps**

1. Write src/data/download.py: CLI `python -m src.data.download --dataset m2cai16|cholec80 --out data/raw/` (Cholec80 path may be a manual copy if the licence requires manual download; script then only verifies).
2. Record SHA-256 of every archive in configs/data.yaml under `checksums:`.
3. Write src/data/verify.py: counts images, XML files, videos and tool-annotation files; fails loudly on mismatch.
4. Store raw data in data/raw/m2cai16_tool_locations/ and data/raw/cholec80/ (gitignored).
5. Put a 20-frame sample + 1 XML in tests/unit/data/sample/ for unit tests (only if the licence allows; otherwise synthetic boxes).
6. Upload a team copy to the shared drive so B and C don't re-download.

**Inputs**

- docs/data/LICENSES_AND_ETHICS.md (approved)

**Outputs (deliverables)**

- src/data/download.py
- src/data/verify.py
- configs/data.yaml
- data/raw/ populated (not in Git)

**Owned files**: `src/data/download.py`, `src/data/verify.py`, `configs/data.yaml`, `requirements/data.txt`

**Depends on**: 1.3.1 (Member A), 1.2.1 (Member D)

**Acceptance criteria**

- [ ] `python -m src.data.verify` passes on a clean machine after download.
- [ ] Counts printed match the dataset documentation.
- [ ] Nothing under data/ is tracked by Git.

#### 2.2.1 VOC → YOLO conversion & class mapping

| When | Effort | Priority | Status | Branch |
|---|---|---|---|---|
| Mon 23 Nov Evening → Tue 24 Nov Morning | 3 h | High | Not Started | `a/2.2.1-voc-to-yolo` |

Convert m2cai16-tool-locations Pascal-VOC boxes into YOLO txt labels using contracts/classes.json, dropping SpecimenBag, with validation and visual spot-checks.

**Steps**

1. Write src/data/convert_voc_to_yolo.py: parse XML, map names case-insensitively (Grasper→0 … Irrigator→5), skip SpecimenBag, clip boxes to image bounds, write `cls cx cy w h` normalised.
2. Log and count: dropped boxes, empty images, malformed XML. Keep images with zero tools as background images (empty .txt).
3. Write src/data/visualize.py: draws labels on N random images to data/processed/qa/.
4. Manually inspect ≥50 rendered images; note issues in docs/data/qa_notes.md.
5. Unit tests tests/unit/data/test_convert.py: known XML → expected txt; out-of-bounds box clipped; SpecimenBag dropped.

**Inputs**

- data/raw/m2cai16_tool_locations/
- contracts/classes.json

**Outputs (deliverables)**

- data/processed/yolo/images|labels (all)
- src/data/convert_voc_to_yolo.py
- src/data/visualize.py
- docs/data/qa_notes.md

**Owned files**: `src/data/convert_voc_to_yolo.py`, `src/data/visualize.py`, `tests/unit/data/`, `docs/data/qa_notes.md`

**Depends on**: 2.1.1 (Member A), 1.2.2 (Member D)

**Acceptance criteria**

- [ ] Every image has exactly one .txt label file (possibly empty).
- [ ] All class ids ∈ {0..5}; all coordinates ∈ [0,1].
- [ ] ≥50 visual spot-checks recorded with <2% label errors.
- [ ] Unit tests pass in CI.

#### 2.2.2 Video-level train/val/test split ⚠ critical integration point

| When | Effort | Priority | Status | Branch |
|---|---|---|---|---|
| Tue 24 Nov Morning | 1 h | High | Not Started | `a/2.2.2-split` |

Split by source video (never by frame) so the test set measures generalisation to unseen surgeries, as required by the success measures.

**Steps**

1. Parse the video ID from each frame filename; build a video → frame count table.
2. Write src/data/split.py: deterministic (seed 42) split ≈70/15/15 by video, stratified so each split contains all 6 classes.
3. Write data/splits/splits.json and place images/labels into train/val/test folders.
4. Generate data/processed/dataset.yaml (Ultralytics format; names from contracts/classes.json).
5. Add a leakage test: assert no video ID appears in more than one split.
6. Hand off: post split counts (videos, images, boxes per class per split) in the PR and tag B.

**Inputs**

- data/processed/yolo/ (unsplit)

**Outputs (deliverables)**

- data/splits/splits.json
- data/processed/dataset.yaml
- Split summary table in PR

**Owned files**: `src/data/split.py`, `data/splits/splits.json`

**Depends on**: 2.2.1 (Member A)

**Acceptance criteria**

- [ ] No video ID shared across splits (test passes).
- [ ] Each split contains every class at least 20 times.
- [ ] `yolo detect val data=data/processed/dataset.yaml` loads the dataset without errors.

**Hand-off**: when merged, tag Member B in the PR (needed for 3.1.1).

#### 2.3.1 Timeline ground truth from Cholec80 presence labels

| When | Effort | Priority | Status | Branch |
|---|---|---|---|---|
| Tue 24 Nov Morning → Tue 24 Nov Afternoon | 3 h | High | Not Started | `a/2.3.1-presence-gt` |

Prepare a held-out set of full surgery videos with per-second tool-presence labels, used to measure timeline agreement (success measure 2). Videos must not overlap with the detector's training videos. Source is Cholec80 or the m2cai16-tool fallback (decided in 1.3.1).

**Steps**

1. Select 3 held-out videos for timeline evaluation (1 for tuning, 2 for reporting); document the choice in docs/data/timeline_eval_set.md.
2. Check and document that none of these videos are the source of any m2cai16 training frame (compare video identifiers/metadata; if uncertain, record as a risk).
3. Write src/data/presence_labels.py: convert the chosen tool-presence annotation files to contract C3 CSV (1 fps, map names to the 6 classes, drop SpecimenBag).
4. Write src/data/extract_frames.py (ffmpeg via subprocess): optional 1 fps frame dump for debugging.
5. Validate: CSV row count ≈ video duration in seconds (±2 s).
6. Hand off the CSVs and the video list to C (task 4.1.3).

**Inputs**

- data/raw/cholec80/

**Outputs (deliverables)**

- data/processed/presence/<video_id>.csv
- docs/data/timeline_eval_set.md
- src/data/presence_labels.py
- src/data/extract_frames.py

**Owned files**: `src/data/presence_labels.py`, `src/data/extract_frames.py`, `docs/data/timeline_eval_set.md`

**Depends on**: 2.1.1 (Member A)

**Acceptance criteria**

- [ ] Each CSV matches contract C3 (header + 0/1 values).
- [ ] Row counts within ±2 s of video length.
- [ ] Overlap check with training videos documented.

**Hand-off**: when merged, tag Member C in the PR (needed for 4.1.3).

#### 2.4.1 EDA & class-balance report

| When | Effort | Priority | Status | Branch |
|---|---|---|---|---|
| Tue 24 Nov Afternoon | 2 h | Medium | Not Started | `a/2.4.1-eda` |

Quantify the dataset so B can plan augmentation and class weighting, and so the report has a data section.

**Steps**

1. Write src/data/eda.py producing CSV + PNG charts in docs/data/figures/: boxes per class per split, images per video, box size distribution, co-occurrence matrix.
2. Summarise findings in notebooks/eda.ipynb (read-only visual companion).
3. Write docs/data/EDA.md: key numbers, imbalance ratio, small-object share, recommendations to B (e.g. oversample scissors/clipper).

**Inputs**

- data/processed/yolo/
- data/splits/splits.json

**Outputs (deliverables)**

- docs/data/EDA.md
- docs/data/figures/*.png
- src/data/eda.py
- notebooks/eda.ipynb

**Owned files**: `src/data/eda.py`, `docs/data/EDA.md`, `docs/data/figures/`, `notebooks/eda.ipynb`

**Depends on**: 2.2.2 (Member A)

**Acceptance criteria**

- [ ] EDA.md contains per-class counts per split and at least 4 figures.
- [ ] Recommendations section addressed to B is present.
- [ ] Charts regenerate from `python -m src.data.eda`.

**Hand-off**: when merged, tag Member B in the PR (needed for 3.1.2, 8.2.1).

#### 5.2.2 Analytics dashboard page

| When | Effort | Priority | Status | Branch |
|---|---|---|---|---|
| Tue 24 Nov Evening → Wed 25 Nov Morning | 4 h | Medium | Not Started | `a/5.2.2-analytics` |

Use case 5: compare per-case statistics (time per instrument, total time, switches) across selected videos.

**Steps**

1. Implement web/src/pages/Analytics/ (stub created by D in 5.1.1): multi-select videos, call /api/analytics (mock mode until 4.2.2 lands).
2. Charts: stacked bar of per-tool seconds per case; line of switches across cases ordered by date; table of stats.
3. If a chart library is needed, request it in a PR to web/package.json (owned by D) — do not edit package.json directly.
4. Export the stats table as CSV.
5. Vitest tests for the data transformation functions.

**Inputs**

- contracts/openapi.yaml (analytics)
- tests/fixtures/sample_timeline.json

**Outputs (deliverables)**

- web/src/pages/Analytics/

**Owned files**: `web/src/pages/Analytics/`

**Depends on**: 5.1.1 (Member D)

**Acceptance criteria**

- [ ] Selecting 3 fixture cases shows correct per-tool totals (match API JSON).
- [ ] CSV export opens in Excel with correct columns.
- [ ] No files outside web/src/pages/Analytics/ changed in the PR.

**Hand-off**: when merged, tag Member D in the PR (needed for 7.1.1).

#### 5.2.3 Arabic localisation & RTL styling

| When | Effort | Priority | Status | Branch |
|---|---|---|---|---|
| Wed 25 Nov Morning | 2 h | Medium | Not Started | `a/5.2.3-arabic` |

Complete Arabic translation of all UI strings and RTL layout fixes, matching the bilingual product promise.

**Steps**

1. Translate every key in web/src/i18n/en.json into web/src/i18n/ar.json (keep keys identical; CI test checks key parity).
2. Write web/src/styles/rtl.css: mirror layout, keep the timeline time axis left-to-right (time always increases to the right) and document this decision.
3. Review all pages in AR; log issues for D's components as GitHub issues rather than editing them.
4. Visually verify Arabic PDF output from C's generator.

**Inputs**

- web/src/i18n/en.json (D)

**Outputs (deliverables)**

- web/src/i18n/ar.json
- web/src/styles/rtl.css
- web/src/i18n/parity.test.ts

**Owned files**: `web/src/i18n/ar.json`, `web/src/styles/rtl.css`, `web/src/i18n/parity.test.ts`

**Depends on**: 5.1.1 (Member D)

**Acceptance criteria**

- [ ] Key parity test passes (en ↔ ar).
- [ ] All pages usable in Arabic with no clipped or mirrored-wrong elements (screenshots in PR).
- [ ] Arabic PDF reviewed and approved.

**Hand-off**: when merged, tag Member D in the PR (needed for 7.1.1).

#### 6.2.1 Usability study: scrubbing vs timeline

| When | Effort | Priority | Status | Branch |
|---|---|---|---|---|
| Wed 25 Nov Afternoon → Wed 25 Nov Evening | 3 h | High | Not Started | `a/6.2.1-usability` |

Success measure 3. Within-subject test: participants find specific moments (e.g. first clipper use) by manual scrubbing vs with the OR Intelligence timeline.

**Steps**

1. Write protocol docs/usability/PROTOCOL.md on Tue evening (before the app is ready): ≥3 participants (classmates are fine), 3 find-tasks per condition, counterbalanced order, verbal consent, no personal data stored.
2. Prepare two comparable videos and the task sheet.
3. Run 10-minute sessions on Wed afternoon on the integrated build; record time-to-find and success per task in docs/usability/results.csv (anonymous IDs).
4. Analyse: median time per condition and the ratio; state clearly that n is small (pilot study).
5. Write docs/usability/RESULTS.md with chart.

**Inputs**

- Running release candidate (7.1.1)

**Outputs (deliverables)**

- docs/usability/PROTOCOL.md
- docs/usability/results.csv
- docs/usability/RESULTS.md

**Owned files**: `docs/usability/`

**Depends on**: 7.1.1 (Member D)

**Acceptance criteria**

- [ ] ≥3 participants completed both conditions.
- [ ] Median time-to-find reported for both conditions, labelled as a pilot.
- [ ] Data anonymous.

#### 8.1.1 Report section: Data

| When | Effort | Priority | Status | Branch |
|---|---|---|---|---|
| Wed 25 Nov Evening | 2 h | Medium | Not Started | `a/8.1.1-report-data` |

Final report chapter on datasets, licences, preprocessing, split, EDA and timeline ground truth.

**Steps**

1. Write docs/report/01_data.md (≤4 pages) reusing EDA.md, LICENSES_AND_ETHICS.md, timeline_eval_set.md.
2. Include split table and 2–3 figures.
3. Add usability results summary (from 6.2.1) as a subsection 01b in the same file.

**Inputs**

- docs/data/*
- docs/usability/RESULTS.md

**Outputs (deliverables)**

- docs/report/01_data.md

**Owned files**: `docs/report/01_data.md`

**Depends on**: 2.4.1 (Member A), 6.2.1 (Member A)

**Acceptance criteria**

- [ ] Section complete, figures referenced, citations present.
- [ ] Reviewed by D.

**Hand-off**: when merged, tag Member D in the PR (needed for 8.1.4).

---

## Member B: ML Engineer

Owns the detector: training, tuning, evaluation, the video inference module that produces detections.jsonl, the model card, the performance benchmark and the slide deck.

**Load:** 8 tasks · 24 h · branch prefix `b/`

### Files and folders you own

- `configs/experiments/`
- `configs/train.yaml`
- `docs/model/BENCHMARK.md`
- `docs/model/EVALUATION.md`
- `docs/model/MODEL_CARD.md`
- `docs/model/experiments.md`
- `docs/model/figures/`
- `docs/model/test_metrics.json`
- `docs/report/02_model.md`
- `docs/slides/`
- `models/weights/`
- `notebooks/experiments/`
- `requirements/ml.txt`
- `src/inference/`
- `src/models/benchmark.py`
- `src/models/evaluate.py`
- `src/models/train.py`
- `src/models/tune.py`
- `tests/unit/inference/`
- `tests/unit/models/`

### Do not modify

- src/data/ and data/ (read-only consumer)
- src/timeline/
- src/api/
- src/reports/
- web/
- contracts/ (propose changes by PR)

### You receive from teammates

- **1.2.2** Interface contracts & shared test fixtures from Member D (Mon 23 Nov Evening)
- **2.2.2** Video-level train/val/test split from Member A (Tue 24 Nov Morning)
- **2.4.1** EDA & class-balance report from Member A (Tue 24 Nov Afternoon)
- **4.1.3** Timeline evaluation vs ground truth from Member C (Wed 25 Nov Morning → Wed 25 Nov Afternoon)

### You hand off

- **3.3.1** → Member C for 4.1.3 (Timeline evaluation vs ground truth): src/inference/detect_video.py, src/inference/README.md
- **3.2.1** → Member D for 7.2.1 (Release candidate v1.0.0 & demo freeze): docs/model/EVALUATION.md, docs/model/test_metrics.json
- **3.3.2** → Member D for 7.1.1 (One-command local run & integration): docs/model/MODEL_CARD.md, GitHub Release model-v1
- **6.1.1** → Member D for 8.1.4 (Final report assembly & README): docs/model/BENCHMARK.md, src/models/benchmark.py
- **8.1.2** → Member D for 8.1.4 (Final report assembly & README): docs/report/02_model.md

### Tasks

#### 3.3.1 Video inference module (detections.jsonl) ⚠ critical integration point

| When | Effort | Priority | Status | Branch |
|---|---|---|---|---|
| Mon 23 Nov Evening → Tue 24 Nov Afternoon | 5 h | High | Not Started | `b/3.3.1-inference` |

Library + CLI that samples a video at N fps, runs the detector and streams detections in contract C4 format. This is what the API (C) calls.

**Steps**

1. Mon evening: set up the environment and implement src/inference/detect_video.py with the exact signature in contract C4 using COCO-pretrained yolov8n.pt as a stand-in (no dependency on training); read frames with OpenCV, sample at sample_fps, batch inference. Swap to baseline.pt/best.pt when available.
2. Add a progress callback parameter `on_progress(fraction: float)` so the API can report progress.
3. CLI: `python -m src.inference.detect_video in.mp4 out.jsonl --fps 5`.
4. Fall back to CPU if no GPU; allow ONNX weights.
5. Tests tests/unit/inference/: run on tests/fixtures/sample_video.mp4 with baseline weights; output validates against contracts/detections.schema.json.
6. Hand off: document usage in src/inference/README.md and notify C.

**Inputs**

- yolov8n.pt (stand-in), later baseline.pt / best.pt
- contracts/detections.schema.json
- tests/fixtures/sample_video.mp4

**Outputs (deliverables)**

- src/inference/detect_video.py
- src/inference/README.md
- tests/unit/inference/

**Owned files**: `src/inference/`, `tests/unit/inference/`

**Depends on**: 1.2.2 (Member D)

**Acceptance criteria**

- [ ] Output for the fixture video validates against the schema.
- [ ] Progress callback reaches 1.0.
- [ ] Processes a 2-min 1080p clip at 5 fps in < 2 min on the target GPU (documented).

**Hand-off**: when merged, tag Member C in the PR (needed for 4.1.3).

#### 3.1.1 Baseline YOLO training

| When | Effort | Priority | Status | Branch |
|---|---|---|---|---|
| Tue 24 Nov Morning → Tue 24 Nov Afternoon | 4 h | High | Not Started | `b/3.1.1-baseline` |

Fine-tune a COCO-pretrained YOLO (e.g. yolov8s / yolo11s) on the 6-class dataset to establish a baseline and produce first usable weights.

**Steps**

1. Write configs/train.yaml (yolov8s, imgsz 640, epochs 50, batch 16, patience 10, seed 42, data path). Start the Kaggle/Colab run as early as possible Tue morning; it runs while you work on 3.3.1.
2. Write src/models/train.py wrapping Ultralytics: `python -m src.models.train --config configs/train.yaml --name baseline`.
3. Train on Colab/Kaggle GPU; log runs to runs/ and record experiment in docs/model/experiments.md (config hash, mAP@0.5, mAP@0.5:0.95, time).
4. Save best weights to models/weights/baseline.pt (store in shared drive / GitHub Release, never in Git).
5. Smoke test tests/unit/models/test_train_config.py (config loads, class names match contracts/classes.json).

**Inputs**

- data/processed/dataset.yaml
- contracts/classes.json

**Outputs (deliverables)**

- models/weights/baseline.pt
- configs/train.yaml
- src/models/train.py
- docs/model/experiments.md

**Owned files**: `src/models/train.py`, `configs/train.yaml`, `requirements/ml.txt`, `docs/model/experiments.md`, `tests/unit/models/`

**Depends on**: 2.2.2 (Member A)

**Acceptance criteria**

- [ ] Baseline val mAP@0.5 recorded in experiments.md.
- [ ] Weights downloadable by the team.
- [ ] Training reproducible from the config with the same seed.

#### 3.1.2 Augmentation & hyper-parameter experiments

| When | Effort | Priority | Status | Branch |
|---|---|---|---|---|
| Tue 24 Nov Evening | 4 h | High | Not Started | `b/3.1.2-tuning` |

Improve on the baseline using EDA findings: model size, image size, augmentation (smoke/blur, HSV, mosaic), class imbalance handling. Select the final model on the validation split only.

**Steps**

1. Plan 2 experiments in docs/model/experiments.md (one change each, chosen from EDA): e.g. imgsz 832 and blur/HSV augmentation or oversampling the rarest class. Launch both in parallel GPU sessions Tue afternoon.
2. Write src/models/tune.py to launch a named experiment from a config override file in configs/experiments/.
3. Run experiments; record val mAP@0.5 and per-class AP for each.
4. Choose the best by val mAP@0.5 (tie-break: per-class min AP, then speed). Do NOT look at the test split.
5. Export final weights models/weights/best.pt and optionally ONNX models/weights/best.onnx.

**Inputs**

- models/weights/baseline.pt
- docs/data/EDA.md

**Outputs (deliverables)**

- models/weights/best.pt
- configs/experiments/*.yaml
- Experiment table in docs/model/experiments.md

**Owned files**: `src/models/tune.py`, `configs/experiments/`, `models/weights/`, `notebooks/experiments/`

**Depends on**: 3.1.1 (Member B), 2.4.1 (Member A)

**Acceptance criteria**

- [ ] 2 experiments logged with config and results (plus baseline).
- [ ] Final model's val mAP@0.5 ≥ baseline.
- [ ] best.pt shared by Tue 23:00; selection rationale written; test split untouched.

#### 3.2.1 Held-out test evaluation report

| When | Effort | Priority | Status | Branch |
|---|---|---|---|---|
| Wed 25 Nov Morning | 3 h | High | Not Started | `b/3.2.1-eval` |

One-time evaluation of the final model on the video-level test split: mAP@0.5, mAP@0.5:0.95, per-instrument precision/recall, confusion matrix, failure analysis.

**Steps**

1. Write src/models/evaluate.py: runs Ultralytics val on split=test, saves metrics JSON to docs/model/test_metrics.json.
2. Produce per-class P/R table at the chosen confidence threshold and PR curves.
3. Collect 20 failure cases (FN/FP) into docs/model/figures/failures/ with short comments (smoke, occlusion, motion blur, partial tools).
4. Write docs/model/EVALUATION.md.
5. Hand off the recommended confidence threshold to C (timeline params).

**Inputs**

- models/weights/best.pt
- test split

**Outputs (deliverables)**

- docs/model/EVALUATION.md
- docs/model/test_metrics.json
- docs/model/figures/

**Owned files**: `src/models/evaluate.py`, `docs/model/EVALUATION.md`, `docs/model/test_metrics.json`, `docs/model/figures/`

**Depends on**: 3.1.2 (Member B)

**Acceptance criteria**

- [ ] Report includes mAP@0.5 and P/R for all 6 instruments on the test split.
- [ ] Test split evaluated exactly once (stated in report).
- [ ] Recommended conf threshold communicated to C in the PR.

**Hand-off**: when merged, tag Member D in the PR (needed for 7.2.1).

#### 3.3.2 Model card & weights release

| When | Effort | Priority | Status | Branch |
|---|---|---|---|---|
| Wed 25 Nov Morning | 1 h | Medium | Not Started | `b/3.3.2-model-card` |

Publish final weights as a GitHub Release asset with a model card describing data, metrics, limits and intended (educational) use.

**Steps**

1. Write docs/model/MODEL_CARD.md: training data + licence, metrics table, known failure modes, intended use, out-of-scope (diagnosis, other procedures).
2. Create GitHub Release `model-v1` with best.pt (and best.onnx) and SHA-256.
3. Add src/inference/fetch_weights.py that downloads and verifies the release asset into models/weights/.

**Inputs**

- docs/model/EVALUATION.md
- models/weights/best.pt

**Outputs (deliverables)**

- docs/model/MODEL_CARD.md
- GitHub Release model-v1
- src/inference/fetch_weights.py

**Owned files**: `docs/model/MODEL_CARD.md`

**Depends on**: 3.2.1 (Member B)

**Acceptance criteria**

- [ ] `python -m src.inference.fetch_weights` downloads and verifies best.pt on a clean clone.
- [ ] Model card states non-diagnostic, educational scope.

**Hand-off**: when merged, tag Member D in the PR (needed for 7.1.1).

#### 6.1.1 Inference performance benchmark

| When | Effort | Priority | Status | Branch |
|---|---|---|---|---|
| Wed 25 Nov Afternoon | 1 h | Low | Not Started | `b/6.1.1-benchmark` |

Measure processing time and resource use for realistic video lengths to set user expectations and choose sample_fps.

**Steps**

1. Write src/models/benchmark.py: time detect_video on one 10-min clip at 1, 2 and 5 fps on the available GPU (and CPU at 1 fps).
2. Optional if time allows: macro-F1 impact of sample_fps using C's evaluate.py (call it, don't modify it).
3. Write docs/model/BENCHMARK.md and recommend default sample_fps.

**Inputs**

- models/weights/best.pt
- src/inference/
- src/timeline/evaluate.py

**Outputs (deliverables)**

- docs/model/BENCHMARK.md
- src/models/benchmark.py

**Owned files**: `src/models/benchmark.py`, `docs/model/BENCHMARK.md`

**Depends on**: 3.3.2 (Member B), 4.1.3 (Member C)

**Acceptance criteria**

- [ ] Table of processing seconds per video-minute for each fps setting.
- [ ] Recommended default sample_fps stated.

**Hand-off**: when merged, tag Member D in the PR (needed for 8.1.4).

#### 8.1.2 Report section: Model

| When | Effort | Priority | Status | Branch |
|---|---|---|---|---|
| Wed 25 Nov Afternoon | 2 h | Medium | Not Started | `b/8.1.2-report-model` |

Chapter on detector choice, training, experiments, test results, failure analysis and benchmark.

**Steps**

1. Write docs/report/02_model.md from experiments.md, EVALUATION.md, BENCHMARK.md.
2. Include metrics table and failure examples.

**Inputs**

- docs/model/*

**Outputs (deliverables)**

- docs/report/02_model.md

**Owned files**: `docs/report/02_model.md`

**Depends on**: 3.2.1 (Member B), 6.1.1 (Member B)

**Acceptance criteria**

- [ ] mAP@0.5 and per-class P/R table present.
- [ ] Reviewed by D.

**Hand-off**: when merged, tag Member D in the PR (needed for 8.1.4).

#### 8.2.1 Presentation slide deck

| When | Effort | Priority | Status | Branch |
|---|---|---|---|---|
| Wed 25 Nov Afternoon → Wed 25 Nov Evening | 4 h | High | Not Started | `b/8.2.1-slides` |

10–15 minute presentation: problem, approach, results (3 success measures), demo screenshots, business model, limits.

**Steps**

1. Wed afternoon: draft outline and get one-line approval from D.
2. Build slides in docs/slides/ using figures from EDA, EVALUATION and TIMELINE_EVAL (link, don't copy-edit others' files).
3. Wed evening: add the usability numbers from 6.2.1 and demo screenshots; rehearse once with the team.

**Inputs**

- docs/data/EDA.md
- docs/model/EVALUATION.md
- docs/timeline/TIMELINE_EVAL.md
- 1.1.1 page

**Outputs (deliverables)**

- docs/slides/OR_Intelligence.pptx (or PDF)

**Owned files**: `docs/slides/`

**Depends on**: 2.4.1 (Member A), 3.2.1 (Member B), 4.1.3 (Member C)

**Acceptance criteria**

- [ ] Deck covers problem, solution, 3 success-measure results, demo, business model, limits.
- [ ] Rehearsal within time limit.

---

## Member C: Backend & Timeline Engineer

Owns everything between detections and the browser: temporal smoothing, interval building and statistics, timeline evaluation, the FastAPI service, notes/search/analytics endpoints and the PDF report.

**Load:** 8 tasks · 25 h · branch prefix `c/`

### Files and folders you own

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

### You receive from teammates

- **1.2.2** Interface contracts & shared test fixtures from Member D (Mon 23 Nov Evening)
- **2.3.1** Timeline ground truth from Cholec80 presence labels from Member A (Tue 24 Nov Morning → Tue 24 Nov Afternoon)
- **3.3.1** Video inference module (detections.jsonl) from Member B (Mon 23 Nov Evening → Tue 24 Nov Afternoon)
- **7.2.1** Release candidate v1.0.0 & demo freeze from Member D (Wed 25 Nov Evening)

### You hand off

- **4.2.2** → Member D for 7.1.1 (One-command local run & integration): src/api/routes/notes.py, src/api/routes/search.py
- **4.3.1** → Member D for 7.1.1 (One-command local run & integration): src/reports/pdf_report.py, src/reports/strings.py
- **4.1.3** → Member B for 6.1.1 (Inference performance benchmark): src/timeline/evaluate.py, docs/timeline/TIMELINE_EVAL.md
- **4.1.3** → Member D for 7.2.1 (Release candidate v1.0.0 & demo freeze): src/timeline/evaluate.py, docs/timeline/TIMELINE_EVAL.md
- **4.1.3** → Member B for 8.2.1 (Presentation slide deck): src/timeline/evaluate.py, docs/timeline/TIMELINE_EVAL.md
- **8.1.3** → Member D for 8.1.4 (Final report assembly & README): docs/report/03_system.md

### Tasks

#### 4.1.1 Temporal smoothing

| When | Effort | Priority | Status | Branch |
|---|---|---|---|---|
| Mon 23 Nov Evening | 3 h | High | Not Started | `c/4.1.1-smoothing` |

Turn noisy per-frame detections into stable per-tool presence signals: confidence threshold, per-tool max-confidence per frame, sliding-window vote / hysteresis.

**Steps**

1. Implement src/timeline/smoothing.py: `presence_matrix(dets, conf) -> np.ndarray[T, 6]` then `smooth(matrix, fps, window_s, method='majority'|'hysteresis', on=0.6, off=0.4)`.
2. Expose parameters in configs/timeline.yaml (conf, window_s, method, on/off thresholds).
3. Develop and test only against tests/fixtures/sample_detections.jsonl (no dependency on the real model).
4. Unit tests: single-frame flicker removed; real 3-s gap kept; output shape and dtype correct.

**Inputs**

- tests/fixtures/sample_detections.jsonl
- contracts/detections.schema.json

**Outputs (deliverables)**

- src/timeline/smoothing.py
- configs/timeline.yaml
- tests/unit/timeline/test_smoothing.py

**Owned files**: `src/timeline/smoothing.py`, `configs/timeline.yaml`, `tests/unit/timeline/`, `requirements/api.txt`

**Depends on**: 1.2.2 (Member D)

**Acceptance criteria**

- [ ] Unit tests pass.
- [ ] On the fixture, number of segments drops by ≥50% versus raw thresholding with no segment >2 s lost.

#### 4.2.1 FastAPI service & background processing jobs ⚠ critical integration point

| When | Effort | Priority | Status | Branch |
|---|---|---|---|---|
| Mon 23 Nov Evening → Tue 24 Nov Afternoon | 5 h | High | Not Started | `c/4.2.1-api` |

HTTP service implementing upload, status, video streaming and timeline endpoints from contracts/openapi.yaml, with a background worker that runs inference → timeline.

**Steps**

1. Scaffold src/api/main.py (FastAPI, CORS for the Vite dev origin), src/api/db.py (SQLite via SQLModel: Video, Note tables).
2. Implement src/api/routes/videos.py: POST /api/videos (save to storage/videos/), GET list/status, GET /file with HTTP range support, GET /timeline.
3. Implement src/api/jobs.py: background worker (FastAPI BackgroundTasks or a single-thread queue) calling detect_video → build_timeline; update status/progress; store timeline JSON in storage/timelines/.
4. Until 3.3.1 lands, use a stub that replays tests/fixtures/sample_detections.jsonl (env INFERENCE_MODE=fixture).
5. Tests tests/unit/api/ with FastAPI TestClient: upload → done → timeline matches schema (fixture mode).
6. Run `uvicorn src.api.main:app` and verify /docs matches openapi.yaml.

**Inputs**

- contracts/openapi.yaml
- src/timeline/builder.py
- src/inference/detect_video.py (via import)

**Outputs (deliverables)**

- src/api/main.py
- src/api/db.py
- src/api/jobs.py
- src/api/routes/videos.py
- tests/unit/api/

**Owned files**: `src/api/main.py`, `src/api/db.py`, `src/api/jobs.py`, `src/api/routes/videos.py`, `tests/unit/api/`

**Depends on**: 1.2.2 (Member D)

**Acceptance criteria**

- [ ] All video endpoints in openapi.yaml implemented; responses validate.
- [ ] Fixture-mode upload reaches status done in tests.
- [ ] Real mode works with best.pt on the sample video.

#### 4.1.2 Interval builder & per-case statistics

| When | Effort | Priority | Status | Branch |
|---|---|---|---|---|
| Tue 24 Nov Morning | 3 h | High | Not Started | `c/4.1.2-builder` |

Convert smoothed presence into contract C5 timeline: intervals per tool (merge small gaps, drop tiny segments), per-tool time, segment counts, tool switches.

**Steps**

1. Implement src/timeline/builder.py: `build_timeline(dets_path, video_id, params) -> dict` (contract C5).
2. Merge gaps < merge_gap_s; drop segments < min_segment_s; compute mean_conf per segment.
3. Define 'tool switch' = change in the set of active tools after smoothing; document the definition in the module docstring.
4. Compute stats: total_s, per_tool_s, per_tool_segments, switches.
5. Validate output against contracts/timeline.schema.json in tests.
6. CLI: `python -m src.timeline.builder detections.jsonl timeline.json`.

**Inputs**

- src/timeline/smoothing.py
- contracts/timeline.schema.json

**Outputs (deliverables)**

- src/timeline/builder.py
- timeline.json (per video)

**Owned files**: `src/timeline/builder.py`

**Depends on**: 4.1.1 (Member C)

**Acceptance criteria**

- [ ] Output validates against schema.
- [ ] Hand-computed stats for the fixture match the module output.
- [ ] Switch definition documented.

#### 4.2.2 Notes, search & analytics endpoints

| When | Effort | Priority | Status | Branch |
|---|---|---|---|---|
| Tue 24 Nov Evening | 3 h | Medium | Not Started | `c/4.2.2-notes-search` |

Endpoints for timestamped notes (use case 2), instrument search across the library (use case 3) and per-case stats comparison (use case 5).

**Steps**

1. src/api/routes/notes.py: CRUD for notes {id, video_id, t_sec, text, author, created_at}.
2. src/api/routes/search.py: /api/search?tool=&min_s= scans stored timelines and returns matching segments sorted by video then start.
3. src/api/routes/analytics.py: /api/analytics?video_ids= returns stats blocks; include an aggregate (mean per-tool seconds, mean switches).
4. Tests for each route with two fixture timelines.

**Inputs**

- src/api/ (4.2.1)
- contracts/openapi.yaml

**Outputs (deliverables)**

- src/api/routes/notes.py
- src/api/routes/search.py
- src/api/routes/analytics.py

**Owned files**: `src/api/routes/notes.py`, `src/api/routes/search.py`, `src/api/routes/analytics.py`

**Depends on**: 4.2.1 (Member C)

**Acceptance criteria**

- [ ] Searching tool=clipper on fixtures returns exactly the clipper segments.
- [ ] Notes persist across server restart.
- [ ] Route tests pass in CI.

**Hand-off**: when merged, tag Member D in the PR (needed for 7.1.1).

#### 4.3.1 PDF report generator (English & Arabic)

| When | Effort | Priority | Status | Branch |
|---|---|---|---|---|
| Tue 24 Nov Evening → Wed 25 Nov Morning | 4 h | Medium | Not Started | `c/4.3.1-pdf` |

Generate a session report: case info, timeline bar chart, per-tool stats, instructor notes with timestamps, disclaimer; in EN or AR (RTL).

**Steps**

1. Implement src/reports/pdf_report.py with ReportLab: `render_report(timeline, notes, lang, out_path)`.
2. Draw the timeline as horizontal coloured bars (colours from contracts/classes.json).
3. Arabic: bundle Noto Naskh Arabic in src/reports/fonts/ (OFL licence), shape text with arabic-reshaper + python-bidi; right-align.
4. Strings in src/reports/strings.py (en/ar).
5. Wire GET /api/videos/{id}/report.pdf?lang= in src/api/routes/reports.py.
6. Golden test: generate both languages from fixtures; assert PDF opens and contains note text (pypdf).

**Inputs**

- contracts/timeline.schema.json
- tests/fixtures/sample_timeline.json

**Outputs (deliverables)**

- src/reports/pdf_report.py
- src/reports/strings.py
- src/reports/fonts/
- src/api/routes/reports.py

**Owned files**: `src/reports/`, `src/api/routes/reports.py`, `tests/unit/reports/`

**Depends on**: 4.1.2 (Member C), 4.2.2 (Member C)

**Acceptance criteria**

- [ ] EN and AR PDFs render with correct Arabic shaping and RTL layout (visual check by A).
- [ ] Report includes timeline chart, stats, notes and the 'educational, not diagnostic' disclaimer.
- [ ] Endpoint returns application/pdf.

**Hand-off**: when merged, tag Member D in the PR (needed for 7.1.1).

#### 4.1.3 Timeline evaluation vs ground truth

| When | Effort | Priority | Status | Branch |
|---|---|---|---|---|
| Wed 25 Nov Morning → Wed 25 Nov Afternoon | 3 h | High | Not Started | `c/4.1.3-timeline-eval` |

Measure success measure 2: agreement between predicted tool intervals and Cholec80 presence labels on the timeline evaluation videos; tune smoothing params on a subset.

**Steps**

1. Run src.inference.detect_video (B's module, unchanged) on each timeline-eval video.
2. Implement src/timeline/evaluate.py: resample predictions to 1 fps; per-tool frame-level precision/recall/F1, and segment IoU; overall macro-F1.
3. Compare raw (no smoothing) vs smoothed; try 3–4 values of window_s and min_segment_s on the 1 tuning video, report on the 2 reporting videos.
4. Write docs/timeline/TIMELINE_EVAL.md with tables and one example timeline plot per video.
5. Update configs/timeline.yaml defaults to the chosen parameters.

**Inputs**

- data/processed/presence/*.csv (2.3.1)
- src/inference/detect_video.py (3.3.1)
- models/weights/best.pt or baseline.pt

**Outputs (deliverables)**

- src/timeline/evaluate.py
- docs/timeline/TIMELINE_EVAL.md
- Tuned configs/timeline.yaml

**Owned files**: `src/timeline/evaluate.py`, `docs/timeline/`

**Depends on**: 4.1.2 (Member C), 2.3.1 (Member A), 3.3.1 (Member B)

**Acceptance criteria**

- [ ] Per-tool F1 table for raw vs smoothed on held-out timeline videos.
- [ ] Tuning and reporting videos are disjoint (stated).
- [ ] Smoothed macro-F1 ≥ raw macro-F1.

**Hand-off**: when merged, tag Member B, Member D in the PR (needed for 6.1.1, 7.2.1, 8.2.1).

#### 8.1.3 Report section: Timeline & System

| When | Effort | Priority | Status | Branch |
|---|---|---|---|---|
| Wed 25 Nov Afternoon | 2 h | Medium | Not Started | `c/8.1.3-report-system` |

Chapter on smoothing method, timeline evaluation, system architecture, API and PDF reporting.

**Steps**

1. Write docs/report/03_system.md: architecture diagram, data flow, smoothing algorithm, TIMELINE_EVAL results, API summary.
2. Include example timeline and PDF screenshot.

**Inputs**

- docs/timeline/TIMELINE_EVAL.md
- contracts/

**Outputs (deliverables)**

- docs/report/03_system.md

**Owned files**: `docs/report/03_system.md`

**Depends on**: 4.1.3 (Member C), 4.3.1 (Member C)

**Acceptance criteria**

- [ ] Raw vs smoothed table present; architecture diagram present.
- [ ] Reviewed by D.

**Hand-off**: when merged, tag Member D in the PR (needed for 8.1.4).

#### 8.2.2 Demo video

| When | Effort | Priority | Status | Branch |
|---|---|---|---|---|
| Wed 25 Nov Evening | 2 h | Medium | Not Started | `c/8.2.2-demo` |

3–4 minute recorded walkthrough of the 5 use cases on the v1.0.0 build (backup if the live demo fails).

**Steps**

1. Write a shot list per use case.
2. Record on the tagged build with demo data; add captions (EN, optional AR).
3. Export to docs/demo/ link (store video in Release/Drive, not Git).

**Inputs**

- v1.0.0 build
- Demo data

**Outputs (deliverables)**

- docs/demo/README.md with link
- Demo video file (Release)

**Owned files**: `docs/demo/`

**Depends on**: 7.2.1 (Member D)

**Acceptance criteria**

- [ ] Shows all 5 use cases in ≤4 min.
- [ ] Plays on the presentation laptop offline.

---

## Member D: Frontend Lead & Integration Owner

Team lead and integration owner. Owns the repo scaffold, interface contracts and fixtures, the web review workspace and library, the one-command local run, smoke tests, merging to develop/main and final report assembly.

**Load:** 11 tasks · 30 h · branch prefix `d/`

### Files and folders you own

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

### You receive from teammates

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

### You hand off

- **1.2.1** → Member A for 2.1.1 (Download & verify datasets): GitHub repo with develop + main, .github/CODEOWNERS
- **1.2.2** → Member A for 2.2.1 (VOC → YOLO conversion & class mapping): contracts/classes.json, contracts/detections.schema.json
- **1.2.2** → Member B for 3.3.1 (Video inference module (detections.jsonl)): contracts/classes.json, contracts/detections.schema.json
- **1.2.2** → Member C for 4.1.1 (Temporal smoothing): contracts/classes.json, contracts/detections.schema.json
- **1.2.2** → Member C for 4.2.1 (FastAPI service & background processing jobs): contracts/classes.json, contracts/detections.schema.json
- **5.1.1** → Member A for 5.2.2 (Analytics dashboard page): web/ app shell, web/src/api/
- **5.1.1** → Member A for 5.2.3 (Arabic localisation & RTL styling): web/ app shell, web/src/api/
- **7.1.1** → Member A for 6.2.1 (Usability study: scrubbing vs timeline): scripts/run_local.ps1, scripts/run_local.sh
- **7.2.1** → Member C for 8.2.2 (Demo video): Tag v1.0.0, CHANGELOG.md

### Tasks

#### 1.1.1 Problem statement, use cases & business model page

| When | Effort | Priority | Status | Branch |
|---|---|---|---|---|
| Mon 23 Nov Evening | 6 h | High | Completed | `d/1.1.1-problem-page` |

Bilingual (EN/AR) page defining the problem, objective, success measures, proposed solution, top-5 use cases and business model. This already exists as or_intelligence_problem_usecases.html.

**Steps**

1. Write problem statement and scope limits.
2. Define the 6-instrument objective and 3 success measures.
3. Describe 5 use cases with users, scenario and value.
4. Add business model and indicative pricing.
5. Publish bilingual page with EN/AR toggle.

**Inputs**

- Course brief
- Domain research on laparoscopic training

**Outputs (deliverables)**

- docs/problem/or_intelligence_problem_usecases.html

**Owned files**: `docs/problem/`

**Depends on**: none, start immediately

**Acceptance criteria**

- [ ] Page states problem, objective, success measures, 5 use cases and business model in EN and AR.
- [ ] Page committed under docs/problem/.

#### 1.2.1 Repository scaffold, branch protection & CI skeleton

| When | Effort | Priority | Status | Branch |
|---|---|---|---|---|
| Mon 23 Nov Evening | 1 h | High | Not Started | `d/1.2.1-scaffold` |

Create the GitHub repository with the agreed folder tree, empty package stubs for every owner, CODEOWNERS that encodes file ownership, protected main/develop branches and a CI workflow that runs lint + tests.

**Steps**

1. Create repo or-intelligence; add .gitignore (data/, runs/, models/weights/*.pt, node_modules/, .env).
2. Create the folder tree from PROJECT_STRUCTURE.md with __init__.py stubs in src/data, src/models, src/inference, src/timeline, src/api, src/reports (scaffold exception: after this single commit each path belongs only to its owner).
3. Create requirements/base.txt and empty owner files requirements/{data,ml,api}.txt (same scaffold exception); pyproject.toml with ruff + pytest config.
4. Write .github/CODEOWNERS mapping each path to its owner (copy the File Ownership Matrix).
5. Create branch develop; protect main and develop: PR required, 1 approval, CI must pass, no force-push.
6. Add .github/workflows/ci.yml: ruff, pytest tests/unit, and `npm ci && npm run build` in web/.
7. Add PR template (.github/pull_request_template.md) with WBS ID, scope, tests, screenshots checklist.
8. Invite A, B, C; confirm each can open a PR from their prefix branch.

**Inputs**

- PROJECT_STRUCTURE.md

**Outputs (deliverables)**

- GitHub repo with develop + main
- .github/CODEOWNERS
- .github/workflows/ci.yml
- PR template

**Owned files**: `.github/`, `.gitignore`, `pyproject.toml`, `requirements/base.txt`

**Depends on**: none, start immediately

**Acceptance criteria**

- [ ] A test PR from each member triggers CI and requests the correct CODEOWNER review.
- [ ] Direct push to main/develop is rejected.
- [ ] CI passes on the empty scaffold.

**Hand-off**: when merged, tag Member A in the PR (needed for 2.1.1).

#### 1.2.2 Interface contracts & shared test fixtures ⚠ critical integration point

| When | Effort | Priority | Status | Branch |
|---|---|---|---|---|
| Mon 23 Nov Evening | 2 h | High | Not Started | `d/1.2.2-contracts` |

Freeze the data contracts (class map, detections, timeline, HTTP API) and ship small fixture files so every member can build and test their module in parallel without waiting for upstream work.

**Steps**

1. Write contracts/classes.json (6 classes, ids 0–5, UI colours).
2. Write contracts/detections.schema.json and contracts/timeline.schema.json (JSON Schema draft 2020-12) matching the Contracts section.
3. Write contracts/openapi.yaml for all endpoints in contract C6, including error responses.
4. Create tests/fixtures/sample_detections.jsonl (≈600 frames, 2 min at 5 fps, with deliberate flicker) and tests/fixtures/sample_timeline.json (valid against schema).
5. Create tests/fixtures/sample_video.mp4 (≤10 MB, 2 min; synthetic or a public demo clip permitted by licence).
6. Add tests/contracts/test_schemas.py validating fixtures against schemas (jsonschema).
7. Hold a 30-min contract review with A, B, C; record sign-off in contracts/CHANGELOG.md. Any later change = PR to contracts/ approved by D + affected owners.

**Inputs**

- Project page (instrument list)
- PROJECT_STRUCTURE.md

**Outputs (deliverables)**

- contracts/classes.json
- contracts/detections.schema.json
- contracts/timeline.schema.json
- contracts/openapi.yaml
- tests/fixtures/*
- contracts/CHANGELOG.md

**Owned files**: `contracts/`, `tests/fixtures/`, `tests/contracts/`

**Depends on**: 1.2.1 (Member D)

**Acceptance criteria**

- [ ] Fixtures validate against schemas in CI.
- [ ] A, B and C have signed off in contracts/CHANGELOG.md.
- [ ] openapi.yaml lints with no errors (e.g. `npx @redocly/cli lint`).

**Hand-off**: when merged, tag Member A, Member B, Member C in the PR (needed for 2.2.1, 3.3.1, 4.1.1, 4.2.1).

#### 5.1.1 Web app shell, API client & upload flow

| When | Effort | Priority | Status | Branch |
|---|---|---|---|---|
| Tue 24 Nov Morning | 3 h | High | Not Started | `d/5.1.1-shell` |

React + Vite + TypeScript shell: routing, layout, typed API client generated from openapi.yaml, i18n loader, upload page with processing status polling.

**Steps**

1. Create web/ with Vite React-TS; add react-router; set up layout and nav (Upload, Review, Library, Analytics).
2. Generate typed client from contracts/openapi.yaml (openapi-typescript) into web/src/api/; add a mock mode using tests/fixtures data.
3. Implement web/src/i18n/index.ts + en.json; RTL switch toggles <html dir>. Load locale files with import.meta.glob('./*.json') so Member A can add ar.json without touching index.ts; load styles/rtl.css only if present.
4. Upload page web/src/pages/Upload/: drag-and-drop, progress bar from GET status polling every 2 s, redirect to Review when done.
5. Auto-register routes with import.meta.glob('../pages/*/index.tsx') so Member A's web/src/pages/Analytics/ appears at /analytics without D editing it and without A editing the router.

**Inputs**

- contracts/openapi.yaml
- tests/fixtures/

**Outputs (deliverables)**

- web/ app shell
- web/src/api/
- web/src/pages/Upload/
- web/src/i18n/index.ts
- web/src/i18n/en.json

**Owned files**: `web/package.json`, `web/vite.config.ts`, `web/src/app/`, `web/src/api/`, `web/src/pages/Upload/`, `web/src/i18n/index.ts`, `web/src/i18n/en.json`

**Depends on**: 1.2.2 (Member D)

**Acceptance criteria**

- [ ] `npm run build` passes in CI.
- [ ] Upload in mock mode reaches Review page.
- [ ] Adding a new folder under web/src/pages/ or a new locale JSON requires no edit to D's files (verified with a throwaway test page).

**Hand-off**: when merged, tag Member A in the PR (needed for 5.2.2, 5.2.3).

#### 5.1.2 Video player + interactive instrument timeline ⚠ critical integration point

| When | Effort | Priority | Status | Branch |
|---|---|---|---|---|
| Tue 24 Nov Morning → Tue 24 Nov Evening | 5 h | High | Not Started | `d/5.1.2-timeline-ui` |

The core review screen: HTML5 video player synced with a colour-coded, zoomable timeline; clicking a bar seeks the video; playhead follows playback.

**Steps**

1. web/src/components/Timeline/: one lane per tool, bars from timeline.tools, colours from classes.json, time axis with mm:ss ticks.
2. Click bar → video.currentTime = start; keyboard: ←/→ previous/next segment of selected tool.
3. Playhead synced via timeupdate; zoom (1×–8×) and horizontal scroll for long videos.
4. Highlight 'unusual patterns': segments longer than configurable thresholds (e.g. irrigation > 60 s) and dense switching windows.
5. web/src/pages/Review/: player + timeline + stats panel (per-tool time, switches).
6. Component tests with Vitest + Testing Library using sample_timeline.json.

**Inputs**

- tests/fixtures/sample_timeline.json
- web/src/api/

**Outputs (deliverables)**

- web/src/components/Timeline/
- web/src/components/VideoPlayer/
- web/src/pages/Review/

**Owned files**: `web/src/components/Timeline/`, `web/src/components/VideoPlayer/`, `web/src/pages/Review/`

**Depends on**: 5.1.1 (Member D)

**Acceptance criteria**

- [ ] Clicking any bar seeks within ±0.5 s of segment start.
- [ ] Renders a 90-min timeline at 60 fps scroll without lag (Chrome performance check).
- [ ] Component tests pass.

#### 5.1.3 Timestamped notes panel & report download

| When | Effort | Priority | Status | Branch |
|---|---|---|---|---|
| Tue 24 Nov Evening | 2 h | Medium | Not Started | `d/5.1.3-notes-ui` |

Instructor notes at the current playhead time, listed and clickable; download PDF report in EN/AR.

**Steps**

1. web/src/components/NotesPanel/: add note at current time (prefilled mm:ss), list sorted by time, click to seek, delete.
2. Show note markers on the timeline.
3. Report button: GET /report.pdf?lang= with language selector.
4. Tests in mock mode.

**Inputs**

- web/src/pages/Review/
- contracts/openapi.yaml

**Outputs (deliverables)**

- web/src/components/NotesPanel/

**Owned files**: `web/src/components/NotesPanel/`

**Depends on**: 5.1.2 (Member D)

**Acceptance criteria**

- [ ] Note added at 12:34 appears at 12:34 on the timeline and in the list.
- [ ] Clicking a note seeks the video.
- [ ] PDF downloads in both languages against the real API.

#### 5.2.1 Library search page

| When | Effort | Priority | Status | Branch |
|---|---|---|---|---|
| Wed 25 Nov Morning | 2 h | Medium | Not Started | `d/5.2.1-library` |

Use case 3: list all processed videos and search segments by instrument and minimum duration; each result opens Review at that timestamp.

**Steps**

1. web/src/pages/Library/: video list (title, duration, status) + search form (tool, min duration).
2. Results grouped by video; click → /review/:id?t=start.
3. Review page reads ?t= and seeks on load (small change inside D's own Review page).

**Inputs**

- /api/videos
- /api/search

**Outputs (deliverables)**

- web/src/pages/Library/

**Owned files**: `web/src/pages/Library/`

**Depends on**: 5.1.1 (Member D)

**Acceptance criteria**

- [ ] 'clipper' search on fixtures lists exactly the clipper segments.
- [ ] Clicking a result opens Review at the right time.

#### 7.1.1 One-command local run & integration ⚠ critical integration point

| When | Effort | Priority | Status | Branch |
|---|---|---|---|---|
| Wed 25 Nov Morning → Wed 25 Nov Afternoon | 3 h | High | Not Started | `d/7.1.1-compose` |

Integrate API (with real model), web app and storage into a single local start command. Integration owner merges feature branches into develop (merge windows Mon/Tue 21:00, Wed 12:00) and resolves conflicts. Docker is optional and only if time remains.

**Steps**

1. scripts/run_local.ps1 and scripts/run_local.sh: fetch weights, start uvicorn on :8000, build web and serve it with Vite preview on :8080 (proxy /api).
2. Optional stretch: docker/Dockerfile.api + docker-compose.yml.
3. Merge all completed feature PRs into develop; run full unit + contract tests.
4. Smoke test with a real 10–30 min video; record results in docs/integration/INTEGRATION_LOG.md.

**Inputs**

- src/api (4.2.x, 4.3.1)
- src/inference (3.3.1)
- web (5.x)
- models/weights/best.pt (3.3.2)

**Outputs (deliverables)**

- scripts/run_local.ps1
- scripts/run_local.sh
- docs/integration/INTEGRATION_LOG.md
- (optional) docker/, docker-compose.yml

**Owned files**: `scripts/`, `docker/`, `docker-compose.yml`, `docs/integration/`

**Depends on**: 4.2.2 (Member C), 4.3.1 (Member C), 3.3.2 (Member B), 5.1.3 (Member D), 5.2.1 (Member D), 5.2.2 (Member A), 5.2.3 (Member A)

**Acceptance criteria**

- [ ] The run script on a clean clone serves the app on http://localhost:8080.
- [ ] A real video processes end-to-end; timeline and PDF work.
- [ ] develop CI green by Wed 18:00.

**Hand-off**: when merged, tag Member A in the PR (needed for 6.2.1).

#### 6.3.1 End-to-end smoke tests (5 use cases)

| When | Effort | Priority | Status | Branch |
|---|---|---|---|---|
| Wed 25 Nov Afternoon | 2 h | High | Not Started | `d/6.3.1-e2e` |

Scripted smoke checklist covering the 5 use cases on the integrated stack, plus one automated Playwright test for the core flow.

**Steps**

1. Write tests/e2e/SMOKE_CHECKLIST.md: upload → done → timeline visible; click clipper bar seeks; add note → appears in PDF; library search → opens at timestamp; analytics shows 2 cases.
2. Automate the core flow (upload → timeline → click bar) in tests/e2e/core.spec.ts with Playwright against the local run script.
3. Run the checklist on the integrated build; tick results in the file.
4. File bugs as GitHub issues assigned to the owning member (per ownership matrix), each with a fix deadline of Wed 18:00.

**Inputs**

- Integrated local stack (7.1.1)

**Outputs (deliverables)**

- tests/e2e/SMOKE_CHECKLIST.md (ticked)
- tests/e2e/core.spec.ts

**Owned files**: `tests/e2e/`

**Depends on**: 7.1.1 (Member D)

**Acceptance criteria**

- [ ] All 5 checklist scenarios pass on the release candidate.
- [ ] Core Playwright test passes.
- [ ] Every failure routed to exactly one owner.

#### 7.2.1 Release candidate v1.0.0 & demo freeze ⚠ critical integration point

| When | Effort | Priority | Status | Branch |
|---|---|---|---|---|
| Wed 25 Nov Evening | 1 h | High | Not Started | `d/7.2.1-release` |

Freeze features, merge develop → main, tag v1.0.0, prepare the demo machine.

**Steps**

1. Confirm E2E, timeline eval and test eval are done; only bug-fix PRs allowed after freeze.
2. Merge develop → main via PR; tag v1.0.0; write CHANGELOG.md.
3. Prepare demo dataset: 3 processed videos with notes in storage/.

**Inputs**

- 6.3.1 results
- 4.1.3
- 3.2.1

**Outputs (deliverables)**

- Tag v1.0.0
- CHANGELOG.md
- Demo data

**Owned files**: `CHANGELOG.md`

**Depends on**: 6.3.1 (Member D), 4.1.3 (Member C), 3.2.1 (Member B)

**Acceptance criteria**

- [ ] v1.0.0 tag on main; CI green.
- [ ] Demo runs offline from the tagged build.

**Hand-off**: when merged, tag Member C in the PR (needed for 8.2.2).

#### 8.1.4 Final report assembly & README

| When | Effort | Priority | Status | Branch |
|---|---|---|---|---|
| Wed 25 Nov Evening | 3 h | High | Not Started | `d/8.1.4-report` |

Assemble introduction, use cases, sections 01–03, frontend chapter, conclusion and limitations into the final report; write the repository README.

**Steps**

1. Write docs/report/00_intro.md (problem, use cases from 1.1.1) and 04_frontend_conclusion.md (UI, limits: one procedure, non-commercial data, not diagnostic; future work).
2. docs/report/main.md includes all sections; export to PDF with pandoc (docs/report/build.sh).
3. README.md: overview, quick start (docker compose), screenshots, team & ownership, licences.

**Inputs**

- docs/report/01–03
- docs/usability/RESULTS.md
- docs/model/BENCHMARK.md

**Outputs (deliverables)**

- docs/report/main.md
- docs/report/00_intro.md
- docs/report/04_frontend_conclusion.md
- docs/report/build.sh
- Final report PDF
- README.md

**Owned files**: `docs/report/main.md`, `docs/report/00_intro.md`, `docs/report/04_frontend_conclusion.md`, `docs/report/build.sh`, `README.md`

**Depends on**: 8.1.1 (Member A), 8.1.2 (Member B), 8.1.3 (Member C), 6.1.1 (Member B)

**Acceptance criteria**

- [ ] Report PDF builds from source.
- [ ] All 3 success measures reported with numbers.
- [ ] README quick start works on a clean clone.

