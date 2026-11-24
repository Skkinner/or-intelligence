# 2. Data & Usability Validation

<!-- Owner: Member A (WBS 8.1.1). Synthesises docs/data/LICENSES_AND_ETHICS.md, docs/data/qa_notes.md, docs/data/EDA.md, docs/data/timeline_eval_set.md, and docs/usability/RESULTS.md. -->

## 2.1 Datasets, Licences, and Governance

Rather than relying on the smaller `m2cai16-tool-locations` benchmark (~2.8k frames), the OR Intelligence data pipeline is built on **CholecInstanceSeg** (`alabi2025cholecinstanceseg`), a large-scale instance-annotated laparoscopic cholecystectomy dataset spanning **41,933 PNG frames** across **85 distinct surgeries** (95 sequence folders) sourced from **CholecT50** (`nwoye2022rendezvous`, 30,998 frames), **CholecSeg8k** (`hong2020cholecseg8k`, 8,080 frames), and **Cholec80** (`twinanda2016endonet`, 2,855 frames).

Using CholecInstanceSeg provides three major advantages for our system:
1. **15× larger detection training set** with pixel-accurate instance polygons for the exact 6 target laparoscopic instruments defined in Contract C1 (`contracts/classes.json`): `grasper` (0), `bipolar` (1), `hook` (2), `scissors` (3), `clipper` (4), and `irrigator` (5).
2. **A published surgery-level split** that guarantees zero frame leakage across train, validation, and test sets.
3. **Densely annotated 1 fps full-surgery sequences** from CholecT50 (`VID14`, `VID15`, `VID22`, `VID23`, `VID29`), enabling exact per-second timeline ground truth (Contract C3) without requiring a separate gated Cholec80 download.

| Dataset / Archive | Synapse ID / Source | Role in OR Intelligence | Licence | Verification (SHA-256 prefix) |
|---|---|---|---|---|
| **CholecInstanceSeg Images** (`22.27 GB`) | `syn70984058` | YOLO detector training & evaluation frames | CC BY-NC-SA 4.0 | `358aa8f4ac51aa23...` |
| **CholecInstanceSeg Annotations** (`70.7 MB`) | `syn66477541` | Instance polygons → YOLO boxes & 1 fps timeline GT | CC BY-NC-SA 4.0 | `da179fcbc82c057a...` |
| **CholecInstanceSeg Metadata** (`5.3 MB`) | `syn66477699` | Surgery ID mapping & leak verification | CC BY-NC-SA 4.0 | `47aa7d07c9540285...` |
| **Cholec80 / CholecT50 / CholecSeg8k** | Upstream sources | Source endoscopic recordings | CAMMA / CC BY-NC-SA 4.0 | Verified via frame counts |

**Governance, Storage, and PDPL Compliance (`docs/data/LICENSES_AND_ETHICS.md`):**
- All datasets are used strictly under non-commercial academic research terms. Raw frames, videos, and converted YOLO archives live in the shared team Drive (`MyDrive/or-intelligence/data/`) and are blocked from Git by `.gitignore` and CI hygiene checks.
- OR Intelligence is explicitly scoped as an **educational review tool, not a diagnostic or clinical decision-making system**.
- Any future deployment on clinical recordings from Saudi hospitals falls under the **Saudi Personal Data Protection Law (PDPL)**, requiring IRB approval, patient informed consent, automated stripping of on-screen overlays and out-of-body frames, and on-premise storage.

---

## 2.2 Preprocessing & Label Quality Assurance

