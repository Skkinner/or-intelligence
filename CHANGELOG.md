# Changelog

Owner: Member D (7.2.1). Written at the release candidate.

## [1.0.0] — 2026-11-25

Final submission of the Computer Vision project.

### Added

- **Data pipeline** on CholecInstanceSeg (85 surgeries, 41,933 frames): download notebook, YOLO conversion, split by
  surgery, EDA, licences and ethics checklist, 1 fps timeline ground truth (`notebooks/00–01`, `docs/data/`).
- **Instrument detector**: YOLOv8s fine-tuned on 6 instruments, test mAP@0.5 0.881 on 22 unseen surgeries; evaluation
  report, model card and CPU/GPU benchmark (`notebooks/02_Model.ipynb`, `docs/model/`).
- **Application** in `mibda-platform/`: Streamlit app, FastAPI service and React web app with instrument timeline,
  phase tracking, timestamped notes, case library and search, comparison, review flags, English/Arabic UI and PDF
  reports, roles and audit log, live video analysis.
- **AI case report** drafted with the Claude API from the case's own data, with evidence labels, de-identification
  and doctor approval before it is final; PubMed literature search and a case-specific research assistant.
- **Usability pilot**: median time to find a moment 66.2 s (manual scrubbing) vs 8.8 s (timeline), n = 4
  (`docs/usability/`).
- **Final report** (`docs/report/report.pdf`), **presentation** (`docs/slides/`) and **live demo script**
  (`docs/demo/README.md`).

### Known gaps

- Timeline agreement with ground truth (success measure 2) was not measured.
- The Docker image in `mibda-platform/` is written but not built; no recorded demo video (live demo only).
- The scaffold at the repository root (`src/`, `web/`) is not the submitted app.

## [0.1.0] — 2026-11-23

- Repository scaffold, contracts (draft), synthetic fixtures, starter modules for all 38 WBS tasks.
