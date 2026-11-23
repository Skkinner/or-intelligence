# OR Intelligence

**Laparoscopic instrument detection → clickable instrument timeline for surgical education.**
Computer Vision Final Project · Deadline **Wednesday 25 Nov 2026, 23:59**

A reviewer uploads a recorded laparoscopic cholecystectomy. A fine-tuned YOLO detector finds 6 instruments
(grasper, bipolar, hook, scissors, clipper, irrigator) in sampled frames. Temporal smoothing removes flicker,
and the result is a colour-coded instrument timeline: click a bar and the video jumps to that moment.
Sessions export as a PDF report with timestamped instructor notes, in English or Arabic.

> Educational review tool, **not** a diagnostic or clinical decision-making system. Public research data only
> (non-commercial licences). No dataset, video or model weights are stored in this repository.

## Status

This repository is the **team starting point**. The structure, contracts, synthetic fixtures, CI and starter
files with `TODO(<member>, <WBS id>)` markers are in place. **No WBS task is implemented yet** (the plan marks
1.1.1 as done outside the repo). Progress is tracked in the GitHub Issues, one per WBS task.

## Objectives and success measures

1. **Detection:** mAP@0.5 and per-instrument precision/recall on a video-level held-out test split.
2. **Timeline:** agreement between predicted tool intervals and ground-truth presence labels.
3. **Usability:** time to find a moment with the timeline vs manual scrubbing (pilot study).

## Pipeline

```text
video ──► src/inference (B) ──► detections.jsonl (C4) ──► src/timeline (C) ──► timeline.json (C5)
                                                                   │
            web/ (D, A) ◄── HTTP API, contracts/openapi.yaml (C6) ◄─┘  src/api (C) ──► PDF (src/reports, C)
data: src/data (A) ──► YOLO dataset (C2) ──► src/models (B) ──► best.pt
```

## Team and responsibilities

