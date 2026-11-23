# C3 · Timeline ground truth (CSV)

File: `data/processed/presence/<video_id>.csv` · Producer: **Member A** (2.3.1) · Consumer: **Member C** (4.1.3)

```text
t_sec,grasper,bipolar,hook,scissors,clipper,irrigator
0,1,0,0,0,0,0
1,1,0,1,0,0,0
```

- One row per second (1 fps); `t_sec` is an integer starting at 0.
- One 0/1 column per tool, in the order of `contracts/classes.json`.
- Row count = video duration in seconds (±2 s).
- Source: Cholec80 tool-presence annotations, or held-out m2cai16-tool videos (decision recorded by A in 1.3.1).
- The videos must not be a source of any detection training frame (checked and documented in 2.3.1).
