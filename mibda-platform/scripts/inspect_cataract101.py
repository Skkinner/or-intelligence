"""Look inside the unzipped Cataract-101 folder BEFORE importing, and test the annotation parser on a few files.

  python scripts/inspect_cataract101.py "C:\\data\\cataract-101"

Prints: file counts by type, video/annotation matching, the first lines of a few CSVs, and what the parser makes of them.
If something does not fit, send me this output and I will adjust or_intelligence/data/cataract101.py.
"""
from __future__ import annotations

import argparse
import collections
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from or_intelligence.data import cataract101  # noqa: E402


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("root")
    ap.add_argument("--n", type=int, default=3, help="how many files to preview")
    a = ap.parse_args()
    root = Path(a.root)
    files = [p for p in root.rglob("*") if p.is_file()]
    print(f"{len(files)} files under {root}")
    print("by extension:", dict(collections.Counter(p.suffix.lower() or '(none)' for p in files).most_common(8)))
    print("top-level entries:", sorted(p.name for p in root.iterdir())[:15])

    sc = cataract101.scan(root)
    print(f"\nvideos: {len(sc.videos)}  matched to a same-name CSV: {len(sc.matched)}  unmatched: {len(sc.unmatched)}")
    print("other CSV files:", [c.name for c in sc.other_csvs][:8])

    if sc.combined:
        print(f"\ncombined annotations.csv: {len(sc.combined)} videos with phase starts")
    previews = list(sc.matched.items())[: a.n] or [(None, c) for c in sc.other_csvs[: a.n]]
    for video, csv_path in previews:
        print(f"\n--- {csv_path.relative_to(root)}" + (f"  (video: {video.name})" if video else ""))
        for line in csv_path.read_text(encoding="utf-8-sig", errors="replace").splitlines()[:8]:
            print("   ", line)
        try:
            cps = (sc.combined or {}).get(video.stem.lower()) if video and sc.combined else cataract101.parse_phase_csv(csv_path)
            print(f"    parsed: {len(cps)} change points, phases seen (0-based): {sorted({p for _, p in cps})}")
            print(f"    first change points: {cps[:6]}")
        except cataract101.AnnotationFormatError as e:
            print(f"    NOT PARSED: {e}")
        if video:
            try:
                fps, n = cataract101.video_info(video)
                print(f"    video: {fps:.2f} fps, {n} frames, {n / fps / 60:.1f} min")
            except ValueError as e:
                print(f"    video problem: {e}")


if __name__ == "__main__":
    main()
