# Project Plan

> **OR Intelligence** · Computer Vision Final Project · Deadline **Wednesday 25 Nov 2026, 23:59**  
> Markdown version of `docs/planning/project_wbs_dashboard.html` (original task IDs and dependencies preserved).

**Laparoscopic instrument detection → clickable instrument timeline for surgical education**

A web-based surgical video review platform. A reviewer uploads a recorded laparoscopic cholecystectomy; a fine-tuned YOLO detector locates 6 instruments (grasper, bipolar, hook, scissors, clipper, irrigator) in sampled frames; temporal smoothing removes flicker; the result is a colour-coded instrument timeline where clicking a bar jumps the video to that moment. Sessions export as a PDF report with timestamped instructor notes (English / Arabic).

## Changes made at repository setup

- Branch names follow feature/member-<a|b|c|d>-<wbs-id>-<slug>, as requested at repository setup. The plan's original names are kept in planBranch.
- Task 7.1.2 added: the course brief requires Deployment Files, so Docker moved from an optional stretch inside 7.1.1 to its own task (Member D, 1 h, Wed afternoon). 7.2.1 now also depends on 7.1.2.
- src/common/contracts.py (read-only contract helpers) added under Member D, who owns contracts/.
- The scaffold, contract drafts and synthetic fixtures were pre-created at setup. Tasks 1.2.1 and 1.2.2 stay open until their remaining acceptance criteria are met (branch protection check, member test PRs, contract sign-off, sample_video.mp4).
- Data and model work happens in two Colab notebooks that follow the WBS owners: notebooks/01_Data.ipynb (Member A: 2.1.1, 2.2.1, 2.2.2, 2.4.1) and notebooks/02_Model.ipynb (Member B: 3.1.1, 3.1.2, 3.2.1, 3.3.2). A hands the ready dataset to B as MyDrive/or-intelligence/data/yolo_dataset.zip. The command-line starter scripts for these tasks were removed; src/inference/detect_video.py (3.3.1) stays because the app imports it.

## Schedule (work blocks)

| Block | Day | Part | Hours |
|---|---|---|---|
| 1 | Mon 23 Nov | Evening | 18:00–23:00 |
| 2 | Tue 24 Nov | Morning | 09:00–13:00 |
| 3 | Tue 24 Nov | Afternoon | 14:00–18:00 |
| 4 | Tue 24 Nov | Evening | 19:00–23:00 |
| 5 | Wed 25 Nov | Morning | 09:00–13:00 |
| 6 | Wed 25 Nov | Afternoon | 14:00–18:00 |
| 7 | Wed 25 Nov | Evening | 19:00–23:59 |

## Milestones

| ID | Milestone | Due | Gate tasks | Meaning |
|---|---|---|---|---|
| M1 | Repo ready & contracts frozen | Mon 23 Nov 23:00 | 1.2.1, 1.2.2, 1.3.1 | Everyone can work in parallel against fixtures. |
| M2 | Training dataset ready | Tue 24 Nov 12:00 | 2.2.2 | YOLO dataset and video-level split handed to B. |
| M3 | Pipeline works on fixtures | Tue 24 Nov 18:00 | 3.3.1, 4.1.2, 4.2.1 | Inference, timeline engine and API each pass their tests independently on fixtures. |
| M4 | Final weights & review UI | Tue 24 Nov 23:00 | 3.1.2, 5.1.2 | best.pt shared, API switches to the real model; timeline review screen works. |
| M5 | Feature complete & integrated | Wed 25 Nov 18:00 | 4.3.1, 5.2.2, 5.2.3, 7.1.1, 6.3.1 | All features merged in develop and running with one command. |
| M6 | Release candidate frozen | Wed 25 Nov 20:00 | 7.2.1 | v1.0.0 tagged; only report/slide work after this point. |
| M7 | Final submission | Wed 25 Nov 23:59 | 8.1.4, 8.2.1, 8.2.2 | Report PDF, slides, demo video and repository link submitted. |

