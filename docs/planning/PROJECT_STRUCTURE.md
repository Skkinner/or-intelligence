# Project Structure & Collaboration

> **OR Intelligence** · Computer Vision Final Project · Deadline **Wednesday 25 Nov 2026, 23:59**  
> Generated from the same data as `project_wbs_dashboard.html`. Member names are placeholders (A–D); rename them in the dashboard.

## Repository tree (owner per path)

```text
or-intelligence/
├── .github/                  D  CODEOWNERS, ci.yml, PR template
├── contracts/                D  classes.json, *.schema.json, openapi.yaml, CHANGELOG.md
├── configs/
│   ├── data.yaml             A
│   ├── train.yaml            B
│   ├── experiments/          B
│   └── timeline.yaml         C
├── requirements/
│   ├── base.txt              D
│   ├── data.txt              A
│   ├── ml.txt                B
│   └── api.txt               C
├── data/            (gitignored)  A  raw/, processed/yolo/, processed/presence/
│   └── splits/splits.json    A  (tracked)
├── models/weights/  (gitignored)  B  baseline.pt, best.pt → GitHub Release
├── src/
│   ├── data/                 A  download, verify, convert_voc_to_yolo, split,
│   │                            presence_labels, extract_frames, eda, visualize
│   ├── models/               B  train, tune, evaluate, benchmark
│   ├── inference/            B  detect_video, fetch_weights
│   ├── timeline/             C  smoothing, builder, evaluate
│   ├── api/                  C  main, db, jobs, routes/{videos,notes,search,analytics,reports}
│   └── reports/              C  pdf_report, strings, fonts/
├── web/                      D  package.json, vite.config.ts
│   └── src/
│       ├── app/ api/         D
│       ├── components/       D  Timeline/, VideoPlayer/, NotesPanel/
│       ├── pages/            D  Upload/, Review/, Library/
│       │   └── Analytics/    A
│       ├── i18n/             D  index.ts, en.json   ·  A  ar.json, parity.test.ts
│       └── styles/rtl.css    A
├── tests/
│   ├── fixtures/ contracts/  D
│   ├── unit/data/            A
│   ├── unit/models/ inference/  B
│   ├── unit/timeline/ api/ reports/  C
│   └── e2e/                  D
├── notebooks/  eda.ipynb A · experiments/ B
├── scripts/                  D  run_local.ps1, run_local.sh
├── docs/
│   ├── problem/              D  (1.1.1, done)
│   ├── data/ usability/      A
│   ├── model/ slides/        B
│   ├── timeline/ demo/       C
│   ├── integration/          D
│   └── report/  00_intro D · 01_data A · 02_model B · 03_system C · 04 + main D
├── README.md  CHANGELOG.md   D
└── docker/ docker-compose.yml  D  (optional stretch)
```

## Module ownership