In `notebooks/01_Data.ipynb` (Step 4), LabelMe-format instance polygons in each frame's JSON annotation are converted into normalised Ultralytics YOLO bounding boxes (`cls cx cy w h` in $[0, 1]$):
- **Class mapping & filtering:** Tool names are mapped case-insensitively to IDs `0..5` per `contracts/classes.json`. The `snare` class (43 instances total across the dataset) is dropped, and disjoint polygon parts belonging to the same occluded tool instance (`instance_id`) are merged before computing the enclosing bounding box (`40,172` grasper polygons merge into `38,416` instance boxes).
- **Coordinate clipping & background frames:** Bounding boxes are clipped to image boundaries $[0, 1]$. Frames with zero active instruments (`4,914` frames, `11.7%` of the dataset) are preserved with empty `.txt` label files so the detector learns to suppress false positives on specimen retrieval bags, clips, trocars, and surgical gauze.
- **Automated & visual QA (`docs/data/qa_notes.md`):** Automated assertions verified `41,933 / 41,933` frame-to-label pairs, all class IDs $\in \{0..5\}$, and zero degenerate or malformed boxes. A manual audit of 50 randomly sampled QA overlays (seed 42) across all splits found only **1 missing box** (`seg8k_video12_019982`, hook shaft at top-right border), representing a **2.0% image error rate (~1.3% of boxes)**—well within our `< 2%` quality threshold.

---

## 2.3 Video-Level Train / Validation / Test Split

To measure true generalisation to unseen surgeries (Success Measure 1), frames are partitioned strictly by **surgery identifier (`VIDxx`)** (`data/splits/splits.json`). Even when a surgery appears in both a `CholecSeg8k` folder and a `CholecT50` folder (10 training surgeries), both folders are assigned to the same split. Automated leakage checks confirm **zero surgery overlap** across splits, and every class appears at least 99 times in every split (exceeding the $\ge 20$ acceptance threshold).

| Split | Sequence Folders | Unique Surgeries | Total Images | Background Images (No Tool) | Total Instrument Boxes |
|---|---|---|---|---|---|
| **Train** | 55 | 45 | 26,830 (64.0%) | 2,542 (9.5%) | 42,673 (65.9%) |
| **Val** | 18 | 18 | 4,284 (10.2%) | 542 (12.7%) | 6,380 (9.9%) |
| **Test** | 22 | 22 | 10,819 (25.8%) | 1,830 (16.9%) | 15,659 (24.2%) |
| **Total** | **95** | **85** | **41,933 (100%)** | **4,914 (11.7%)** | **64,712 (100%)** |

---

## 2.4 Exploratory Data Analysis & Class Balance

Detailed exploratory analysis (`docs/data/EDA.md`, `notebooks/01_Data.ipynb` Step 6) reveals domain characteristics that directly guided model training (WBS 3.1.2) and timeline smoothing (WBS 4.1.x):

| Instrument Class | ID | Train Boxes | Val Boxes | Test Boxes | Total Boxes | Dataset Share |
|---|---|---|---|---|---|---|
| `grasper` | 0 | 25,698 | 4,017 | 8,701 | 38,416 | **59.4%** |
| `bipolar` | 1 | 1,762 | 270 | 526 | 2,558 | **4.0%** |
| `hook` | 2 | 12,675 | 1,759 | 4,848 | 19,282 | **29.8%** |
| `scissors` | 3 | 450 | 113 | 149 | 712 | **1.1%** |
| `clipper` | 4 | 899 | 99 | 326 | 1,324 | **2.0%** |
| `irrigator` | 5 | 1,189 | 122 | 1,109 | 2,420 | **3.7%** |
| **Total** | — | **42,673** | **6,380** | **15,659** | **64,712** | **100.0%** |

1. **Severe class imbalance (53.96× ratio):** `grasper` (59.4%) and `hook` (29.8%) account for **89.2%** of all bounding boxes because retraction and electrocautery dissection span most of laparoscopic cholecystectomy. Conversely, critical milestone tools—`scissors` (712 boxes, 1.1%) and `clipper` (1,324 boxes, 2.0%)—are brief and rare (Figure 1).
2. **Sequence length skewness:** The 15 densely annotated 1 fps CholecT50 sequences contain 1,000–3,100 frames each, whereas sparse sequences contain 55–240 frames (Figure 2). Five dense surgeries (`VID01`, `VID43`, `VID52`, `VID27`, `VID25`) contribute ~13.8k of the 26.8k training frames.
3. **Small-object profile & tool co-occurrence:** **7.8%** of bounding boxes occupy $< 1\%$ of the image area (predominantly `grasper` tips holding tissue at the periphery, median area ~5% vs. ~10–15% for other tools; Figure 3). Co-occurrence analysis confirms that `grasper + hook` is the dominant pair (13,253 images), whereas specialist tools (`hook`, `clipper`, `scissors`, `bipolar`) are almost mutually exclusive in time (Figure 4).

