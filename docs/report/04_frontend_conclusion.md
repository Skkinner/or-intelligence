# 5. Web Application, Limitations and Conclusion

<!-- Owner: Member D (WBS 8.1.4). Describes mibda-platform/web (React) and mibda-platform/app (Streamlit). -->

## 5.1 Web Application

The platform has two user interfaces over the same API, database and logic. The **React + Vite + TypeScript app**
(`mibda-platform/web/`) is the main interface; the **Streamlit app** (`mibda-platform/app/`) still runs and holds
the views that were not ported yet (Compare, Progress, Model & data, procedure library, admin pages).

| Page | What the user can do | Use case |
|---|---|---|
| Sign-in | Local accounts with three roles (trainee, instructor, admin); one-click demo login in demo mode | — |
| Dashboard | Key figures and recent cases | — |
| Case library | Browse cases as cards or a table with blurred thumbnails; filter by title, tags and source. Cross-case moment search ("every clipping segment") and filtering by instrument are in the Streamlit library view. | 3 |
| Review | Video (or server-side frames) with labelled detection boxes, colour-coded instrument timeline and phase list that jump the video, live highlight of the current phase, usage table, timestamped notes, PDF export | 1, 2, 4 |
| Operation tracker | Phase steps, timeline with playhead, time per phase vs. the library median, instrument-by-phase heatmap | 5 |
| Live analysis | Upload a video or use the sample clip; the detector and online phase estimator run in the background and the page updates as results arrive; save the result as a case | — |
| AI report, literature, assistant | Generate a case report draft with the Claude API, edit it, pick evidence frames, approve it and export the PDF; PubMed search; case-specific assistant with cited sources (off until the administrator enables it; Section 4.6) | 2 |
| Settings | Language (English / Arabic) and account; timeline parameters are set in the Streamlit Settings view | — |

**Arabic interface.** Every label exists in English and Arabic; switching to Arabic sets the whole layout right to
left (navigation, tables, timeline axis) and uses IBM Plex Sans Arabic. Fonts and icons are bundled, so the app makes
no external requests for them.

**Design.** A single design system (`web/src/theme.css`) defines the MIBDA' theme (deep burgundy, warm beige, muted
copper), with reusable components for cards, charts, the phase timeline and the video workstation. Instrument and
phase colours come from the backend, so the web app, the Streamlit app and the PDF report use the same palette.

**Usability (Success Measure 3).** In the pilot study (Section 2.6) the timeline cut the median time to find a
moment from 66.2 s with manual scrubbing to 8.8 s (7.57× faster), and raised the success rate from 91.7% to 100%.

## 5.2 Results Against the Success Measures

| Success measure | Result | Section |
|---|---|---|
| 1. Detection | Test mAP@0.5 **0.881** on 22 unseen surgeries; scissors weakest (AP@0.5 0.711) | 3.3 |
| 2. Timeline agreement | Evaluation set prepared; **comparison not run yet** | 2.5, 4.3 |
| 3. Usability | Median time to find a moment **66.2 s → 8.8 s** (pilot, n = 4) | 2.6 |

## 5.3 Limitations

- **One procedure.** Trained and tested on laparoscopic cholecystectomy only. A Cataract-101 adapter shows the
  per-procedure design works for phases, but the detector and phase estimator are cholecystectomy-only.
- **Non-commercial research data.** The datasets and therefore the weights are CC BY-NC-SA 4.0; a commercial
  version needs institution-owned or licensed data.
- **Educational, not diagnostic.** The timeline, flags and statistics describe instrument presence; they do not
  detect errors or score the surgeon.
- **Weak classes and estimated phases.** Scissors are sometimes detected as grasper (Section 3.4). Estimated phases
  reach about 70% accuracy on 5 videos and are always labelled *Estimated*.
- **Timeline agreement not measured.** Smoothing defaults were set by inspection (Section 4.3).
- **Small usability pilot.** Four participants; the result shows a clear trend but is not a formal test.
- **Privacy tools are best effort.** Face blurring and text de-identification are not certified.
- **AI-drafted reports depend on an external service.** The Claude features need an API key, a network connection
  and the administrator's approval, and every draft must be checked by a doctor before it is final.
- **Deployment.** The platform runs locally; the Docker image is written but has not been built and tested.
  Live analysis was tested on short clips on a CPU, not on long videos or a GPU.

## 5.4 Future Work

- Run the timeline evaluation and tune smoothing on `VID23` (Section 4.3).
- Retrain the detector with oversampled scissors and clipper frames (Section 3.6).
- Train the phase estimator on more videos and add more procedures from `procedures.yaml`.
- Port Compare, Progress and the admin pages to the React app; build and test the Docker image.
- Repeat the usability study with more participants, including Arabic-speaking trainees.

## 5.5 Conclusion

OR Intelligence turns a long laparoscopic recording into a colour-coded, clickable instrument timeline. A YOLOv8s
detector trained on 85 surgeries from public data reaches mAP@0.5 0.881 on unseen surgeries, and a simple smoothing
and interval engine turns its per-frame output into segments, statistics and review flags. Around it, the platform
adds what instructors need to teach with the result: timestamped notes, a searchable case library, comparisons,
English and Arabic reports, an AI case report drafted with the Claude API under doctor review, and roles with an
audit log. In a small pilot, reviewers found moments about 7.6 times
faster than by scrubbing. The main open item is measuring timeline agreement against the ground truth that is
already prepared.