| Path | Owner | WBS tasks | Others |
|---|---|---|---|
| `.github/` | Member D | 1.2.1 | read-only, PR to owner |
| `.gitignore` | Member D | 1.2.1 | read-only, PR to owner |
| `CHANGELOG.md` | Member D | 7.2.1 | read-only, PR to owner |
| `README.md` | Member D | 8.1.4 | read-only, PR to owner |
| `configs/data.yaml` | Member A | 2.1.1 | read-only, PR to owner |
| `configs/experiments/` | Member B | 3.1.2 | read-only, PR to owner |
| `configs/timeline.yaml` | Member C | 4.1.1 | read-only, PR to owner |
| `configs/train.yaml` | Member B | 3.1.1 | read-only, PR to owner |
| `contracts/` | Member D | 1.2.2 | read-only, PR to owner |
| `data/splits/splits.json` | Member A | 2.2.2 | read-only, PR to owner |
| `docker-compose.yml` | Member D | 7.1.1 | read-only, PR to owner |
| `docker/` | Member D | 7.1.1 | read-only, PR to owner |
| `docs/data/` | Member A | 1.3.1 | read-only, PR to owner |
| `docs/data/EDA.md` | Member A | 2.4.1 | read-only, PR to owner |
| `docs/data/figures/` | Member A | 2.4.1 | read-only, PR to owner |
| `docs/data/qa_notes.md` | Member A | 2.2.1 | read-only, PR to owner |
| `docs/data/timeline_eval_set.md` | Member A | 2.3.1 | read-only, PR to owner |
| `docs/demo/` | Member C | 8.2.2 | read-only, PR to owner |
| `docs/integration/` | Member D | 7.1.1 | read-only, PR to owner |
| `docs/model/BENCHMARK.md` | Member B | 6.1.1 | read-only, PR to owner |
| `docs/model/EVALUATION.md` | Member B | 3.2.1 | read-only, PR to owner |
| `docs/model/MODEL_CARD.md` | Member B | 3.3.2 | read-only, PR to owner |
| `docs/model/experiments.md` | Member B | 3.1.1 | read-only, PR to owner |
| `docs/model/figures/` | Member B | 3.2.1 | read-only, PR to owner |
| `docs/model/test_metrics.json` | Member B | 3.2.1 | read-only, PR to owner |
| `docs/problem/` | Member D | 1.1.1 | read-only, PR to owner |
| `docs/report/00_intro.md` | Member D | 8.1.4 | read-only, PR to owner |
| `docs/report/01_data.md` | Member A | 8.1.1 | read-only, PR to owner |
| `docs/report/02_model.md` | Member B | 8.1.2 | read-only, PR to owner |
| `docs/report/03_system.md` | Member C | 8.1.3 | read-only, PR to owner |
| `docs/report/04_frontend_conclusion.md` | Member D | 8.1.4 | read-only, PR to owner |
| `docs/report/build.sh` | Member D | 8.1.4 | read-only, PR to owner |
| `docs/report/main.md` | Member D | 8.1.4 | read-only, PR to owner |
| `docs/slides/` | Member B | 8.2.1 | read-only, PR to owner |
| `docs/timeline/` | Member C | 4.1.3 | read-only, PR to owner |
| `docs/usability/` | Member A | 6.2.1 | read-only, PR to owner |
| `models/weights/` | Member B | 3.1.2 | read-only, PR to owner |
| `notebooks/eda.ipynb` | Member A | 2.4.1 | read-only, PR to owner |
| `notebooks/experiments/` | Member B | 3.1.2 | read-only, PR to owner |
| `pyproject.toml` | Member D | 1.2.1 | read-only, PR to owner |
| `requirements/api.txt` | Member C | 4.1.1 | read-only, PR to owner |
| `requirements/base.txt` | Member D | 1.2.1 | read-only, PR to owner |
| `requirements/data.txt` | Member A | 2.1.1 | read-only, PR to owner |
| `requirements/ml.txt` | Member B | 3.1.1 | read-only, PR to owner |
| `scripts/` | Member D | 7.1.1 | read-only, PR to owner |
| `src/api/db.py` | Member C | 4.2.1 | read-only, PR to owner |
| `src/api/jobs.py` | Member C | 4.2.1 | read-only, PR to owner |
| `src/api/main.py` | Member C | 4.2.1 | read-only, PR to owner |
| `src/api/routes/analytics.py` | Member C | 4.2.2 | read-only, PR to owner |
| `src/api/routes/notes.py` | Member C | 4.2.2 | read-only, PR to owner |
| `src/api/routes/reports.py` | Member C | 4.3.1 | read-only, PR to owner |
| `src/api/routes/search.py` | Member C | 4.2.2 | read-only, PR to owner |
| `src/api/routes/videos.py` | Member C | 4.2.1 | read-only, PR to owner |
| `src/data/convert_voc_to_yolo.py` | Member A | 2.2.1 | read-only, PR to owner |
| `src/data/download.py` | Member A | 2.1.1 | read-only, PR to owner |
| `src/data/eda.py` | Member A | 2.4.1 | read-only, PR to owner |
| `src/data/extract_frames.py` | Member A | 2.3.1 | read-only, PR to owner |
| `src/data/presence_labels.py` | Member A | 2.3.1 | read-only, PR to owner |
| `src/data/split.py` | Member A | 2.2.2 | read-only, PR to owner |
| `src/data/verify.py` | Member A | 2.1.1 | read-only, PR to owner |
| `src/data/visualize.py` | Member A | 2.2.1 | read-only, PR to owner |
| `src/inference/` | Member B | 3.3.1 | read-only, PR to owner |
| `src/models/benchmark.py` | Member B | 6.1.1 | read-only, PR to owner |
| `src/models/evaluate.py` | Member B | 3.2.1 | read-only, PR to owner |
| `src/models/train.py` | Member B | 3.1.1 | read-only, PR to owner |
| `src/models/tune.py` | Member B | 3.1.2 | read-only, PR to owner |
| `src/reports/` | Member C | 4.3.1 | read-only, PR to owner |
| `src/timeline/builder.py` | Member C | 4.1.2 | read-only, PR to owner |
| `src/timeline/evaluate.py` | Member C | 4.1.3 | read-only, PR to owner |
| `src/timeline/smoothing.py` | Member C | 4.1.1 | read-only, PR to owner |
| `tests/contracts/` | Member D | 1.2.2 | read-only, PR to owner |
| `tests/e2e/` | Member D | 6.3.1 | read-only, PR to owner |
| `tests/fixtures/` | Member D | 1.2.2 | read-only, PR to owner |
| `tests/unit/api/` | Member C | 4.2.1 | read-only, PR to owner |
| `tests/unit/data/` | Member A | 2.2.1 | read-only, PR to owner |
| `tests/unit/inference/` | Member B | 3.3.1 | read-only, PR to owner |
| `tests/unit/models/` | Member B | 3.1.1 | read-only, PR to owner |
| `tests/unit/reports/` | Member C | 4.3.1 | read-only, PR to owner |
| `tests/unit/timeline/` | Member C | 4.1.1 | read-only, PR to owner |
| `web/package.json` | Member D | 5.1.1 | read-only, PR to owner |
| `web/src/api/` | Member D | 5.1.1 | read-only, PR to owner |
| `web/src/app/` | Member D | 5.1.1 | read-only, PR to owner |
| `web/src/components/NotesPanel/` | Member D | 5.1.3 | read-only, PR to owner |
| `web/src/components/Timeline/` | Member D | 5.1.2 | read-only, PR to owner |
| `web/src/components/VideoPlayer/` | Member D | 5.1.2 | read-only, PR to owner |
| `web/src/i18n/ar.json` | Member A | 5.2.3 | read-only, PR to owner |
| `web/src/i18n/en.json` | Member D | 5.1.1 | read-only, PR to owner |
| `web/src/i18n/index.ts` | Member D | 5.1.1 | read-only, PR to owner |
| `web/src/i18n/parity.test.ts` | Member A | 5.2.3 | read-only, PR to owner |
| `web/src/pages/Analytics/` | Member A | 5.2.2 | read-only, PR to owner |
| `web/src/pages/Library/` | Member D | 5.2.1 | read-only, PR to owner |
| `web/src/pages/Review/` | Member D | 5.1.2 | read-only, PR to owner |
| `web/src/pages/Upload/` | Member D | 5.1.1 | read-only, PR to owner |
| `web/src/styles/rtl.css` | Member A | 5.2.3 | read-only, PR to owner |
| `web/vite.config.ts` | Member D | 5.1.1 | read-only, PR to owner |

