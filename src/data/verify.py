"""Verify downloaded raw datasets (counts + checksums). Fails loudly on mismatch.

WBS 2.1.1 · Owner: Member A

Usage:
    python -m src.data.verify            # checks every dataset listed in configs/data.yaml

TODO(A, 2.1.1):
  - Count images, VOC XML files, videos and tool-annotation files per dataset.
  - Compare with `expected_counts` in configs/data.yaml (fill them from the dataset documentation).
  - Exit with code 1 and a clear message on any mismatch.
"""

from __future__ import annotations

import sys
from pathlib import Path

from src.data.download import load_config


def count_files(folder: Path, pattern: str) -> int:
    return sum(1 for _ in folder.rglob(pattern)) if folder.exists() else 0


def verify(config: dict) -> list[str]:
    """Return a list of human-readable problems (empty list = everything OK)."""
    raise NotImplementedError("WBS 2.1.1 (Member A): implement dataset verification")


def main() -> int:
    problems = verify(load_config())
    for p in problems:
        print(f"[FAIL] {p}")
    if problems:
        return 1
    print("[OK] all datasets verified")
    return 0


if __name__ == "__main__":
    sys.exit(main())