## Work Breakdown Structure

### Phase 1 · Planning & Requirements

**1.1 Problem definition**

| WBS | Task | Owner | When | h | Priority | Depends on | Status |
|---|---|---|---|---|---|---|---|
| 1.1.1 | Problem statement, use cases & business model page | Member D | Mon 23 Nov Evening | 6 | High | — | Completed |

**1.2 Project infrastructure & contracts**

| WBS | Task | Owner | When | h | Priority | Depends on | Status |
|---|---|---|---|---|---|---|---|
| 1.2.1 | Repository scaffold, branch protection & CI skeleton | Member D | Mon 23 Nov Evening | 1 | High | — | Not Started |
| 1.2.2 ⚠ | Interface contracts & shared test fixtures | Member D | Mon 23 Nov Evening | 2 | High | 1.2.1 | Not Started |

**1.3 Data governance**

| WBS | Task | Owner | When | h | Priority | Depends on | Status |
|---|---|---|---|---|---|---|---|
| 1.3.1 | Dataset licensing & ethics checklist | Member A | Mon 23 Nov Evening | 1 | High | — | Not Started |

### Phase 2 · Data Collection & Preparation

**2.1 Data acquisition**

| WBS | Task | Owner | When | h | Priority | Depends on | Status |
|---|---|---|---|---|---|---|---|
| 2.1.1 | Download & verify datasets | Member A | Mon 23 Nov Evening | 2 | High | 1.3.1, 1.2.1 | Not Started |

**2.2 Detection dataset**

| WBS | Task | Owner | When | h | Priority | Depends on | Status |
|---|---|---|---|---|---|---|---|
| 2.2.1 | VOC → YOLO conversion & class mapping | Member A | Mon 23 Nov Evening → Tue 24 Nov Morning | 3 | High | 2.1.1, 1.2.2 | Not Started |
| 2.2.2 ⚠ | Video-level train/val/test split | Member A | Tue 24 Nov Morning | 1 | High | 2.2.1 | Not Started |

**2.3 Timeline ground truth**

| WBS | Task | Owner | When | h | Priority | Depends on | Status |
|---|---|---|---|---|---|---|---|
| 2.3.1 | Timeline ground truth from Cholec80 presence labels | Member A | Tue 24 Nov Morning → Tue 24 Nov Afternoon | 3 | High | 2.1.1 | Not Started |

**2.4 Exploratory data analysis**

| WBS | Task | Owner | When | h | Priority | Depends on | Status |
|---|---|---|---|---|---|---|---|
| 2.4.1 | EDA & class-balance report | Member A | Tue 24 Nov Afternoon | 2 | Medium | 2.2.2 | Not Started |

### Phase 3 · Model Development

**3.1 Detector training**

| WBS | Task | Owner | When | h | Priority | Depends on | Status |
|---|---|---|---|---|---|---|---|
| 3.1.1 | Baseline YOLO training | Member B | Tue 24 Nov Morning → Tue 24 Nov Afternoon | 4 | High | 2.2.2 | Not Started |
| 3.1.2 | Augmentation & hyper-parameter experiments | Member B | Tue 24 Nov Evening | 4 | High | 3.1.1, 2.4.1 | Not Started |

**3.2 Detector evaluation**

| WBS | Task | Owner | When | h | Priority | Depends on | Status |
|---|---|---|---|---|---|---|---|
| 3.2.1 | Held-out test evaluation report | Member B | Wed 25 Nov Morning | 3 | High | 3.1.2 | Not Started |

**3.3 Video inference & release**

| WBS | Task | Owner | When | h | Priority | Depends on | Status |
|---|---|---|---|---|---|---|---|
| 3.3.1 ⚠ | Video inference module (detections.jsonl) | Member B | Mon 23 Nov Evening → Tue 24 Nov Afternoon | 5 | High | 1.2.2 | Not Started |
| 3.3.2 | Model card & weights release | Member B | Wed 25 Nov Morning | 1 | Medium | 3.2.1 | Not Started |