## Shared-file rules

| Path | Owner | Rule |
|---|---|---|
| `contracts/` | Member D | Change only by PR approved by D + every affected consumer; record in contracts/CHANGELOG.md. |
| `web/package.json` | Member D | Member A requests new dependencies by a PR that touches only package.json + lockfile; D approves. |
| `requirements/base.txt` | Member D | Each owner adds packages only to their own requirements/{data,ml,api}.txt. |
| `.github/` | Member D | CI and CODEOWNERS changes by D only. |
| `scripts/, docker/, docker-compose.yml` | Member D | C requests API runtime/start-up changes by issue; D implements. |
| `src/inference/` | Member B | C imports detect_video(); signature changes require a contract PR first. |

**Scaffold exception:** task 1.2.1 (Member D) creates empty stubs in every folder in one commit. After that commit, each path belongs only to its owner.

## Git branch strategy

- **main**: protected, release only. D merges `develop → main` at the release candidate (Wed 20:00) and tags `v1.0.0`.
- **develop**: protected integration branch. PRs only, 1 approval + green CI. D merges at merge windows: **Mon 23:00, Tue 13:00, Tue 21:00, Wed 12:00, Wed 18:00**.
- **Feature branches**: one per WBS task, `<member>/<wbs-id>-<slug>`, e.g. `c/4.1.1-smoothing`. Branch from the latest develop and rebase before opening the PR.
- **PR rules**: title `[WBS 4.1.1] Temporal smoothing`; touches only the owner's paths (CODEOWNERS auto-requests the right reviewer); includes tests and acceptance evidence; under ~400 changed lines where possible.
- **Contracts**: any change to `contracts/` is its own PR, approved by D and every consumer, and logged in `contracts/CHANGELOG.md`.
- **Conflicts**: the integration owner (D) resolves merge conflicts on develop. Nobody edits another member's files to make their own PR pass; open an issue for the owner instead.
- **Never commit** data/, frames, videos or *.pt weights. Share them via GitHub Release or the team drive.

