# 1. Introduction

<!-- Owner: Member D (WBS 8.1.4). Sources: README.md, PROJECT_PLAN.md, REQUIREMENTS_CHECKLIST.md, mibda-platform/README.md. -->

## 1.1 Problem

Surgical trainees learn a great deal by reviewing recorded operations, but a laparoscopic cholecystectomy lasts
30–90 minutes and the moments worth discussing (the first clip, a short cut with scissors, a long irrigation)
often last only a few seconds. Today an instructor finds them by scrubbing the seek bar by hand. This is slow, it is
easy to step over a 5–10 second action, and the result of the review (what was seen, what was said) is rarely
written down in a form a trainee can keep. Existing review tools are also almost always English-only, which is a
barrier for Arabic-speaking programmes.

**OR Intelligence** is a web-based review platform for recorded laparoscopic cholecystectomies. A fine-tuned YOLO
detector finds six instruments (grasper, bipolar, hook, scissors, clipper, irrigator) in sampled frames. Temporal
smoothing removes flicker, and the result is a colour-coded instrument timeline: clicking a bar jumps the video to
that moment. Instructors add timestamped notes, search a case library by instrument, compare cases, and export a
PDF report in English or Arabic. An optional AI case report, drafted with the Claude API from the case's own data and
approved by a doctor, turns the analysis into a written summary.

> OR Intelligence is an **educational review aid, not a diagnostic or clinical decision-making system**. It is
> built and evaluated on public research data only (non-commercial licences, Section 2.1).

## 1.2 Objective

Turn a raw surgical recording into a navigable, searchable record of *which instrument is in use when*, so that
reviewers find teaching moments in seconds instead of minutes, in English or Arabic.

The solution is designed as an end-to-end computer-vision pipeline:

```text
problem → data (Section 2) → detector (Section 3) → timeline engine and API (Section 4)
        → web application (Section 5) → evaluation (Sections 2.6, 3.3, 4.3) → deployment and demo
```

## 1.3 Use Cases

| # | User | Scenario | Platform feature |
|---|---|---|---|
| 1 | Instructor, trainee | Jump straight to a moment ("when was the hook first used?") instead of scrubbing | Clickable instrument timeline and phase list that seek the video |
| 2 | Instructor | Comment on the operation while reviewing it and give the trainee a written record | Timestamped notes, PDF report (English / Arabic) and an AI-drafted case report (Claude API) that the doctor reviews and approves |
| 3 | Instructor | Prepare a teaching session ("show all clipping segments") across many recordings | Case library with search by instrument |
| 4 | Instructor | Spot unusual tool patterns quickly (long irrigation, many tool switches in a short time) | Rule-based review flags on the timeline |
| 5 | Programme director | Compare cases: time per instrument, total time, number of tool entries | Per-case statistics, comparison and progress views |

## 1.4 Success Measures

1. **Detection:** mAP@0.5 and per-instrument precision/recall on a held-out test split separated by surgery
   (result: Section 3.3).
2. **Timeline:** agreement between predicted instrument intervals and ground-truth presence labels
   (ground truth: Section 2.5; result: Section 4.3).
3. **Usability:** time to find a moment with the timeline vs. manual scrubbing (result: Section 2.6).

## 1.5 Report Structure

Section 2 describes the data, its licences and the usability pilot. Section 3 covers the detection model.
Section 4 explains the timeline engine, the API, the PDF reports and the AI case report drafted with the Claude API.
Section 5 presents the web application, the limitations and the conclusion. The business model is covered in the
presentation.
