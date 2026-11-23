# Dataset licences & ethics (Owner: Member A, WBS 1.3.1)

## Decision

The project uses **CholecInstanceSeg** (instance-segmentation masks for 6+1 tools on frames from Cholec80,
CholecT50 and CholecSeg8k) instead of m2cai16-tool-locations. It gives far more labelled frames (41,933 vs ~2.8k),
the same 6 instruments as `contracts/classes.json`, a published video-level split, and fully annotated 1 fps videos
that double as timeline ground truth (so no separate Cholec80 access is needed). m2cai16 is no longer used.

## Datasets

| Dataset | Role here | Licence | Access | Allowed use | Citation key |
|---|---|---|---|---|---|
| CholecInstanceSeg | detector training/eval (2.2.x), timeline GT (2.3.1) | CC BY-NC-SA 4.0 (paper licence on arXiv; confirm the Synapse page's conditions of use before release) | Synapse `syn64891826` (DOI 10.7303/syn64891826.1); free account + accepting the terms | Non-commercial research/education; attribution; derivatives share-alike; no redistribution of frames outside the team | `alabi2025cholecinstanceseg` |
| Cholec80 (source frames) | origin of the images (not downloaded separately) | CAMMA non-commercial research licence (CC BY-NC-SA 4.0) | via CholecInstanceSeg only | as above | `twinanda2016endonet` |
| CholecT50 (source frames) | origin of the images and the 1 fps full videos | CAMMA non-commercial research licence (CC BY-NC-SA 4.0) | via CholecInstanceSeg only | as above | `nwoye2022rendezvous` |
| CholecSeg8k (source frames) | origin of some images | CC BY-NC-SA 4.0 | via CholecInstanceSeg only | as above | `hong2020cholecseg8k` |

Allowed for this project: academic course project, internal team use, publishing aggregate metrics and a few
illustrative frames in the report/slides with attribution. **Not allowed:** commercial use, putting frames, videos or
the dataset (or the YOLO conversion) in the Git repo or any public place.

## Download & verification (WBS 2.1.1)

Downloaded 2026-11-23 from Synapse with `scripts/download_synapse.py` (resumable, MD5-checked) / `notebooks/00_Download_CholecInstanceSeg.ipynb`.

| File | Synapse ID | Size (bytes) | SHA-256 |
|---|---|---|---|
| `cholecinstance_seg_reference_image_set.zip` | syn70984058 | 22,274,378,866 | `358aa8f4ac51aa23b9e510419bf7066e7d7242e3227b62ea16af730ead78b74d` |
| `cholecinstanceseg.zip` (annotations) | syn66477541 | 70,703,958 | `da179fcbc82c057ac61c852c67fdff2e9cb2413d524b501b094f7a36ec1de2f0` |
| `cholecinstanceseg_metadata.csv` | syn66477699 | 5,337,979 | `47aa7d07c9540285721937d316eed0b390090f8f345eabedec3e67bbd8c0401a` |

Counts (printed by `01_Data.ipynb` step 3) vs. the paper (arXiv:2406.16039, recommended split):

| Split | Sequences | PNG frames | Annotation JSONs | Paper |
|---|---|---|---|---|
| train | 55 | 26,830 | 26,830 | 55 / 26,830 |
| val | 18 | 4,284 | 4,284 | 18 / 4,284 |
| test | 22 | 10,819 | 10,819 | 22 / 10,819 |
| **total** | 95 folders (85 surgeries) | 41,933 | 41,933 | 41,933 |

All counts match. Every annotation has its frame. No surgery number (`VIDxx`) appears in more than one split.
Sources (metadata CSV): CholecT50 30,998 · CholecSeg8k 8,080 · Cholec80 2,855 frames.

## Timeline ground-truth decision (told Member C)

- [x] ~~Cholec80~~ / ~~m2cai16-tool~~ → **CholecT50 full videos inside CholecInstanceSeg**
- Decision: per-second presence from the instance labels of the 5 fully annotated (1 fps) CholecT50 videos that are
  *not* in the training split: VID23 (val → tuning), VID14, VID15, VID22, VID29 (test → reporting). See `timeline_eval_set.md`.
- Reason: no team member has Cholec80 access; these videos are annotated on every second, come with the dataset we
  already use, and are disjoint from detector training by construction.

## Storage rule

- `data/` is gitignored. **No raw video, frames or weights are ever committed to Git.** CI blocks them.
- Team copies live on the shared drive: `MyDrive/or-intelligence/data/cholecinstanceseg/` (raw zips) and
  `MyDrive/or-intelligence/data/yolo_dataset.zip` (converted). Share the folder with the team; do not re-download.

## Scope statement

OR Intelligence is an **educational review tool, not a diagnostic or clinical decision-making system**. A human instructor always makes the final judgment.

## Privacy (PDPL)

The public datasets are de-identified endoscopic video released for research. Any future use of **real patient
recordings** (e.g. from a Saudi hospital) falls under the Saudi Personal Data Protection Law (PDPL): it needs
written informed consent or an approved legal basis, ethics (IRB) approval, removal of identifiers (on-screen text,
timestamps, out-of-body frames that show faces/staff), storage inside approved infrastructure, and must never be put in this repo.

## BibTeX

```bibtex
@article{alabi2025cholecinstanceseg,
  title   = {CholecInstanceSeg: A Tool Instance Segmentation Dataset for Laparoscopic Surgery},
  author  = {Alabi, Oluwatosin and Toe, Ko Ko Zayar and Zhou, Zijian and Budd, Charlie and Raison, Nicholas and Shi, Miaojing and Vercauteren, Tom},
  journal = {Scientific Data},
  year    = {2025},
  doi     = {10.1038/s41597-025-05163-w},
  note    = {arXiv:2406.16039. Dataset: Synapse, doi:10.7303/syn64891826.1}
}

@article{twinanda2016endonet,
  title   = {EndoNet: A Deep Architecture for Recognition Tasks on Laparoscopic Videos},
  author  = {Twinanda, Andru P. and Shehata, Sherif and Mutter, Didier and Marescaux, Jacques and de Mathelin, Michel and Padoy, Nicolas},
  journal = {arXiv preprint arXiv:1602.03012},
  year    = {2016}
}

@article{nwoye2022rendezvous,
  title   = {Rendezvous: Attention Mechanisms for the Recognition of Surgical Action Triplets in Endoscopic Videos},
  author  = {Nwoye, Chinedu Innocent and Yu, Tong and Gonzalez, Cristians and Seeliger, Barbara and Mascagni, Pietro and Mutter, Didier and Marescaux, Jacques and Padoy, Nicolas},
  journal = {Medical Image Analysis},
  pages   = {102433},
  year    = {2022},
  doi     = {10.1016/j.media.2022.102433}
}

@article{hong2020cholecseg8k,
  title   = {CholecSeg8k: A Semantic Segmentation Dataset for Laparoscopic Cholecystectomy Based on Cholec80},
  author  = {Hong, W.-Y. and Kao, C.-L. and Kuo, Y.-H. and Wang, J.-R. and Chang, W.-L. and Shih, C.-S.},
  journal = {arXiv preprint arXiv:2012.12453},
  year    = {2020}
}
```

EndoNet was published in IEEE Transactions on Medical Imaging (2017); swap in that venue if your report style needs the journal version.