### Branches per member

| Member | Branch prefix | Task branches |
|---|---|---|
| Member A | `a/` | `a/1.3.1-licensing`, `a/2.1.1-download`, `a/2.2.1-voc-to-yolo`, `a/2.2.2-split`, `a/2.3.1-presence-gt`, `a/2.4.1-eda`, `a/5.2.2-analytics`, `a/5.2.3-arabic`, `a/6.2.1-usability`, `a/8.1.1-report-data` |
| Member B | `b/` | `b/3.1.1-baseline`, `b/3.1.2-tuning`, `b/3.2.1-eval`, `b/3.3.1-inference`, `b/3.3.2-model-card`, `b/6.1.1-benchmark`, `b/8.1.2-report-model`, `b/8.2.1-slides` |
| Member C | `c/` | `c/4.1.1-smoothing`, `c/4.1.2-builder`, `c/4.1.3-timeline-eval`, `c/4.2.1-api`, `c/4.2.2-notes-search`, `c/4.3.1-pdf`, `c/8.1.3-report-system`, `c/8.2.2-demo` |
| Member D | `d/` | `d/1.1.1-problem-page`, `d/1.2.1-scaffold`, `d/1.2.2-contracts`, `d/5.1.1-shell`, `d/5.1.2-timeline-ui`, `d/5.1.3-notes-ui`, `d/5.2.1-library`, `d/6.3.1-e2e`, `d/7.1.1-compose`, `d/7.2.1-release`, `d/8.1.4-report` |

## Interface contracts (frozen Mon 23 Nov 23:00, task 1.2.2)

### C1 · Class map

File: `contracts/classes.json` · Producer: D (1.2.2) · Consumers: A, B, C, D

```text
{"0":"grasper","1":"bipolar","2":"hook","3":"scissors","4":"clipper","5":"irrigator"}
// m2cai16 "SpecimenBag" is dropped. Colours for the UI timeline live here too:
// {"colors":{"grasper":"#2563eb","bipolar":"#7c3aed","hook":"#dc2626","scissors":"#16a34a","clipper":"#ea580c","irrigator":"#0891b2"}}
```

### C2 · YOLO dataset layout

File: `data/processed/yolo/ + data/processed/dataset.yaml` · Producer: A (2.2.1, 2.2.2) · Consumers: B

```text
data/processed/yolo/images/{train,val,test}/<video>_<frame>.jpg
data/processed/yolo/labels/{train,val,test}/<video>_<frame>.txt   # "cls cx cy w h" normalised 0-1
data/processed/dataset.yaml   # path, train, val, test, names (from contracts/classes.json)
data/splits/splits.json        # {"train":["v01",...],"val":[...],"test":[...]}  — video IDs, no frame leakage
```

