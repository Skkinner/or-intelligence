# WBS Validation

> **OR Intelligence** · Computer Vision Final Project · Deadline **Wednesday 25 Nov 2026, 23:59**  
> Generated from the same data as `project_wbs_dashboard.html`. Member names are placeholders (A–D); rename them in the dashboard.

## Result

**0 hard conflicts** (the build refuses to generate files if any exist) · **0 warnings**.

| Check | Result |
|---|---|
| Every task has exactly one accountable owner | ✓ 37/37 |
| No duplicate task names or outputs produced by two members | ✓ |
| One owner per file/folder, no cross-owner folder nesting | ✓ 95 paths |
| All dependencies exist and are acyclic | ✓ |
| Schedule respects dependencies and ends by the deadline | ✓ last task ends Wed 25 Nov Evening |
| Every task has steps, outputs, owned files, acceptance criteria | ✓ |
| Every requirement maps to at least one task | ✓ 17/17 |
| Every deliverable maps to producing tasks | ✓ 9/9 |
| Workload within ±20% of mean | ✓ 23–30 h, mean 25.5 h |
| No member over 5 h in one work block | ✓ |

## Requirement coverage

| ID | Requirement | Source | Tasks | Owners |
|---|---|---|---|---|
| R1 | Detect 6 instruments per frame (grasper, bipolar, hook, scissors, clipper, irrigator) | Project objective | 2.2.1, 3.1.1, 3.1.2 | A, B |
| R2 | Model metrics: mAP@0.5 and per-instrument precision/recall on a video-level held-out test set | Success measures | 2.2.2, 3.2.1 | A, B |
| R3 | Temporal smoothing to remove flicker | Proposed solution | 4.1.1 | C |
| R4 | Colour-coded instrument timeline (e.g. hook 03:10–09:45) | Proposed solution | 4.1.2, 5.1.2 | C, D |
| R5 | Timeline agreement with ground-truth presence labels | Success measures | 2.3.1, 4.1.3 | A, C |
| R6 | Upload a recorded video and process it | Proposed solution | 3.3.1, 4.2.1, 5.1.1 | B, C, D |
| R7 | Click a timeline bar to jump the video to that moment | Use case 1, 4 | 5.1.2 | D |
| R8 | Timestamped instructor notes | Use case 2 | 4.2.2, 5.1.3 | C, D |
| R9 | PDF report export including instructor notes | Use case 2 | 4.3.1 | C |
| R10 | Searchable library indexed by instrument ("show all clipping segments") | Use case 3 | 4.2.2, 5.2.1 | C, D |
| R11 | Find unusual tool patterns / clips quickly (long irrigation, repeated switches) | Use case 4 | 4.1.2, 5.1.2 | C, D |
| R12 | Per-case statistics: time per instrument, total time, tool switches; compare across cases | Use case 5 | 4.1.2, 4.2.2, 5.2.2 | C, A |
| R13 | Arabic-language interface and reports | Gap in existing tools / business model | 4.3.1, 5.2.3 | C, A |
| R14 | Usability test: time to find a moment, scrubbing vs timeline | Success measures | 6.2.1 | A |
| R15 | Public research data only; non-commercial licence; educational, not diagnostic | Scope & limits / note | 1.3.1, 3.3.2, 8.1.4 | A, B, D |
| R16 | Problem definition, use cases and business model documented | Project page | 1.1.1 | D |
| R17 | Final project report and presentation | Final project delivery | 8.1.4, 8.2.1, 8.2.2 | D, B, C |

## Deliverables

| ID | Deliverable | Tasks |
|---|---|---|
| D1 | Labelled YOLO dataset + video-level split + EDA report | 2.2.1, 2.2.2, 2.4.1 |
| D2 | Trained YOLO weights + evaluation report (mAP@0.5, per-class P/R) + model card | 3.1.2, 3.2.1, 3.3.2 |
| D3 | Video inference module (detections.jsonl contract) | 3.3.1 |
| D4 | Timeline engine (smoothing, intervals, statistics) + timeline evaluation | 4.1.1, 4.1.2, 4.1.3 |
| D5 | Backend API + PDF report generator (EN/AR) | 4.2.1, 4.2.2, 4.3.1 |
| D6 | Web app: review workspace, notes, library search, analytics, Arabic/RTL | 5.1.1, 5.1.2, 5.1.3, 5.2.1, 5.2.2, 5.2.3 |
| D7 | Usability study results (manual scrubbing vs timeline) | 6.2.1 |
| D8 | Integrated, containerised release candidate (v1.0.0) | 7.1.1, 7.2.1 |
| D9 | Final report, README, slide deck, demo video | 8.1.4, 8.2.1, 8.2.2 |

