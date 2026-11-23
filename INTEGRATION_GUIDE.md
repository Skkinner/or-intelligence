# Integration Guide

How the four members' components connect, and how Member D integrates them. Integration owner: **Member D**.

## Principle

Components only meet through the **contracts** in `contracts/`. Every member builds and tests against those
contracts plus the synthetic data in `tests/fixtures/`, so nobody waits for anybody. Integration is then
"replace the fixture with the real producer", not a refactor.

## Component map

| # | Producer → Consumer | Contract | Interface | Fixture until ready | Real producer ready |
|---|---|---|---|---|---|
| 1 | D → all | C1 `contracts/classes.json` | `src.common.contracts.class_names()`, `class_colors()` | — | now (draft) |
| 2 | A → B | C2 `contracts/dataset_layout.md` | `data/processed/dataset.yaml`, `data/splits/splits.json` | — | 2.2.2, M2 Tue 12:00 |
| 3 | A → C | C3 `contracts/presence.schema.md` | `data/processed/presence/<video>.csv` | `tests/fixtures/sample_presence.csv` | 2.3.1, Tue afternoon |
| 4 | B → C | C4 `contracts/detections.schema.json` | `detect_video(video_path, out_path, sample_fps, conf, weights, on_progress) -> dict` | `tests/fixtures/sample_detections.jsonl` | 3.3.1, M3 Tue 18:00 |
| 5 | B → C, D | weights | `models/weights/best.pt` via `python -m src.inference.fetch_weights` | COCO `yolov8n.pt` stand-in | 3.1.2, M4 Tue 23:00 |
| 6 | C → C, D, A | C5 `contracts/timeline.schema.json` | `build_timeline(dets_path, video_id, params) -> dict` | `tests/fixtures/sample_timeline*.json` | 4.1.2, Tue morning |
| 7 | C → D, A | C6 `contracts/openapi.yaml` | HTTP on `:8000`, prefix `/api` | web mock mode (`VITE_API_MOCK=1`) | 4.2.1 / 4.2.2, Tue |
| 8 | C → D | PDF | `GET /api/videos/{id}/report.pdf?lang=en\|ar` | — | 4.3.1, Wed morning |
| 9 | A → D | web page | `web/src/pages/Analytics/index.tsx` (auto-registered) | — | 5.2.2, Wed morning |
| 10 | A → D | locale | `web/src/i18n/ar.json`, `web/src/styles/rtl.css` (auto-loaded) | English fallback | 5.2.3, Wed morning |

## Conventions

| Item | Convention |
|---|---|
| Class ids | 0 grasper · 1 bipolar · 2 hook · 3 scissors · 4 clipper · 5 irrigator (never hard-code; use C1) |
| Video id | file stem of the uploaded video, or the API-assigned id |
| Frame files | `<video_id>_<frame_index>.jpg` / `.txt` |
| Times | seconds as float, from video start; UI shows `mm:ss` |
| Boxes | detections: `[x1, y1, x2, y2]` normalised 0–1 · YOLO labels: `cls cx cy w h` normalised 0–1 |
| Storage (API) | `$STORAGE_DIR/videos/<id>.mp4`, `detections/<id>.jsonl`, `timelines/<id>.json`, `app.db` |
| Config | `configs/data.yaml` (A), `configs/train.yaml` + `experiments/` (B), `configs/timeline.yaml` (C) |
| Env | `.env.example`: `INFERENCE_MODE`, `WEIGHTS_PATH`, `STORAGE_DIR`, `SAMPLE_FPS`, `VITE_API_MOCK` |
| Python imports | always from repo root: `from src.timeline.builder import build_timeline` |
| Web extension points | new page = new folder `web/src/pages/<Name>/index.tsx` exporting `route` + default component; new language = `web/src/i18n/<lang>.json` |

## Switch-over points

1. **M3 (Tue 18:00):** C's API runs end-to-end in fixture mode; D switches the web from mock mode to the real API
   (`VITE_API_MOCK=0`, Vite proxies `/api` to `:8000`).
2. **M4 (Tue 23:00):** B shares `best.pt`; C sets `INFERENCE_MODE=real` and verifies on the fixture video.
3. **Wed morning:** B posts the recommended confidence threshold (3.2.1); C updates `configs/timeline.yaml` (4.1.3).
4. **M5 (Wed 18:00):** everything merged into `develop`, one-command run works, smoke checklist passes.

## Integration procedure (Member D)

At each merge window:

```bash
git switch develop && git pull
gh pr list --base develop                     # review queue
gh pr checks <n> && gh pr merge <n> --squash  # only green PRs with 1 approval
pytest -m "not gpu and not data" && (cd web && npm ci && npm run build && npm test)
```

Log the window in `docs/integration/INTEGRATION_LOG.md`. Conflicts are resolved by D on `develop`; nobody edits
another member's files to make their own PR pass.

Full-stack check (7.1.1 / 7.1.2):

```bash
INFERENCE_MODE=real ./scripts/run_local.sh    # or: docker compose up --build
# open http://localhost:8080, upload a 10–30 min video, run tests/e2e/SMOKE_CHECKLIST.md
cd tests/e2e && npm install && npm run install-browsers && npm test
```

Release (7.2.1, Wed 20:00): open PR `develop → main`, merge, `git tag v1.0.0 && git push origin v1.0.0`,
update `CHANGELOG.md`. After that only docs and slides change.

## Contract tests

`tests/contracts/test_schemas.py` validates every fixture against the schemas, and
`tests/unit/api/test_api.py::test_every_contract_path_is_routed` fails if an endpoint in `openapi.yaml` has no route.
Producers should add a test that their real output validates against the same schema
(`src.common.contracts.validate(obj, "timeline")`).

## Changing a contract

Open a "Contract change request" issue, then a PR that touches only `contracts/` (+ regenerated fixtures with
`python tests/fixtures/make_fixtures.py`). It needs approval from D and every consumer listed in
`contracts/README.md`, and an entry in `contracts/CHANGELOG.md`.