### Phase 4 · Timeline Engine & Backend

**4.1 Timeline engine**

| WBS | Task | Owner | When | h | Priority | Depends on | Status |
|---|---|---|---|---|---|---|---|
| 4.1.1 | Temporal smoothing | Member C | Mon 23 Nov Evening | 3 | High | 1.2.2 | Not Started |
| 4.1.2 | Interval builder & per-case statistics | Member C | Tue 24 Nov Morning | 3 | High | 4.1.1 | Not Started |
| 4.1.3 | Timeline evaluation vs ground truth | Member C | Wed 25 Nov Morning → Wed 25 Nov Afternoon | 3 | High | 4.1.2, 2.3.1, 3.3.1 | Not Started |

**4.2 Backend API**

| WBS | Task | Owner | When | h | Priority | Depends on | Status |
|---|---|---|---|---|---|---|---|
| 4.2.1 ⚠ | FastAPI service & background processing jobs | Member C | Mon 23 Nov Evening → Tue 24 Nov Afternoon | 5 | High | 1.2.2 | Not Started |
| 4.2.2 | Notes, search & analytics endpoints | Member C | Tue 24 Nov Evening | 3 | Medium | 4.2.1 | Not Started |

**4.3 Reporting**

| WBS | Task | Owner | When | h | Priority | Depends on | Status |
|---|---|---|---|---|---|---|---|
| 4.3.1 | PDF report generator (English & Arabic) | Member C | Tue 24 Nov Evening → Wed 25 Nov Morning | 4 | Medium | 4.1.2, 4.2.2 | Not Started |

### Phase 5 · Web Application

**5.1 Review workspace**

| WBS | Task | Owner | When | h | Priority | Depends on | Status |
|---|---|---|---|---|---|---|---|
| 5.1.1 | Web app shell, API client & upload flow | Member D | Tue 24 Nov Morning | 3 | High | 1.2.2 | Not Started |
| 5.1.2 ⚠ | Video player + interactive instrument timeline | Member D | Tue 24 Nov Morning → Tue 24 Nov Evening | 5 | High | 5.1.1 | Not Started |
| 5.1.3 | Timestamped notes panel & report download | Member D | Tue 24 Nov Evening | 2 | Medium | 5.1.2 | Not Started |

**5.2 Library, analytics & localisation**

| WBS | Task | Owner | When | h | Priority | Depends on | Status |
|---|---|---|---|---|---|---|---|
| 5.2.1 | Library search page | Member D | Wed 25 Nov Morning | 2 | Medium | 5.1.1 | Not Started |
| 5.2.2 | Analytics dashboard page | Member A | Tue 24 Nov Evening → Wed 25 Nov Morning | 4 | Medium | 5.1.1 | Not Started |
| 5.2.3 | Arabic localisation & RTL styling | Member A | Wed 25 Nov Morning | 2 | Medium | 5.1.1 | Not Started |

### Phase 6 · Testing & Validation

**6.1 Performance validation**

| WBS | Task | Owner | When | h | Priority | Depends on | Status |
|---|---|---|---|---|---|---|---|
| 6.1.1 | Inference performance benchmark | Member B | Wed 25 Nov Afternoon | 1 | Low | 3.3.2, 4.1.3 | Not Started |

**6.2 Usability validation**

| WBS | Task | Owner | When | h | Priority | Depends on | Status |
|---|---|---|---|---|---|---|---|
| 6.2.1 | Usability study: scrubbing vs timeline | Member A | Wed 25 Nov Afternoon → Wed 25 Nov Evening | 3 | High | 7.1.1 | Not Started |

**6.3 End-to-end validation**