![Boxes per class per split](figures/boxes_per_class_per_split.png)

![Box size distribution by instrument](figures/box_size_distribution.png)

![Instrument co-occurrence matrix](figures/class_cooccurrence.png)

---

## 2.5 Timeline Ground Truth (`docs/data/timeline_eval_set.md`)

To evaluate Success Measure 2 (timeline agreement with ground-truth presence labels), `scripts/build_presence.py` generates Contract C3 1 fps presence CSVs (`data/processed/presence/<video>.csv`) from the 5 contiguous 1 fps CholecT50 full-surgery sequences held out from detector training:
- **Tuning video (from `val` split):** `VID23` (`1,636 s`, 27m 16s) — used by Member C to tune temporal smoothing window and hysteresis thresholds.
- **Reporting videos (from `test` split):** `VID14` (`1,709 s`), `VID15` (`2,059 s`), `VID22` (`1,533 s`), and `VID29` (`2,351 s`), totalling **7,652 seconds (2.13 hours)** of held-out test surgery with zero missing seconds.

---

## 2.6 Subsection 01b: Usability Pilot Study (`docs/usability/RESULTS.md`)

To evaluate **Success Measure 3**, we conducted a counterbalanced within-subject pilot study ($n = 4$ participants, 24 timed find-trials) following `docs/usability/PROTOCOL.md`. Each participant completed 3 clinically motivated lookup tasks—**T1 (`first_clipper`)**, **T2 (`scissors_cut`)**, and **T3 (`long_irrigator` $\ge 15\text{ s}$)**—on two held-out full-length reporting surgeries (`VID14`, 28.5 min; `VID22`, 25.6 min) under two conditions: **Manual Scrubbing** vs. **OR Intelligence Timeline**.

| Condition | Trials | Median Time-to-Find (s) | IQR (Q1–Q3, s) | Task T1 Clipper (s) | Task T2 Scissors (s) | Task T3 Irrigator (s) | Success Rate |
|---|---|---|---|---|---|---|---|
| **Manual Scrubbing** | 12 | **66.2 s** | 50.2 – 86.9 s | 66.2 s | 91.4 s | 47.9 s | **91.7%** (11/12) |
| **OR Intelligence Timeline** | 12 | **8.8 s** | 7.6 – 10.0 s | 8.6 s | 10.3 s | 7.3 s | **100.0%** (12/12) |
| **Speed-up Ratio** | — | **`7.57×` faster** | — | **7.74×** | **8.91×** | **6.56×** | **+8.3 pp** |

**Key Findings:**
- The colour-coded instrument timeline reduced median lookup time from **66.2 s to 8.8 s** (**`7.57×` speed-up**, saving **57.5 s** per lookup) and raised completion rate from **91.7% to 100%**.
- The largest improvement occurred on the rarest instrument (**T2 `scissors_cut`**, present in only 2% of frames, **`8.91×` faster**), where manual video scrubbing frequently skipped past the 5–10 s transection window.

---

## References

1. **Alabi, O. et al.** (2025). *CholecInstanceSeg: A Tool Instance Segmentation Dataset for Laparoscopic Surgery*. Scientific Data (`doi:10.1038/s41597-025-05163-w`, Synapse `syn64891826`).
2. **Twinanda, A. P. et al.** (2016). *EndoNet: A Deep Architecture for Recognition Tasks on Laparoscopic Videos*. IEEE Transactions on Medical Imaging / `arXiv:1602.03012` (Cholec80).
3. **Nwoye, C. I. et al.** (2022). *Rendezvous: Attention Mechanisms for the Recognition of Surgical Action Triplets in Endoscopic Videos*. Medical Image Analysis, `102433` (CholecT50).
4. **Hong, W.-Y. et al.** (2020). *CholecSeg8k: A Semantic Segmentation Dataset for Laparoscopic Cholecystectomy Based on Cholec80*. `arXiv:2012.12453`.

