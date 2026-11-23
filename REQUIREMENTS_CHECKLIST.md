# Requirements Checklist

> Every requirement mapped to the task(s) that deliver it and to the expected deliverable.  
> **P** = course brief (`docs/planning/Unit7_Project_brief.pdf`, authoritative). **R** = project page / success measures (WBS).  
> Generated from `docs/planning/wbs_data.json`. Tick a box only when the deliverable is merged into `develop`.

## Course brief (mandatory)

| Done | ID | Requirement | Tasks | Owners | Deliverable |
|---|---|---|---|---|---|
| ☐ | P1 | Select a real-world problem that Computer Vision (image/video understanding) can solve | 1.1.1 | Member D | docs/problem/ |
| ☐ | P2 | Design the CV solution as an end-to-end pipeline: problem → data → model → evaluation → deployment → demo | 1.1.1, 1.2.2 | Member D | docs/problem/, contracts/ |
| ☐ | P3 | Data stage of the pipeline | 1.3.1, 2.1.1, 2.2.1, 2.2.2, 2.3.1, 2.4.1 | Member A | D1 |
| ☐ | P4 | Train or fine-tune a CV model | 3.1.1, 3.1.2 | Member B | D2 |
| ☐ | P5 | Evaluate the solution | 3.2.1, 4.1.3, 6.1.1, 6.2.1, 6.3.1 | Member B, Member C, Member A, Member D | D2, D4, D7 |
| ☐ | P6 | Deploy the CV solution | 7.1.1, 7.1.2 | Member D, Member C | D8 |
| ☐ | P7 | Present a working live demo | 7.2.1, 8.2.2 | Member D, Member C | D8, D9 |
| ☐ | P8 | Deliverable: Presentation | 8.2.1 | Member B | D9 |
| ☐ | P9 | Deliverable: Code Repository (GitHub) | 1.2.1, 7.2.1, 8.1.4 | Member D | this repository, tag v1.0.0 |
| ☐ | P10 | Deliverable: Deployment Files | 7.1.1, 7.1.2 | Member D, Member C | scripts/, docker/, docker-compose.yml |
| ☐ | P11 | Deliverable: Demo | 7.2.1, 8.2.2 | Member D, Member C | D9 demo video + live demo |

## Project requirements & success measures

| Done | ID | Requirement | Source | Tasks | Owners | Deliverable |
|---|---|---|---|---|---|---|
| ☐ | R1 | Detect 6 instruments per frame (grasper, bipolar, hook, scissors, clipper, irrigator) | Project objective | 2.2.1, 3.1.1, 3.1.2 | Member A, Member B | D1, D2 |
| ☐ | R2 | Model metrics: mAP@0.5 and per-instrument precision/recall on a video-level held-out test set | Success measures | 2.2.2, 3.2.1 | Member A, Member B | D1, D2 |
| ☐ | R3 | Temporal smoothing to remove flicker | Proposed solution | 4.1.1 | Member C | D4 |
| ☐ | R4 | Colour-coded instrument timeline (e.g. hook 03:10–09:45) | Proposed solution | 4.1.2, 5.1.2 | Member C, Member D | D4, D6 |
| ☐ | R5 | Timeline agreement with ground-truth presence labels | Success measures | 2.3.1, 4.1.3 | Member A, Member C | D4 |
| ☐ | R6 | Upload a recorded video and process it | Proposed solution | 3.3.1, 4.2.1, 5.1.1 | Member B, Member C, Member D | D3, D5, D6 |
| ☐ | R7 | Click a timeline bar to jump the video to that moment | Use case 1, 4 | 5.1.2 | Member D | D6 |
| ☐ | R8 | Timestamped instructor notes | Use case 2 | 4.2.2, 5.1.3 | Member C, Member D | D5, D6 |
| ☐ | R9 | PDF report export including instructor notes | Use case 2 | 4.3.1 | Member C | D5 |
| ☐ | R10 | Searchable library indexed by instrument ("show all clipping segments") | Use case 3 | 4.2.2, 5.2.1 | Member C, Member D | D5, D6 |
| ☐ | R11 | Find unusual tool patterns / clips quickly (long irrigation, repeated switches) | Use case 4 | 4.1.2, 5.1.2 | Member C, Member D | D4, D6 |
| ☐ | R12 | Per-case statistics: time per instrument, total time, tool switches; compare across cases | Use case 5 | 4.1.2, 4.2.2, 5.2.2 | Member C, Member A | D4, D5, D6 |
| ☐ | R13 | Arabic-language interface and reports | Gap in existing tools / business model | 4.3.1, 5.2.3 | Member C, Member A | D5, D6 |
| ☐ | R14 | Usability test: time to find a moment, scrubbing vs timeline | Success measures | 6.2.1 | Member A | D7 |
| ☐ | R15 | Public research data only; non-commercial licence; educational, not diagnostic | Scope & limits | 1.3.1, 3.3.2, 8.1.4 | Member A, Member B, Member D | D1, D2, D9 |
| ☐ | R16 | Problem definition, use cases and business model documented | Project page | 1.1.1 | Member D | docs/problem/ |
| ☐ | R17 | Final project report and presentation | Final project delivery | 8.1.4, 8.2.1, 8.2.2 | Member D, Member B, Member C | D9 |

## Deliverables

| ID | Deliverable | Produced by |
|---|---|---|
| D1 | Labelled YOLO dataset + video-level split + EDA report | 2.2.1 (A), 2.2.2 (A), 2.4.1 (A) |
| D2 | Trained YOLO weights + evaluation report (mAP@0.5, per-class P/R) + model card | 3.1.2 (B), 3.2.1 (B), 3.3.2 (B) |
| D3 | Video inference module (detections.jsonl contract) | 3.3.1 (B) |
| D4 | Timeline engine (smoothing, intervals, statistics) + timeline evaluation | 4.1.1 (C), 4.1.2 (C), 4.1.3 (C) |
| D5 | Backend API + PDF report generator (EN/AR) | 4.2.1 (C), 4.2.2 (C), 4.3.1 (C) |
| D6 | Web app: review workspace, notes, library search, analytics, Arabic/RTL | 5.1.1 (D), 5.1.2 (D), 5.1.3 (D), 5.2.1 (D), 5.2.2 (A), 5.2.3 (A) |
| D7 | Usability study results (manual scrubbing vs timeline) | 6.2.1 (A) |
| D8 | Integrated release candidate (v1.0.0) + deployment files | 7.1.1 (D), 7.1.2 (C), 7.2.1 (D) |
| D9 | Final report, README, slide deck, demo video | 8.1.4 (D), 8.2.1 (B), 8.2.2 (C) |

## Submission (Wed 25 Nov 23:59, milestone M7)

- [ ] Presentation: `docs/slides/` (8.2.1, Member B)
- [ ] Code repository: GitHub link, tag `v1.0.0` on `main` (7.2.1, Member D)
- [ ] Deployment files: `scripts/run_local.*`, `docker/`, `docker-compose.yml` (7.1.1 Member D, 7.1.2 Member C)
- [ ] Demo: live demo from the tagged build + backup video linked in `docs/demo/README.md` (7.2.1 D, 8.2.2 C)
- [ ] Final report PDF built from `docs/report/` (8.1.4, Member D)

## Coverage check

- Requirements: 28, uncovered: none.
- Tasks: 38, all with exactly one owner.