| WBS | Task | Owner | When | h | Priority | Depends on | Status |
|---|---|---|---|---|---|---|---|
| 6.3.1 | End-to-end smoke tests (5 use cases) | Member D | Wed 25 Nov Afternoon | 2 | High | 7.1.1 | Not Started |

### Phase 7 · Integration

**7.1 Deployment**

| WBS | Task | Owner | When | h | Priority | Depends on | Status |
|---|---|---|---|---|---|---|---|
| 7.1.1 ⚠ | One-command local run & integration | Member D | Wed 25 Nov Morning → Wed 25 Nov Afternoon | 3 | High | 4.2.2, 4.3.1, 3.3.2, 5.1.3, 5.2.1, 5.2.2, 5.2.3 | Not Started |
| 7.1.2 | Deployment files: Dockerfiles & docker-compose *(added at setup)* | Member D | Wed 25 Nov Afternoon | 1 | High | 7.1.1 | Not Started |

**7.2 Release**

| WBS | Task | Owner | When | h | Priority | Depends on | Status |
|---|---|---|---|---|---|---|---|
| 7.2.1 ⚠ | Release candidate v1.0.0 & demo freeze | Member D | Wed 25 Nov Evening | 1 | High | 6.3.1, 4.1.3, 3.2.1, 7.1.2 | Not Started |

### Phase 8 · Documentation & Final Delivery

**8.1 Final report**

| WBS | Task | Owner | When | h | Priority | Depends on | Status |
|---|---|---|---|---|---|---|---|
| 8.1.1 | Report section: Data | Member A | Wed 25 Nov Evening | 2 | Medium | 2.4.1, 6.2.1 | Not Started |
| 8.1.2 | Report section: Model | Member B | Wed 25 Nov Afternoon | 2 | Medium | 3.2.1, 6.1.1 | Not Started |
| 8.1.3 | Report section: Timeline & System | Member C | Wed 25 Nov Afternoon | 2 | Medium | 4.1.3, 4.3.1 | Not Started |
| 8.1.4 | Final report assembly & README | Member D | Wed 25 Nov Evening | 3 | High | 8.1.1, 8.1.2, 8.1.3, 6.1.1 | Not Started |

**8.2 Presentation**

| WBS | Task | Owner | When | h | Priority | Depends on | Status |
|---|---|---|---|---|---|---|---|
| 8.2.1 | Presentation slide deck | Member B | Wed 25 Nov Afternoon → Wed 25 Nov Evening | 4 | High | 2.4.1, 3.2.1, 4.1.3 | Not Started |
| 8.2.2 | Demo video | Member C | Wed 25 Nov Evening | 2 | Medium | 7.2.1 | Not Started |

⚠ = critical integration point: **1.2.2** Interface contracts & shared test fixtures · **2.2.2** Video-level train/val/test split · **3.3.1** Video inference module (detections.jsonl) · **4.2.1** FastAPI service & background processing jobs · **5.1.2** Video player + interactive instrument timeline · **7.1.1** One-command local run & integration · **7.2.1** Release candidate v1.0.0 & demo freeze

## Dependencies (cross-member hand-offs)

