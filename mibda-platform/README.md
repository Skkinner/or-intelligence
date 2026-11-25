# OR Intelligence: surgical video review platform

> **Where this lives:** this folder is a self-contained platform (Streamlit app, FastAPI layer, React app, tests). It does not touch the rest of the repository: run every command below **from inside `mibda-platform/`**. It uses its own `requirements.txt`, `pytest.ini` and `ruff.toml`, and it is not collected by the repo-level CI test run. Model weights (`models/best.pt`), datasets and `.env` are never committed (see the repo `.gitignore`).


A medical-education platform for recorded operations: **operation tracker** (phase by phase, with live playback),
instrument timeline, phase list with jump-to-phase, notes, case library with cross-case search, comparison,
per-trainee progress, procedure library, English/Arabic UI and PDF reports, roles, audit log and data retention.

> Educational review aid. Not a diagnostic or assessment system. Public research datasets only (non-commercial licences).

## Honest status

| Part | State |
|---|---|
| Streamlit platform | Built and running. Every view renders without errors in a headless Streamlit test; Dashboard, Operation tracker (live playback), Review, Library, Compare, Progress, Model & data and Settings (Arabic) were also opened in a real browser. |
| Visual design | MIBDA' theme (hero header, KPI cards, phase stepper, case cards with thumbnails), shared by the Streamlit and React apps. |
| **Operation tracker** | Works. Phases come from the dataset annotations (demo) or from the **phase estimator** (below). |
| **Phase estimator** | Small logistic-regression + left-to-right Viterbi model on the instrument timeline. **Leave-one-video-out accuracy about 70% (majority-class baseline 36%), ranging from 43% to 98% by video.** Trained on only 5 videos; offline use only. |
| Procedure library | **Per-procedure engine**: each procedure (procedures.yaml) defines its own phases and instruments. 1 procedure ready (cholecystectomy), **Cataract surgery adapter verified on the real Cataract-101 files**, 6 planned. Phases of planned procedures are left empty on purpose, not guessed. |
| **Cataract-101 adapter** | Run on the real release (101 videos, one `annotations.csv` with phase start frames, `phases.csv`): phase ids match the page order, 5 cases imported and all main views render in EN/AR. Parsing and rendering are checked; **the look and long-video playback in a real browser are not**. Phase estimator and YOLO ids remain cholecystectomy-only. |
| Dataset merge | `scripts/merge_datasets.py` is unit-tested on synthetic data. Not run on real merged datasets. |
| Tests | `python -m pytest` runs the suite in `tests/` (timeline, phase estimator, datasets, i18n, API, platform, AI features); the real-dataset tests run only when `ORI_TEST_CHOLECT50` is set. |
| **Instrument detector (YOLOv8s)** | Trained by the team on the CholecInstanceSeg boxes (85 surgeries, split by surgery): **test mAP@0.5 0.881** (scissors weakest at 0.711, 149 test boxes). Independent check on CholecT45 labels of 4 held-out videos (presence per frame): precision/recall grasper 0.96/0.85, bipolar 0.86/0.88, hook 0.95/0.97, scissors 0.67/0.67 (21 positives), clipper 0.82/0.88, irrigator 0.90/0.82. About 130 ms per frame on a CPU. Weights: `models/best.pt` (never committed). |
| **Live analysis page** | Runs the detector on a video frame by frame and shows boxes, instruments in view and an approximate live phase (online forward filter, weaker than the offline decode: 57-91% on the 5 labelled videos it was trained on). Saving a case recomputes phases offline. Tested end to end on a 240-frame clip; not tested on long videos or on a GPU. |
| Docker (React + FastAPI) | Built and tested: `docker compose up -d --build` → <http://localhost:8080> (`Dockerfile.api`, `web/Dockerfile`). Public mode without demo login: `docker-compose.public.yml`; online deployment: [`deploy/DEPLOY.md`](deploy/DEPLOY.md). The older `Dockerfile` (Streamlit only, without the detector) is not built. |
| Timeline interaction | In this Streamlit version a single click on the chart does not select; **drag a small box** to jump (the phase list's Go buttons and the time slider also jump). |

Demo cases imported with `seed_demo.py` **replay the dataset's own annotations**, not the detector's output. The UI
labels them "Ground-truth annotation replay (demo, not model output)": do not present them as model results. Model
results come from Live analysis (or "Run trained model on this case") with `models/best.pt`.

## Quick start (Windows PowerShell)

```powershell
pip install -r requirements.txt
python scripts/seed_demo.py --cholect50 "C:\path\to\cholect50-challenge-val"
streamlit run app/main.py
```

Demo accounts (admin / instructor / trainee) are defined in `scripts/seed_demo.py` (local use only; change or delete them before any real deployment).

## Train

```bash
pip install -r requirements-train.txt
# 1) phase estimator (CPU, seconds)
python scripts/train_phase_estimator.py --src /path/to/cholect50-challenge-val        # -> models/phase_estimator.json
# 2) instrument detector (needs a GPU: Colab/Kaggle)
python scripts/prepare_yolo.py --src /path/to/cholect50-challenge-val --out datasets/or_yolo
python scripts/train.py --data datasets/or_yolo/data.yaml --epochs 60                  # -> models/best.pt
python scripts/evaluate.py --data datasets/or_yolo/data.yaml --split test              # -> models/metrics.json
```

The challenge-validation set is small (5 videos, 1,318 frames, 1,319 boxes). On the default split the validation video has no
irrigator boxes, and hook / scissors / clipper have few examples, so expect weak, noisy metrics on those classes.

## Datasets, procedures and merging

- `datasets.yaml`: registry of public datasets (also shown in the app). `procedures.yaml`: the procedure library.
- Adapters that exist: CholecT50 challenge-validation (`prepare_yolo.py`), CholecInstanceSeg (`prepare_instance_seg.py`;
  the release has **annotations only, no images**), generic image + binary-mask folders (`masks_to_yolo.py`).
- Merge several prepared YOLO datasets into one with class-name mapping:
  `python scripts/merge_datasets.py --src a=datasets/x --src b=datasets/y --out datasets/merged --rename "Grasper=grasper"`
- **Cataract-101** (continuous videos with 10 phases, no instrument labels): download `cataract-101.zip` (about 8.3 GB) from the
  [ITEC page](https://ftp.itec.aau.at/datasets/ovid/cat-101/index.html) after accepting its terms, unzip, then
  `python scripts/inspect_cataract101.py <folder>` and `python scripts/seed_demo.py --cataract101 <folder> --limit 5`.
- **Adding a procedure** = add its dataset to `datasets.yaml`, write an adapter that builds a `CaseAnalysis` (set `procedure=<id>`),
  and describe the procedure (phases, instruments) in `procedures.yaml`. The tracker, review, compare and PDF report read the
  phases and instruments from that definition. A procedure without instrument labels shows phases only.
  Still cholecystectomy-only: `constants.py` class ids used by the YOLO scripts, the phase estimator, and the Progress charts.

## AI case report, related literature and research assistant

Three tabs inside every case (Review page), for instructors and admins:

| Tab | What it does | Source of truth |
|---|---|---|
| AI report | Drafts a structured report with Claude, lets the doctor edit it, regenerate the AI part, add or remove evidence frames, approve it as final, and export a PDF. | Case facts, doctor notes, analysis results. Frames come from real timestamps (notes, phase starts). |
| Related resources | Searches PubMed (NCBI E-utilities) with the procedure, the case's phases and instruments. Shows title, authors, date, type, start of the abstract, why it matched, and the PubMed link. | Real PubMed records only (PMID + link); nothing is generated. |
| Research assistant | Case-specific chat. Retrieval picks the relevant case chunks, notes and paper abstracts; Claude answers with citations like `[N2]`, `[R1]` and says when evidence is missing. | Same chunks, shown under each answer as "Sources". |

Labelling: automated analysis, doctor-provided text and AI-generated text are shown and printed separately. An AI draft
is marked DRAFT in the PDF until a doctor ticks the review box and approves it. Observations the model makes without a
valid supporting source are dropped. Trainees only see an approved report.

Setup (`.env.example` lists the variables):

```powershell
$env:ANTHROPIC_API_KEY = "sk-ant-..."     # Claude Console key, server side only
$env:ORI_ALLOW_EXTERNAL_AI = "1"          # explicit approval to send de-identified text to Claude
streamlit run app/main.py
```

Privacy: only text leaves the server (no video, no images). It is de-identified first (`or_intelligence/deid.py`: names with
titles, user names, e-mails, phones, long IDs, dates) and the case title is replaced by "Case #id". This is best-effort,
not a certified anonymiser, and doctors must not type patient names into notes. With `ORI_ALLOW_EXTERNAL_AI` unset the
AI buttons are disabled; PubMed search works without a key. Token usage is shown and written to the audit log.
Dashboard and library previews are blurred on the server; the sharp frame is only shown inside the case review.

## Layout

```text
or_intelligence/   core: timeline, insights, phase_estimator, detector, report, db, auth, procedures, dataset adapters, i18n
app/               Streamlit UI (main.py, theme.py, views/)
scripts/           prepare_*, masks_to_yolo, merge_datasets, train, evaluate, train_phase_estimator, seed_demo
models/            phase_estimator.json (+ metrics); best.pt goes here after training
tests/             pytest suite
datasets.yaml  procedures.yaml
```

## Design notes

- Splits are **by video**, never by frame (neighbouring frames are near-duplicates and would leak).
- Progress charts are descriptive hints from instrument presence, not error detection or a skill score.
- Uploaded cases need a consent confirmation and a retention period; purging only deletes files inside the platform's own data folders.
- Faces are blurred in video previews (best effort, not certified anonymization).
- Arabic PDFs need an Arabic-capable font (Tahoma/Arial on Windows, DejaVu on Linux) plus `arabic-reshaper` and `python-bidi`; long Arabic paragraphs may wrap in the wrong visual order.

## Phases: what is verified and what is estimated

- Phases from annotations (CholecT50 / Cataract-101 replays) are shown as **Verified**.
- Phases from the model are **Estimated** (hatched on the timeline, with the model's confidence); short or low-confidence ones read **Estimated, uncertain**.
- The estimator was trained to read whole operations. A recording is treated as a complete operation only if `params["complete_operation"]` is true; otherwise (clips, live recordings) it uses the instruments around each moment only, so a 4-minute excerpt is no longer stretched across every phase.
- Cases are no longer created from the UI (the Add cases page was removed). Cases come from the public-dataset importers and from saving a Live analysis.

## React front end (web/) and API (api/)

The same platform is also available as a React + Vite + TypeScript app on top of a FastAPI service. Both use the same database and logic; the Streamlit app still runs.

```powershell
# terminal 1: API (set ORI_DEMO_MODE=1 for the one-click demo login)
$env:ORI_DEMO_MODE="1"; python -m uvicorn api.main:app --port 8000
# terminal 2: web app (proxies /api to :8000)
cd web; npm install; npm run dev        # http://localhost:5173
```

Ported: sign-in, dashboard, case library, review (video or server-side frames, detection overlay, timeline, phase list with jump and live highlight, usage, notes, PDF), AI report, related literature, research assistant, Live analysis (upload or sample clip, runs the YOLO detector and the online phase estimator in the background, the page updates as results arrive, then save as a case), operation tracker (phase steps, timeline with playhead, time per phase vs. library median, instrument-by-phase heatmap, phase table), settings, Arabic/English with RTL. Detection boxes show the instrument name and confidence; the model's class names are matched to the platform instruments by name. Not ported (still in Streamlit): Compare, Progress, Model & data, procedure library, admin pages.
Videos in a codec browsers cannot play (MPEG-4 part 2) are shown as privacy-processed frames from the server instead of a `<video>`.

### Design system (web/)

`web/src/theme.css` holds the whole MIBDA' design system (deep burgundy `#5C061C`, warm beige `#F2E9E1`, muted copper `#CD7F32`; glass surfaces, sidebar, video workstation, phase timeline, tables, responsive drawer). Reusable pieces: `components/ui.tsx` (Glass, Metrics, PageHead, Hero, CaseCard, Alert, Skeleton), `components/charts.tsx` (AreaChart, Donut, Ring, HBars, no chart library), `components/PhaseTimeline.tsx`, `components/review.tsx` (Player with labelled detection boxes, Timeline, PhaseList). Icons are Lucide; fonts are Inter and IBM Plex Sans Arabic (bundled via @fontsource, no external requests). Instrument and phase colours come from the backend and use the same palette.