### C3 · Timeline ground truth

File: `data/processed/presence/<video_id>.csv` · Producer: A (2.3.1) · Consumers: C (4.1.3)

```text
t_sec,grasper,bipolar,hook,scissors,clipper,irrigator
0,1,0,0,0,0,0
1,1,0,1,0,0,0          # 1 fps, 0/1 per tool, derived from Cholec80 tool annotations
```

### C4 · Detections (per video)

File: `contracts/detections.schema.json` · Producer: B (3.3.1) · Consumers: C (4.1.x, 4.2.1)

```text
# detections.jsonl — one JSON object per sampled frame
{"video_id":"abc123","frame":125,"t":5.0,"w":1920,"h":1080,
 "dets":[{"cls":2,"name":"hook","conf":0.91,"box":[0.41,0.33,0.62,0.71]}]}
# box = [x1,y1,x2,y2] normalised. Python API:
# detect_video(video_path: str, out_path: str, sample_fps: float = 5.0,
#              conf: float = 0.25, weights: str = "models/weights/best.pt") -> dict  # {"frames":int,"seconds":float}
```

### C5 · Timeline (per video)

File: `contracts/timeline.schema.json` · Producer: C (4.1.2) · Consumers: C (4.2, 4.3), D, A (5.2.2)

```text
{"video_id":"abc123","duration_s":2712.0,"sample_fps":5.0,
 "tools":{"hook":[{"start":190.0,"end":585.0,"mean_conf":0.83}], "clipper":[...]},
 "stats":{"total_s":2712.0,"switches":41,
          "per_tool_s":{"hook":1120.4,"clipper":96.0,...},
          "per_tool_segments":{"hook":7,...}},
 "params":{"conf":0.4,"window_s":2.0,"min_segment_s":1.5,"merge_gap_s":2.0}}
```

### C6 · HTTP API

File: `contracts/openapi.yaml` · Producer: D drafts (1.2.2); C implements (4.2.x) · Consumers: D, A (web)

```text
POST /api/videos                  multipart file → {"id","status":"queued"}
GET  /api/videos                  → [{id,title,status,duration_s,created_at}]
GET  /api/videos/{id}             → {id,status:"queued|processing|done|failed",progress:0-1}
GET  /api/videos/{id}/file        → video stream (HTTP range requests)
GET  /api/videos/{id}/timeline    → Timeline (C5)
GET  /api/videos/{id}/notes       POST {t_sec,text,author} · DELETE /notes/{note_id}
GET  /api/videos/{id}/report.pdf?lang=en|ar
GET  /api/search?tool=clipper&min_s=5 → [{video_id,start,end,tool}]
GET  /api/analytics?video_ids=a,b → [{video_id, stats}]
```

## Integration procedure

1. Every member develops against `tests/fixtures/`, so no one waits for upstream code.
2. Open a PR per WBS task into `develop`; CI (ruff, pytest, contract tests, web build) must pass; CODEOWNERS requests the owner's review.
3. Member D merges at the merge windows (Mon 23:00, Tue 13:00, Tue 21:00, Wed 12:00, Wed 18:00) and resolves conflicts.
4. After M4 (best.pt, Tue 23:00), C switches the API from `INFERENCE_MODE=fixture` to real inference.
5. Wed 18:00: feature freeze (M5). D runs the smoke checklist (6.3.1); bugs become issues for the owning member.
6. Wed 20:00: D merges `develop → main` and tags `v1.0.0`. After that only docs/slides change.
7. Wed 23:59: submit report PDF, slides, demo video link and repository link.

## Daily rhythm

- 09:00 Tue and Wed: 10-min stand-up (yesterday / today / blocked).
- Blocked for more than 30 min? Post in the team chat and tag the producer of the input you need.
- Progress: update the dashboard, export JSON, and post it in the team chat at each merge window (localStorage does not sync).
