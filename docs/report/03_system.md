# 4. Timeline Engine and System

<!-- Owner: Member C (WBS 8.1.3). Describes the implementation in mibda-platform/ (or_intelligence/, api/). -->

## 4.1 Architecture and Data Flow

The delivered system lives in `mibda-platform/`. It is a self-contained Python package (`or_intelligence/`) with
two front ends on top of the same database and logic: a Streamlit app (`app/`) and a FastAPI service (`api/`)
used by a React web app (`web/`, Section 5).

```text
video ──► detector (YOLOv8s, best.pt) ──► per-frame boxes ──► timeline engine ──► instrument intervals
              (or_intelligence/detector.py)                   (timeline.py)          │      phase segments
                                                                                       ├─► usage statistics, review flags (insights.py)
                                                                                       ├─► SQLite: cases, notes, users, audit log (db.py)
                                                                                       ├─► FastAPI (api/) ──► React web app
                                                                                       ├─► PDF report EN/AR (report.py)
                                                                                       └─► AI case report + assistant (Claude API, case_report.py)
```

1. **Sampling and detection.** A recording is sampled at a fixed rate (default one frame per second for uploads,
   `sample_step_s = 1.0`) and each sampled frame goes through the detector of Section 3. Every box keeps its
   instrument id and confidence.
2. **Timeline engine** (`or_intelligence/timeline.py`) turns boxes into per-instrument time intervals, statistics
   and phase segments (Section 4.2).
3. **Storage.** Cases, timestamped notes, users (roles: trainee, instructor, admin; salted PBKDF2 password
   hashes) and an audit log are stored in SQLite (`or_intelligence/db.py`). The analysis of each case is stored as
   a file next to its media.
4. **Delivery.** The API serves the case list, case analysis, video or frames, notes and PDF export to the web app.

## 4.2 Temporal Smoothing and Interval Building

Frame-by-frame detections flicker: a tool that is in view for a minute can be missed in single frames (occlusion,
motion blur, smoke), and a single false positive can create a one-frame "use". The engine removes this in three
steps, with defaults in `or_intelligence/config.py` that a reviewer can change per session in the Streamlit Settings view:

| Step | What it does | Default |
|---|---|---|
| Confidence filter | A sample counts as "instrument present" only if a box of that instrument has confidence ≥ threshold (same threshold as Section 3.3) | `conf = 0.25` |
| Majority filter | For each instrument, a sliding window over time keeps a sample positive only if most samples in the window are positive. Removes one-sample flicker in both directions. | `smooth = 3` samples |
| Gap merging | Positive samples closer than the gap limit are joined into one interval, so a short occlusion does not split a segment | `max_gap = 15 s` |

Each sample stands for one sampling step, so a single positive sample becomes an interval of that length instead
of zero. The output is a list of intervals (instrument, start, end), which drives the colour-coded timeline.

From the intervals the engine computes, per instrument: active seconds, percentage of the case, number of segments,
first and last use and longest segment; and per case: duration, number of instrument entries, entries per minute
and number of instruments used (use case 5).

**Review flags** (`or_intelligence/insights.py`, use case 4) are simple rules on the intervals, presented as
"look here" pointers, not as error detection or a skill score:

| Flag | Rule (default) |
|---|---|
| Long use | One instrument in continuous use for ≥ 300 s |
| Frequent entries | ≥ 6 instrument entries inside a 60 s window |
| Idle gap | No instrument for ≥ 120 s (only with dense sampling) |
| Clipper segments | Every clipper segment is listed, because clipping is a key teaching step |

**Surgical phases.** When a recording has phase annotations (CholecT50 replays), they are shown as *Verified*.
Otherwise a small phase estimator (`or_intelligence/phase_estimator.py`: logistic regression on instrument-presence
features followed by a left-to-right Viterbi decode) proposes phases, which are shown as *Estimated* and hatched on
the timeline. Leave-one-video-out accuracy is about 70% (majority-class baseline 36%), from 43% to 98% by video,
on only 5 training videos, so phases are a navigation aid, not a result.

## 4.3 Timeline Evaluation (Success Measure 2)

<!-- TODO(C, 4.1.3): run the raw-vs-smoothed comparison and fill docs/timeline/TIMELINE_EVAL.md, then copy the
     table here. Do not invent numbers. -->

The evaluation set is ready (Section 2.5): 1 fps ground-truth presence labels for a tuning video (`VID23`) and four
held-out reporting videos (`VID14`, `VID15`, `VID22`, `VID29`, 7,652 s in total). The planned measure is per-instrument
F1 of second-by-second presence and segment IoU, before and after smoothing.

**This comparison has not been run yet**, so no timeline-agreement number is reported. The smoothing defaults above
were therefore chosen by inspection, not by the planned parameter sweep on `VID23`.

## 4.4 API

The FastAPI service (`mibda-platform/api/`) exposes the platform to the web app under `/api`:

