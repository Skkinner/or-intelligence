# Usability Pilot Results: Manual Scrubbing vs. OR Intelligence Timeline (Owner: Member A, WBS 6.2.1)

> **Scope note:** This is a **pilot usability study** ($n = 4$ participants, 24 timed find-trials across two 25–28 minute held-out laparoscopic cholecystectomy videos, `VID14` and `VID22`). Because $n$ is small, we report medians, interquartile ranges (IQR), and task completion rates without formal hypothesis-testing claims. Raw anonymous trial data is stored in `docs/usability/results.csv` following `docs/usability/PROTOCOL.md`.

## 1. Overall Summary

| Condition | Trials | Median time-to-find (s) | IQR (Q1–Q3, s) | Mean time-to-find (s) | Success rate (within 120 s) |
|---|---|---|---|---|---|
| **Manual scrubbing** | 12 | **66.2 s** | 50.2 – 86.9 s | 70.2 s | **91.7%** (11 / 12) |
| **OR Intelligence timeline** | 12 | **8.8 s** | 7.6 – 10.0 s | 8.8 s | **100.0%** (12 / 12) |

- **Speed-up ratio ($\text{Median}_{\text{scrubbing}} / \text{Median}_{\text{timeline}}$):** **`7.57×` faster** (`66.2 s` vs. `8.75 s`, saving **57.5 seconds** per lookup, or an **86.8% reduction** in search time).

## 2. Breakdown by Find-Task

Rare instruments (`clipper` and `scissors`, present in only 1–7% of surgery seconds) are the hardest to locate by manual scrubbing because random seeks along a 28-minute seek bar frequently step right over a 5–15 second action.

| Task | Instrument rarity in video | Manual scrubbing median (s) | Timeline median (s) | Speed-up ratio |
|---|---|---|---|---|
| **T1 (`first_clipper`)** | 1–7% of frames | 66.2 s | 8.6 s | **7.74×** |
| **T2 (`scissors_cut`)** | 2% of frames | 91.4 s (1 timeout at 120 s) | 10.3 s | **8.91×** |
| **T3 (`long_irrigator`)** | 15–17% of frames | 47.9 s | 7.3 s | **6.56×** |

## 3. Visual Comparison Chart (Median Time-to-Find)

```text
Task / Condition                 Median Time-to-Find (seconds)
──────────────────────────────────────────────────────────────────────────────────
T1: First Clipper Use
  Manual Scrubbing  [█████████████████████████████████░░░░░░░░░░░░░░░░░]  66.2 s
  OR Timeline       [████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░]   8.6 s

T2: Scissors Transection
  Manual Scrubbing  [██████████████████████████████████████████████░░░░]  91.4 s
  OR Timeline       [█████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░]  10.3 s

T3: Long Irrigation (>=15 s)
  Manual Scrubbing  [████████████████████████░░░░░░░░░░░░░░░░░░░░░░░░░░]  47.9 s
  OR Timeline       [████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░]   7.3 s

Overall (All 12 Trials per Condition)
  Manual Scrubbing  [█████████████████████████████████░░░░░░░░░░░░░░░░░]  66.2 s
  OR Timeline       [████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░]   8.8 s
──────────────────────────────────────────────────────────────────────────────────
                     0s        20s       40s       60s       80s      100s
```

## 4. Per-Participant Summary

| Participant | Order | Scrubbing Video | Scrubbing Median (s) | Timeline Video | Timeline Median (s) | Individual Ratio |
|---|---|---|---|---|---|---|
| `P1` | Scrubbing → Timeline | `VID14` | 68.4 s | `VID22` | 8.2 s | 8.34× |
| `P2` | Timeline → Scrubbing | `VID22` | 58.0 s | `VID14` | 9.8 s | 5.92× |
| `P3` | Scrubbing → Timeline | `VID22` | 64.0 s | `VID14` | 7.9 s | 8.10× |
| `P4` | Timeline → Scrubbing | `VID14` | 74.6 s | `VID22` | 8.9 s | 8.38× |

Every participant found target moments **5.9× to 8.4× faster** with the colour-coded instrument timeline regardless of whether they used the timeline first or second.

## 5. Qualitative Observations

1. **Eliminating blind scrubbing on rare events:** During manual scrubbing, participants relied on anatomical heuristics (e.g., jumping to the middle third of the video to look for Calot's triangle dissection), yet still needed 60–95 seconds of fine back-and-forth scrubbing to catch the brief `scissors` cut (`P3` timed out at 120 s on `VID22`). With the OR Intelligence timeline, participants scanned the orange (`clipper`) and green (`scissors`) lanes visually and clicked directly onto the bar in under 11 seconds.
2. **Distinguishing long vs. short episodes:** For Task T3 (`long_irrigator`), the timeline bar width immediately encoded duration, allowing participants to ignore short 2–3 second flushes and click the widest teal bar (`6.8–8.6 s`).
3. **Bilingual / RTL ergonomics:** Keeping the timeline time axis left-to-right (`direction: ltr` in `web/src/styles/rtl.css`) while mirroring the surrounding Arabic interface prevented any confusion with the HTML5 video scrubber.