| Member | Role | Owns | Tasks |
|---|---|---|---|
| Member A | Data Engineer & UX Research | `notebooks/01_Data.ipynb`, `src/data/` (presence labels), `docs/data/`, `docs/usability/`, Analytics page, `ar.json`, `rtl.css` | 10 |
| Member B | ML Engineer | `notebooks/02_Model.ipynb`, `src/inference/`, `src/models/benchmark.py`, `docs/model/`, `docs/slides/` | 8 |
| Member C | Backend & Timeline Engineer | `src/timeline/`, `src/api/`, `src/reports/`, `configs/timeline.yaml`, `docs/timeline/`, `docs/demo/` | 8 |
| Member D | Frontend Lead & Integration Owner | `contracts/`, `tests/fixtures/`, `web/` (except A's files), `scripts/`, `docker/`, `.github/`, root docs | 12 |

Names are placeholders until the team fills in `.github/team.json`. Full list per member: **[TEAM_TASKS.md](TEAM_TASKS.md)**.

## Documentation

| Document | What it is for |
|---|---|
| [TEAM_TASKS.md](TEAM_TASKS.md) | Every member's tasks, files, deliverables and completion checklists |
| [PROJECT_PLAN.md](PROJECT_PLAN.md) | The WBS with original task IDs, schedule, milestones and dependencies |
| [CONTRIBUTING.md](CONTRIBUTING.md) | Exact git commands: clone, branch, commit, push, PR |
| [INTEGRATION_GUIDE.md](INTEGRATION_GUIDE.md) | How the components connect and how to integrate them |
| [REQUIREMENTS_CHECKLIST.md](REQUIREMENTS_CHECKLIST.md) | Course and project requirements → tasks → deliverables |
| [contracts/](contracts/README.md) | The shared interfaces C1–C6 |
| [docs/planning/](docs/planning/) | Original plan: dashboard HTML, WBS data, validation, course brief |

## Data and model (Google Colab, no setup needed)

Two notebooks, one per owner. Run them in order; they pass files through the shared Google Drive folder
`MyDrive/or-intelligence/`.

| Notebook | Owner | WBS | Open | Produces (in Drive) |
|---|---|---|---|---|
| [`notebooks/01_Data.ipynb`](notebooks/01_Data.ipynb) | Member A | 2.1.1, 2.2.1, 2.2.2, 2.4.1 | [![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Skkinner/or-intelligence/blob/main/notebooks/01_Data.ipynb) | `data/yolo_dataset.zip`, `data/splits.json`, `results/eda/` |
| [`notebooks/02_Model.ipynb`](notebooks/02_Model.ipynb) | Member B | 3.1.1, 3.1.2, 3.2.1, 3.3.1, 3.3.2 | [![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Skkinner/or-intelligence/blob/main/notebooks/02_Model.ipynb) | `weights/best.pt`, `results/test_metrics.json`, `*_detections.jsonl` |

1. Upload the dataset zip once: `MyDrive/or-intelligence/data/m2cai16-tool-locations.zip`, and share the folder with the team.
2. Member A: open `01_Data` in Colab → *Runtime → Run all*.
3. Member B: open `02_Model` in Colab → *Runtime → Change runtime type → T4 GPU* → *Run all*.

To open a notebook from this private repo in Colab: *File → Open notebook → GitHub*, tick *Include private repos*.
Weights and data stay in Drive; they are never committed to GitHub. The app uses the same inference code from
`src/inference/detect_video.py` with `best.pt` copied to `models/weights/`.

## Installation (only for the app: API and web)

Requirements: Python 3.11+, Node 20+, Git. Training happens in Colab, not here.

```bash
git clone https://github.com/<owner>/or-intelligence.git
cd or-intelligence
python -m venv .venv
# Windows: .venv\Scripts\activate    macOS/Linux: source .venv/bin/activate
pip install -r requirements/<your-area>.txt     # data.txt (A) · ml.txt (B) · api.txt (C) · base.txt (D)
cd web && npm ci && cd ..                       # web work (A, D)
```

## Running

```bash
pytest -m "not gpu and not data"        # unit + contract tests (what CI runs)
ruff check .
cd web && npm run dev                    # web app on http://localhost:5173 (mock data from tests/fixtures)
uvicorn src.api.main:app --reload        # API on http://localhost:8000/docs
```

Full stack (after integration, WBS 7.1.1 / 7.1.2):

```bash
./scripts/run_local.sh                  # Windows: powershell -ExecutionPolicy Bypass -File scripts\run_local.ps1
docker compose up --build               # alternative; app on http://localhost:8080
```

`INFERENCE_MODE=fixture` (default) replays synthetic detections. Set `INFERENCE_MODE=real` once
`models/weights/best.pt` exists (`python -m src.inference.fetch_weights`).

## Repository structure

```text
or-intelligence/
├── .github/            D   CI, CODEOWNERS, PR/issue templates, team.json, issues/manifest.json
├── contracts/          D   C1 classes · C2 dataset layout · C3 presence CSV · C4 detections · C5 timeline · C6 openapi
├── configs/            C   timeline.yaml
├── requirements/       D base · A data · B ml · C api
├── data/               A   gitignored (only splits/splits.json is tracked)
├── models/weights/     B   gitignored (GitHub Release model-v1)
├── src/
│   ├── common/         D   read-only contract helpers
│   ├── data/           A   presence labels + frame extraction (timeline ground truth, 2.3.1)
│   ├── models/         B   benchmark (6.1.1)
│   ├── inference/      B   detect_video, fetch_weights
│   ├── timeline/       C   smoothing, builder, evaluate
│   ├── api/            C   FastAPI app, db, jobs, routes/
│   └── reports/        C   PDF report EN/AR
├── web/                D   React + Vite + TS (pages/Analytics, i18n/ar.json, styles/rtl.css → A)
├── tests/              fixtures/ contracts/ e2e/ (D) · unit/<area>/ (owner of the area)
├── notebooks/          A 01_Data.ipynb · B 02_Model.ipynb (Colab)
├── scripts/            D   run_local.*, github/ (generate + setup)
├── docker/ docker-compose.yml   D
└── docs/               problem · data · usability · model · slides · timeline · demo · integration · report · planning
```

## Licences

Code: TODO (team decision). Datasets: see `docs/data/LICENSES_AND_ETHICS.md` (WBS 1.3.1). Research,
non-commercial use only, with citation.