| Area | Endpoints |
|---|---|
| Session | `POST /login`, `POST /demo` (demo mode only), `POST /logout`, `GET /me` |
| Library | `GET /dashboard`, `GET /cases`, `GET /cases/{id}`, `GET /cases/{id}/thumb` |
| Review | `GET /cases/{id}/analytics`, `GET /cases/{id}/video`, `GET /cases/{id}/frame` |
| Notes | `POST /cases/{id}/notes`, `DELETE /cases/{id}/notes/{note_id}` |
| Reports | `GET /cases/{id}/export.pdf`; AI case report: `GET`/`PUT /cases/{id}/report`, `POST …/report/generate`, `POST …/report/reopen`, `GET …/report/frame`, `GET …/report.pdf` |
| Literature and assistant | `/cases/{id}/refs` (PubMed search), `/cases/{id}/chat` |
| Live analysis | `/live/upload`, `/live/start`, `/live/{job}`, `/live/{job}/frame`, `/live/{job}/stop`, `/live/{job}/save` |

Live analysis runs the detector on an uploaded video in a background job; the page polls the job and updates as
results arrive, and the finished analysis is saved as a new case. Videos in a codec browsers cannot play are served
as server-side frames instead.

## 4.5 PDF Reports (English / Arabic)

`or_intelligence/report.py` builds the case report with ReportLab: case details, a Gantt-style instrument timeline
with phases, the usage table, review flags and the instructor's timestamped notes (use case 2). The same report is
available in Arabic: text is shaped with `arabic-reshaper` and `python-bidi` and set right to left with an
Arabic-capable font (Tahoma/Arial on Windows, DejaVu on Linux). If those are missing, the report falls back to
English and says so. Long Arabic paragraphs can still wrap in the wrong visual order, a known limitation.

## 4.6 AI Case Report with the Claude API

Beyond the fixed PDF of Section 4.5, the platform drafts a written case report with Anthropic's Claude API
(`or_intelligence/llm.py`, `case_report.py`; model set by `ORI_LLM_MODEL`, default `claude-sonnet-5-5`). The call runs
on the server only; the API key (`ANTHROPIC_API_KEY`) never reaches the browser.

**How a report is built**

1. **Case context.** `casecontext.py` turns the case into numbered, labelled text blocks:
   case facts (C), phases (P), instrument usage (I), review flags (F), the doctor's notes (N) and teaching clips (K).
   The text is de-identified first (Section 4.7).
2. **Draft.** Claude receives the blocks with a strict instruction: use only these blocks, invent no findings,
   patient details or outcomes, and reply in JSON with a 3–5 sentence summary, a list of observations and the
   limitations of the data. Every observation must name the blocks that support it (for example `["P1","N2"]`).
3. **Check.** The platform drops every observation whose evidence labels do not exist in the context, so an
   unsupported statement cannot reach the report.
4. **Doctor review.** The doctor edits the text, regenerates the AI part (their own comments and chosen frames are
   kept), adds or removes evidence frames (taken from real timestamps: notes and phase starts) and approves it.
5. **PDF.** The report is exported in English or Arabic. Until a doctor ticks the review box and approves it, the PDF
   is marked **DRAFT**; after approval it shows **FINAL** with the doctor's name and date. Trainees see only approved
   reports.

Throughout, the three kinds of content are kept apart and labelled in the app and in the PDF: **automated
analysis** (the platform), **doctor-provided** text (notes, comments) and **AI-generated** text (Claude).

**Related literature and research assistant.** The same case view searches PubMed (NCBI E-utilities) with the
procedure, phases and instruments of the case and lists real records only (PMID and link; nothing is generated).
A case-specific assistant answers questions with Claude using retrieval over the case blocks, the notes and the
retrieved abstracts; it cites them as `[N2]`, `[R1]`, says when the evidence is missing, labels general knowledge
as such and refuses to diagnose or choose a treatment.

Token usage of every Claude call is shown to the user and written to the audit log.

## 4.7 Privacy and Safety

- Uploaded cases need a consent confirmation and a retention period; purging deletes only files inside the
  platform's own data folders.
- Faces are blurred in video previews, and library previews are blurred on the server (best effort, not a certified
  anonymiser).
- The Claude features (Section 4.6) are off unless the administrator sets `ORI_ALLOW_EXTERNAL_AI=1`. Only text
  leaves the server, never video or images. It is de-identified first (`or_intelligence/deid.py`: names with titles,
  user names, e-mails, phone numbers, long IDs, dates) and the case title is replaced by "Case #id". This is best
  effort, not a certified anonymiser, so doctors must not type patient names into notes.
- The audit log records sign-ins (including failed ones), case views, notes, PDF exports, AI report actions
  (generate, edit, approve, reopen) with token usage, literature searches, user creation and data purges.

## 4.8 Tests

`mibda-platform/tests/` holds a pytest suite (62 test functions in 9 files) covering the timeline engine, phase estimator, dataset adapters,
internationalisation, API and platform views (`python -m pytest` from inside `mibda-platform/`).