## Ownership verification

Each row below is one path with exactly one owner (full matrix in PROJECT_STRUCTURE.md).

| Member | Paths owned | Tasks |
|---|---|---|
| Member A | 24 | 1.3.1, 2.1.1, 2.2.1, 2.2.2, 2.3.1, 2.4.1, 5.2.2, 5.2.3, 6.2.1, 8.1.1 |
| Member B | 20 | 3.1.1, 3.1.2, 3.2.1, 3.3.1, 3.3.2, 6.1.1, 8.1.2, 8.2.1 |
| Member C | 20 | 4.1.1, 4.1.2, 4.1.3, 4.2.1, 4.2.2, 4.3.1, 8.1.3, 8.2.2 |
| Member D | 31 | 1.1.1, 1.2.1, 1.2.2, 5.1.1, 5.1.2, 5.1.3, 5.2.1, 6.3.1, 7.1.1, 7.2.1, 8.1.4 |

## Dependency validation

| Task | Owner | When | Depends on | Cross-member inputs |
|---|---|---|---|---|
| 1.1.1 Problem statement, use cases & business model page | D | Mon 23 Nov Evening | — | — |
| 1.2.1 Repository scaffold, branch protection & CI skeleton | D | Mon 23 Nov Evening | — | — |
| 1.2.2 Interface contracts & shared test fixtures | D | Mon 23 Nov Evening | 1.2.1 | — |
| 1.3.1 Dataset licensing & ethics checklist | A | Mon 23 Nov Evening | — | — |
| 2.1.1 Download & verify datasets | A | Mon 23 Nov Evening | 1.3.1, 1.2.1 | 1.2.1 (D) |
| 2.2.1 VOC → YOLO conversion & class mapping | A | Mon 23 Nov Evening → Tue 24 Nov Morning | 2.1.1, 1.2.2 | 1.2.2 (D) |
| 2.2.2 Video-level train/val/test split | A | Tue 24 Nov Morning | 2.2.1 | — |
| 2.3.1 Timeline ground truth from Cholec80 presence labels | A | Tue 24 Nov Morning → Tue 24 Nov Afternoon | 2.1.1 | — |
| 2.4.1 EDA & class-balance report | A | Tue 24 Nov Afternoon | 2.2.2 | — |
| 3.1.1 Baseline YOLO training | B | Tue 24 Nov Morning → Tue 24 Nov Afternoon | 2.2.2 | 2.2.2 (A) |
| 3.1.2 Augmentation & hyper-parameter experiments | B | Tue 24 Nov Evening | 3.1.1, 2.4.1 | 2.4.1 (A) |
| 3.2.1 Held-out test evaluation report | B | Wed 25 Nov Morning | 3.1.2 | — |
| 3.3.1 Video inference module (detections.jsonl) | B | Mon 23 Nov Evening → Tue 24 Nov Afternoon | 1.2.2 | 1.2.2 (D) |
| 3.3.2 Model card & weights release | B | Wed 25 Nov Morning | 3.2.1 | — |
| 4.1.1 Temporal smoothing | C | Mon 23 Nov Evening | 1.2.2 | 1.2.2 (D) |
| 4.1.2 Interval builder & per-case statistics | C | Tue 24 Nov Morning | 4.1.1 | — |
| 4.1.3 Timeline evaluation vs ground truth | C | Wed 25 Nov Morning → Wed 25 Nov Afternoon | 4.1.2, 2.3.1, 3.3.1 | 2.3.1 (A), 3.3.1 (B) |
| 4.2.1 FastAPI service & background processing jobs | C | Mon 23 Nov Evening → Tue 24 Nov Afternoon | 1.2.2 | 1.2.2 (D) |
| 4.2.2 Notes, search & analytics endpoints | C | Tue 24 Nov Evening | 4.2.1 | — |
| 4.3.1 PDF report generator (English & Arabic) | C | Tue 24 Nov Evening → Wed 25 Nov Morning | 4.1.2, 4.2.2 | — |
| 5.1.1 Web app shell, API client & upload flow | D | Tue 24 Nov Morning | 1.2.2 | — |
| 5.1.2 Video player + interactive instrument timeline | D | Tue 24 Nov Morning → Tue 24 Nov Evening | 5.1.1 | — |
| 5.1.3 Timestamped notes panel & report download | D | Tue 24 Nov Evening | 5.1.2 | — |
| 5.2.1 Library search page | D | Wed 25 Nov Morning | 5.1.1 | — |
| 5.2.2 Analytics dashboard page | A | Tue 24 Nov Evening → Wed 25 Nov Morning | 5.1.1 | 5.1.1 (D) |
| 5.2.3 Arabic localisation & RTL styling | A | Wed 25 Nov Morning | 5.1.1 | 5.1.1 (D) |
| 6.1.1 Inference performance benchmark | B | Wed 25 Nov Afternoon | 3.3.2, 4.1.3 | 4.1.3 (C) |
| 6.2.1 Usability study: scrubbing vs timeline | A | Wed 25 Nov Afternoon → Wed 25 Nov Evening | 7.1.1 | 7.1.1 (D) |
| 6.3.1 End-to-end smoke tests (5 use cases) | D | Wed 25 Nov Afternoon | 7.1.1 | — |
| 7.1.1 One-command local run & integration | D | Wed 25 Nov Morning → Wed 25 Nov Afternoon | 4.2.2, 4.3.1, 3.3.2, 5.1.3, 5.2.1, 5.2.2, 5.2.3 | 4.2.2 (C), 4.3.1 (C), 3.3.2 (B), 5.2.2 (A), 5.2.3 (A) |
| 7.2.1 Release candidate v1.0.0 & demo freeze | D | Wed 25 Nov Evening | 6.3.1, 4.1.3, 3.2.1 | 4.1.3 (C), 3.2.1 (B) |
| 8.1.1 Report section: Data | A | Wed 25 Nov Evening | 2.4.1, 6.2.1 | — |
| 8.1.2 Report section: Model | B | Wed 25 Nov Afternoon | 3.2.1, 6.1.1 | — |
| 8.1.3 Report section: Timeline & System | C | Wed 25 Nov Afternoon | 4.1.3, 4.3.1 | — |
| 8.1.4 Final report assembly & README | D | Wed 25 Nov Evening | 8.1.1, 8.1.2, 8.1.3, 6.1.1 | 8.1.1 (A), 8.1.2 (B), 8.1.3 (C), 6.1.1 (B) |
| 8.2.1 Presentation slide deck | B | Wed 25 Nov Afternoon → Wed 25 Nov Evening | 2.4.1, 3.2.1, 4.1.3 | 2.4.1 (A), 4.1.3 (C) |
| 8.2.2 Demo video | C | Wed 25 Nov Evening | 7.2.1 | 7.2.1 (D) |