| Task | Owner | Needs | From |
|---|---|---|---|
| 2.1.1 Download & verify datasets | Member A | 1.2.1 Repository scaffold, branch protection & CI skeleton | Member D |
| 2.2.1 VOC → YOLO conversion & class mapping | Member A | 1.2.2 Interface contracts & shared test fixtures | Member D |
| 3.1.1 Baseline YOLO training | Member B | 2.2.2 Video-level train/val/test split | Member A |
| 3.1.2 Augmentation & hyper-parameter experiments | Member B | 2.4.1 EDA & class-balance report | Member A |
| 3.3.1 Video inference module (detections.jsonl) | Member B | 1.2.2 Interface contracts & shared test fixtures | Member D |
| 4.1.1 Temporal smoothing | Member C | 1.2.2 Interface contracts & shared test fixtures | Member D |
| 4.1.3 Timeline evaluation vs ground truth | Member C | 2.3.1 Timeline ground truth from Cholec80 presence labels | Member A |
| 4.1.3 Timeline evaluation vs ground truth | Member C | 3.3.1 Video inference module (detections.jsonl) | Member B |
| 4.2.1 FastAPI service & background processing jobs | Member C | 1.2.2 Interface contracts & shared test fixtures | Member D |
| 5.2.2 Analytics dashboard page | Member A | 5.1.1 Web app shell, API client & upload flow | Member D |
| 5.2.3 Arabic localisation & RTL styling | Member A | 5.1.1 Web app shell, API client & upload flow | Member D |
| 6.1.1 Inference performance benchmark | Member B | 4.1.3 Timeline evaluation vs ground truth | Member C |
| 6.2.1 Usability study: scrubbing vs timeline | Member A | 7.1.1 One-command local run & integration | Member D |
| 7.1.1 One-command local run & integration | Member D | 4.2.2 Notes, search & analytics endpoints | Member C |
| 7.1.1 One-command local run & integration | Member D | 4.3.1 PDF report generator (English & Arabic) | Member C |
| 7.1.1 One-command local run & integration | Member D | 3.3.2 Model card & weights release | Member B |
| 7.1.1 One-command local run & integration | Member D | 5.2.2 Analytics dashboard page | Member A |
| 7.1.1 One-command local run & integration | Member D | 5.2.3 Arabic localisation & RTL styling | Member A |
| 7.2.1 Release candidate v1.0.0 & demo freeze | Member D | 4.1.3 Timeline evaluation vs ground truth | Member C |
| 7.2.1 Release candidate v1.0.0 & demo freeze | Member D | 3.2.1 Held-out test evaluation report | Member B |
| 8.1.4 Final report assembly & README | Member D | 8.1.1 Report section: Data | Member A |
| 8.1.4 Final report assembly & README | Member D | 8.1.2 Report section: Model | Member B |
| 8.1.4 Final report assembly & README | Member D | 8.1.3 Report section: Timeline & System | Member C |
| 8.1.4 Final report assembly & README | Member D | 6.1.1 Inference performance benchmark | Member B |
| 8.2.1 Presentation slide deck | Member B | 2.4.1 EDA & class-balance report | Member A |
| 8.2.1 Presentation slide deck | Member B | 4.1.3 Timeline evaluation vs ground truth | Member C |
| 8.2.2 Demo video | Member C | 7.2.1 Release candidate v1.0.0 & demo freeze | Member D |

## Workload

| Member | Role | Tasks | Hours |
|---|---|---|---|
| Member A | Data Engineer & UX Research | 10 | 23 |
| Member B | ML Engineer | 8 | 24 |
| Member C | Backend & Timeline Engineer | 8 | 25 |
| Member D | Frontend Lead & Integration Owner | 12 | 31 |

Member D's total includes the 6 h already spent on 1.1.1 and the 1 h for task 7.1.2 added at setup.

## Conflicts resolved while planning

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
| The course brief requires Deployment Files, but Docker was only an optional stretch inside 7.1.1. | New task 7.1.2 (Member D, 1 h, Wed afternoon) owns docker/ and docker-compose.yml; 7.2.1 now depends on it. |
| The team works in Google Colab; command-line training scripts were too complex. | Data tasks run in notebooks/01_Data.ipynb (A) and model tasks in notebooks/02_Model.ipynb (B). A hands the dataset to B as yolo_dataset.zip in Drive. src/inference/detect_video.py stays because the API imports it. |
| Branch naming requested at repository setup differs from the plan. | Branches are feature/member-<a|b|c|d>-<wbs-id>-<slug>; each task's original name is kept as planBranch. |

Risks, assumptions and cut list: see `docs/planning/WBS_VALIDATION.md`.
