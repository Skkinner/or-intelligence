"""Interval builder and per-case statistics -> timeline JSON (contract C5).

WBS 4.1.2 · Owner: Member C · Branch: feature/member-c-4.1.2-builder
Depends on: 4.1.1 (smoothing.py)

CLI:
    python -m src.timeline.builder detections.jsonl timeline.json [--video-id abc123]

Definitions (document final choices here — acceptance criterion):
    - Tool switch: a change in the *set* of active tools between consecutive samples after smoothing.
      TODO(C, 4.1.2): confirm/adjust and keep this docstring in sync.
    - Segments with gaps < merge_gap_s are merged; segments shorter than min_segment_s are dropped.

Acceptance:
    - Output validates against contracts/timeline.schema.json.
    - Hand-computed stats for the fixture match the module output.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import yaml

from src.common.contracts import iter_jsonl, validate

TIMELINE_CONFIG = Path("configs/timeline.yaml")


def load_params(path: Path = TIMELINE_CONFIG) -> dict:
    with open(path, encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def build_timeline(dets_path: str, video_id: str, params: dict) -> dict:
    """Build the contract-C5 timeline dict for one video.

    TODO(C, 4.1.2):
      1. records = list(iter_jsonl(dets_path)); infer sample_fps and duration_s.
      2. times, m = smoothing.presence_matrix(records, params["conf"]);
         present = smoothing.smooth(m, fps, params["window_s"], params["method"], params["on"], params["off"])
      3. Per tool: boolean runs -> [start, end] segments; merge gaps; drop short; mean_conf from m.
      4. stats = {total_s, switches, per_tool_s, per_tool_segments}.
      5. validate(result, "timeline") before returning.
    """
    _ = (iter_jsonl, validate)
    raise NotImplementedError("WBS 4.1.2 (Member C)")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("detections", type=Path)
    parser.add_argument("out", type=Path)
    parser.add_argument("--video-id", default=None)
    args = parser.parse_args()
    timeline = build_timeline(str(args.detections), args.video_id or args.detections.stem, load_params())
    args.out.write_text(json.dumps(timeline, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
