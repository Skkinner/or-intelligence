# OR Intelligence

**Laparoscopic instrument detection → clickable instrument timeline for surgical education.**
Computer Vision Final Project · Deadline **Wednesday 25 Nov 2026, 23:59**

A reviewer uploads a recorded laparoscopic cholecystectomy. A fine-tuned YOLO detector finds 6 instruments
(grasper, bipolar, hook, scissors, clipper, irrigator) in sampled frames. Temporal smoothing removes flicker,
and the result is a colour-coded instrument timeline: click a bar and the video jumps to that moment.
Sessions export as a PDF report with timestamped instructor notes, in English or Arabic.

> Educational review tool, **not** a diagnostic or clinical decision-making system. Public research data only
> (non-commercial licences). No dataset, video or model weights are stored in this repository.

## Status: v1.0.0 (final submission, 25 Nov 2026)

**The delivered application is in [`mibda-platform/`](mibda-platform/README.md)**: a self-contained platform with a
Streamlit app, a FastAPI service and a React web app, its own tests and requirements. Start there to run the demo.

| Deliverable | Where |
|---|---|
| Application (code) | [`mibda-platform/`](mibda-platform/README.md) |
| Data pipeline and model training | [`notebooks/`](notebooks/) (Colab) |
| Final report | [`docs/report/report.pdf`](docs/report/report.pdf) (sources: `docs/report/*.md`) |
| Presentation | [`docs/slides/OR_Intelligence.pptx`](docs/slides/OR_Intelligence.pptx) |
| Live demo script | [`docs/demo/README.md`](docs/demo/README.md) |
| Data, model and usability results | [`docs/data/`](docs/data/), [`docs/model/`](docs/model/), [`docs/usability/`](docs/usability/) |

The folders `src/`, `web/`, `tests/`, `docker/` and `scripts/run_local.*` at the repository root are the **original
team scaffold** (contracts, fixtures and starter files with `TODO` markers). The working implementation was built in
`mibda-platform/` instead, so these scaffold folders are kept for reference and are not the submitted app.

## Objectives and results

| Success measure | Result |
|---|---|
| 1. **Detection:** mAP@0.5 and per-instrument precision/recall on a held-out test split (by surgery) | Test mAP@0.5 **0.881** on 22 unseen surgeries ([docs/model/EVALUATION.md](docs/model/EVALUATION.md)) |
| 2. **Timeline:** agreement between predicted tool intervals and ground-truth presence labels | Ground truth prepared ([docs/data/timeline_eval_set.md](docs/data/timeline_eval_set.md)); comparison not run |
| 3. **Usability:** time to find a moment with the timeline vs manual scrubbing (pilot study) | Median **66.2 s → 8.8 s**, 7.57× faster, n = 4 ([docs/usability/RESULTS.md](docs/usability/RESULTS.md)) |

## Run the application

See [`mibda-platform/README.md`](mibda-platform/README.md) for the full guide. In short (Windows PowerShell, from
inside `mibda-platform/`):

```powershell
pip install -r requirements.txt
python scripts/seed_demo.py --cholect50 "C:\path\to\cholect50-challenge-val"
streamlit run app/main.py
```

The trained detector `best.pt` goes in `mibda-platform/models/` (never committed). The optional AI case report uses
the Claude API: set `ANTHROPIC_API_KEY` and `ORI_ALLOW_EXTERNAL_AI=1` in `mibda-platform/.env`
(see `mibda-platform/.env.example`).

## Original scaffold (reference)

The sections below describe the original team scaffold at the repository root, kept for reference.

### Pipeline (as planned)

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
| Member C | Backend & Timeline Engineer | `src/timeline/`, `src/api/`, `src/reports/`, `configs/timeline.yaml`, `docker/`, `docs/timeline/`, `docs/demo/` | 9 |
| Member D | Frontend Lead & Integration Owner | `contracts/`, `tests/fixtures/`, `web/` (except A's files), `scripts/`, `.github/`, root docs | 11 |

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

1. Download the CholecInstanceSeg dataset into Drive with [`notebooks/00_Download_CholecInstanceSeg.ipynb`](notebooks/00_Download_CholecInstanceSeg.ipynb), and share the folder with the team.
2. Member A: open `01_Data` in Colab → *Runtime → Run all*.
3. Member B: open `02_Model` in Colab → *Runtime → Change runtime type → T4 GPU* → *Run all*.

To open a notebook from this private repo in Colab: *File → Open notebook → GitHub*, tick *Include private repos*.
Weights and data stay in Drive; they are never committed to GitHub. The app uses the same inference code from
`src/inference/detect_video.py` with `best.pt` copied to `models/weights/`.

## Scaffold installation (root `src/` and `web/`, not the submitted app)

Requirements: Python 3.11+, Node 20+, Git. Training happens in Colab, not here.

```bash
git clone https://github.com/Skkinner/or-intelligence.git
cd or-intelligence
python -m venv .venv
# Windows: .venv\Scripts\activate    macOS/Linux: source .venv/bin/activate
pip install -r requirements/<your-area>.txt     # data.txt (A) · ml.txt (B) · api.txt (C) · base.txt (D)
cd web && npm ci && cd ..                       # web work (A, D)
```

## Scaffold commands

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
├── mibda-platform/     the delivered application (Streamlit, FastAPI, React, tests)
├── notebooks/          00_Download · A 01_Data.ipynb · B 02_Model.ipynb (Colab)
├── scripts/            D   run_local.*, github/ (generate + setup)
├── docker/ docker-compose.yml   C   deployment files (7.1.2)
└── docs/               problem · data · usability · model · slides · timeline · demo · integration · report · planning
```

## Licences

Code: no open-source licence has been chosen, so all rights are reserved by the project team. Datasets: see `docs/data/LICENSES_AND_ETHICS.md` (WBS 1.3.1). Research,
non-commercial use only, with citation.
