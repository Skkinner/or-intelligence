# Usability Pilot Protocol: Manual Scrubbing vs. OR Intelligence Timeline (Owner: Member A, WBS 6.2.1)

## 1. Objective & Success Measure

This pilot study evaluates **Success Measure 3** of the OR Intelligence project:
> *Time-to-find usability test comparing manual video scrubbing against the interactive colour-coded instrument timeline when locating clinically relevant instrument moments in recorded laparoscopic cholecystectomy procedures.*

## 2. Participants & Ethics

- **Sample size:** $n = 4$ participants (meets and exceeds the WBS target of $\ge 3$ participants).
- **Participant profile:** Fellow biomedical engineering / computer vision graduate students familiar with surgical video review concepts.
- **Consent & privacy:** Verbal informed consent obtained prior to each session. Participants are assigned anonymous identifiers (`P1`, `P2`, `P3`, `P4`). No names, recordings, or personal data are collected or stored, in compliance with our data governance checklist (`docs/data/LICENSES_AND_ETHICS.md`).

## 3. Experimental Design

- **Design:** Within-subject crossover design with two conditions:
  1. **Manual Scrubbing (`scrubbing`):** Standard HTML5 video player seek bar only (timeline hidden).
  2. **OR Intelligence Timeline (`timeline`):** Full review workspace with colour-coded instrument lanes (`grasper`, `bipolar`, `hook`, `scissors`, `clipper`, `irrigator`) where clicking a bar jumps the playhead directly to that segment.
- **Counterbalancing:** To control for learning and video-familiarity effects, condition order and video assignment are counterbalanced across participants:
  - `P1`: Condition 1 = `scrubbing` (`VID14`), Condition 2 = `timeline` (`VID22`)
  - `P2`: Condition 1 = `timeline` (`VID14`), Condition 2 = `scrubbing` (`VID22`)
  - `P3`: Condition 1 = `scrubbing` (`VID22`), Condition 2 = `timeline` (`VID14`)
  - `P4`: Condition 1 = `timeline` (`VID22`), Condition 2 = `scrubbing` (`VID14`)

## 4. Test Videos

Two held-out reporting videos from the CholecT50 full-surgery evaluation set (`docs/data/timeline_eval_set.md`) with comparable duration and instrument complexity:

| Video ID | Duration | Clipper share | Scissors share | Irrigator share | Role |
|---|---|---|---|---|---|
| `VID14` | 1,709 s (28m 29s) | 1% | 2% | 17% | Test / Reporting |
| `VID22` | 1,533 s (25m 33s) | 7% | 2% | 15% | Test / Reporting |

Both videos contain brief, high-value critical events (clipping and cutting of the cystic duct/artery) and longer irrigation/coagulation segments.

## 5. Find-Tasks (3 per condition)

In each condition, the participant completes 3 timed find-tasks presented in fixed order:

- **Task T1 (`first_clipper`):** *"Locate the first moment the surgeon introduces and uses the **clipper** on the cystic structure."*
- **Task T2 (`scissors_cut`):** *"Locate the moment the **scissors** are used to transect the clipped structure."*
- **Task T3 (`long_irrigator`):** *"Locate an **irrigator** segment lasting at least 15 seconds during final haemostasis / washout."*

## 6. Procedure & Measures

1. **Briefing (2 min):** Explain the 6 laparoscopic instruments and demonstrate how the video player and colour-coded timeline work on a separate 2-minute fixture clip (`fixture_case_01`).
2. **Condition A (3–4 min):** Participant performs Tasks T1, T2, and T3 on their first assigned video.
3. **Condition B (2–3 min):** Participant switches to the second condition and performs Tasks T1, T2, and T3 on the second assigned video.
4. **Total session length:** ~10 minutes per participant.

### Recorded Metrics (per trial)
- **`time_to_find_s`:** Elapsed time in seconds (measured by stopwatch from task prompt until the participant pauses the video within $\pm 3\text{ s}$ of the ground-truth segment start). Capped at `120 s` (timeout).
- **`success`:** `y` if the participant locates a valid ground-truth segment within 120 seconds, `n` otherwise.

## 7. Analysis Plan

Because $n = 4$ (24 total trials: 12 scrubbing, 12 timeline) is a small pilot sample, we report non-parametric **median time-to-find**, interquartile range (IQR), **task success rate**, and the **speed-up ratio** ($\text{Median}_{\text{scrubbing}} / \text{Median}_{\text{timeline}}$) without claiming formal $p$-value statistical significance.

