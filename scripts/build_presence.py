"""WBS 2.3.1 - per-second tool-presence ground truth (contract C3) from CholecInstanceSeg.

The CholecT50 "full" videos in CholecInstanceSeg are annotated on every frame of the
1 fps CholecT50 release, so annotation <prefix>_VIDxx_<n>.json is second n of the video.
A tool is present in a second if that frame has at least one instance of it.

Only videos that are NOT in the detector's training split are used (val -> tuning,
test -> reporting), so no timeline video ever contributed a training frame.

Usage (stdlib only, reads the annotation zip directly):
    py scripts/build_presence.py [path/to/cholecinstanceseg.zip] [out_dir]
"""
import csv
import json
import re
import sys
import zipfile
from collections import defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
CLASSES = [v for _, v in sorted(json.load(open(REPO / "contracts" / "classes.json"))["classes"].items(),
                                key=lambda kv: int(kv[0]))]
ZIP = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.home() / "Downloads" / "cholecinstanceseg.zip"
OUT = Path(sys.argv[2]) if len(sys.argv) > 2 else REPO / "data" / "processed" / "presence"
ROLE = {"val": "tuning", "test": "reporting"}   # train videos are never used here

OUT.mkdir(parents=True, exist_ok=True)
frames = defaultdict(dict)        # (split, video) -> {second: set of tools}
with zipfile.ZipFile(ZIP) as z:
    for name in z.namelist():
        m = re.search(r"/(train|val|test)/(VID\d+)_t50_full/ann_dir/[^/]*_(\d+)\.json$", name)
        if not m or m.group(1) not in ROLE:
            continue
        shapes = json.loads(z.read(name)).get("shapes", [])
        frames[(m.group(1), m.group(2))][int(m.group(3))] = {
            str(s.get("label", "")).strip().lower() for s in shapes}

summary = []
for (split, video), by_sec in sorted(frames.items()):
    n = max(by_sec) + 1
    missing = n - len(by_sec)
    with open(OUT / f"{video}.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["t_sec", *CLASSES])
        for t in range(n):
            tools = by_sec.get(t, set())
            w.writerow([t, *(int(c in tools) for c in CLASSES)])
    share = {c: sum(c in by_sec.get(t, ()) for t in range(n)) / n for c in CLASSES}
    summary.append((video, ROLE[split], split, n, missing, share))
    print(f"{video:6s} {ROLE[split]:9s} ({split}) {n:5d} s  missing seconds: {missing}  "
          + " ".join(f"{c}={share[c]:.0%}" for c in CLASSES))
print("wrote", len(summary), "CSV files to", OUT)