Critical integration points: **1.2.2** Interface contracts & shared test fixtures · **2.2.2** Video-level train/val/test split · **3.3.1** Video inference module (detections.jsonl) · **4.2.1** FastAPI service & background processing jobs · **5.1.2** Video player + interactive instrument timeline · **7.1.1** One-command local run & integration · **7.2.1** Release candidate v1.0.0 & demo freeze

## Workload assessment

| Member | Role | Tasks | High priority | Total h | Remaining h | vs mean |
|---|---|---|---|---|---|---|
| Member A | Data Engineer & UX Research | 10 | 6 | 23 | 23 | -10% |
| Member B | ML Engineer | 8 | 5 | 24 | 24 | -6% |
| Member C | Backend & Timeline Engineer | 8 | 4 | 25 | 25 | -2% |
| Member D | Frontend Lead & Integration Owner | 11 | 9 | 30 | 24 | +18% |

Member D's total includes the 6 h already spent on the completed problem/use-case page (1.1.1). Remaining hours: A 23 h, B 24 h, C 25 h, D 24 h.

**Hours per block** (planned, spread evenly across a task's blocks):

| Member | Mon Eve | Tue Mor | Tue Aft | Tue Eve | Wed Mor | Wed Aft | Wed Eve |
|---|---|---|---|---|---|---|---|
| A | 4.5 | 4.0 | 3.5 | 2.0 | 4.0 | 1.5 | 3.5 |
| B | 1.7 | 3.7 | 3.7 | 4.0 | 4.0 | 5.0 | 2.0 |
| C | 4.7 | 4.7 | 1.7 | 5.0 | 3.5 | 3.5 | 2.0 |
| D | 3.0 | 4.7 | 1.7 | 3.7 | 3.5 | 3.5 | 4.0 |

## Conflicts found and resolved while planning

| Issue | Resolution |
|---|---|
| Draft plan had 8 weeks / ~270 h of work; the real deadline is Wed 25 Nov 23:59 (≈2.5 days). | Re-planned into 7 dated work blocks with an MVP scope: 1 baseline + 2 tuning runs, 3 timeline-eval videos, a pilot usability test (≥3 people), a smoke checklist + 1 Playwright test, and a run script instead of Docker. About 25 h per member. |
| Inference module (B) originally waited on the first trained weights, which blocked the API (C) until Tuesday afternoon. | 3.3.1 is built Monday night against COCO-pretrained yolov8n.pt and swaps weights later; the dependency on 3.1.1 was removed. |
| Cholec80 access needs an approval request that will probably not arrive before the deadline. | 1.3.1 decides on Monday evening: use Cholec80 only if access already exists, otherwise use presence labels from held-out m2cai16-tool videos. |
| The web router and i18n loader (D) would have to import A's Analytics page and ar.json, so both would edit the same files. | D's shell auto-discovers pages and locale files with import.meta.glob. A adds files only inside their own paths. |
| A single requirements.txt would be edited by A, B and C at the same time. | Split into requirements/{base (D), data (A), ml (B), api (C)}.txt. |
| A's analytics charts may need a new npm package in web/package.json, which D owns. | A opens a PR that touches only package.json + lockfile; D approves it. Listed in shared-file rules. |
| Everyone writing one shared final report file would cause merge conflicts. | One file per section (01_data A, 02_model B, 03_system C, main + 00/04 D). D assembles them by include, not by copy-editing. |
| The benchmark (B) needs timeline F1 code that C owns. | B calls src/timeline/evaluate.py read-only. Signature changes go through C. |
| The API (C) needs PDF routing inside src/api/, which could collide with D's integration work. | C owns all of src/api/ including routes/reports.py. D owns only scripts/, docker/ and the root deployment files. |
| The slide deck originally depended on report sections that are finished in the last block, which left no time for slides. | 8.2.1 now depends on EDA, test evaluation and timeline evaluation (ready by Wed afternoon). Usability numbers are added in the final block. |
| Initial scaffold creates __init__.py stubs in every member's folder. | Scaffold exception: after the single scaffold commit by D, each path belongs only to its owner (CODEOWNERS enforces this). |

## Remaining risks & assumptions

| Risk | Impact | Mitigation | Owner |
|---|---|---|---|
| Cholec80 access not available in time | No ground truth for success measure 2 | Fallback to held-out m2cai16-tool presence labels (decided Mon evening in 1.3.1) | A |
| m2cai16-tool-locations is small (~2.5k frames); rare classes (scissors, clipper) may score low | Lower mAP for those tools | Oversampling/augmentation in 3.1.2; report per-class honestly | B |
| Free GPU quota or session limits interrupt training | best.pt late, M4 slips | Start baseline Tue 09:00, save checkpoints every epoch, run the 2 experiments in parallel sessions | B |
| Possible overlap between m2cai16 training videos and timeline-eval videos | Inflated timeline metrics | Overlap check documented in 2.3.1; pick clearly separate videos | A |
| Arabic PDF shaping issues | Arabic report unreadable | arabic-reshaper + python-bidi + bundled Noto Naskh; A reviews Wed morning | C |
| Integration surprises in the last day | Missed deadline | Contracts + fixtures frozen Mon; merge windows each evening; feature freeze Wed 18:00 | D |
| Usability pilot has few participants (≥3) | Weak statistical evidence | Report as a pilot with medians; no significance claims | A |
| Little slack: a member losing a block | Tasks slip | Stretch items (Docker, benchmark F1, 2nd experiment) are cut first; D re-assigns at stand-up | D |

**Assumptions**

- Team of 4 (Members A–D). Real names are not yet known: they are editable in the dashboard and stored locally.
- No code exists yet; every task except 1.1.1 (problem & use-case page, which exists) starts as Not Started.
- Hard deadline: Wednesday 25 Nov 2026, 23:59. Work starts Monday 23 Nov evening, which gives 7 working blocks of about 4–5 h. Each member's load is about 25 h, so this is an MVP plan: one baseline model plus 1–2 tuning runs, a small usability test, and a one-command local run instead of a hardened deployment.
- Bounding-box training data comes from m2cai16-tool-locations (public, VOC-format boxes). Timeline ground truth uses Cholec80 tool-presence labels (1 fps) if the team already has access. A new Cholec80 access request will likely not be approved before Wednesday, so the fallback is presence labels from the m2cai16-tool videos that are held out from detection training (task 1.3.1 decides on Monday evening).
- Stack: Python 3.11, Ultralytics YOLO (v8/11), FastAPI + SQLite, React + Vite + TypeScript, ReportLab for PDF. A free GPU (Kaggle or Colab) is used for training; training runs in the background while members build other modules.
- Daily sync: 10-minute stand-up at 09:00 Tue and Wed, plus a 21:00 merge window each evening run by Member D.

**Cut first if time runs short:** Docker (7.1.1 stretch), F1-vs-fps analysis (6.1.1 optional step), second tuning experiment (3.1.2), Arabic demo captions (8.2.2).
