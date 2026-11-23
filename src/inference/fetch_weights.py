"""Download and verify the released detector weights into models/weights/.

WBS 3.3.2 · Owner: Member B · Used by: Member D's run scripts (7.1.1)

Usage:
    python -m src.inference.fetch_weights            # -> models/weights/best.pt (sha256 checked)

TODO(B, 3.3.2):
  - After creating GitHub Release `model-v1`, fill RELEASE_URL and SHA256 below.
  - Download with urllib (no extra deps), verify sha256, skip if the file already matches.
  - For a private repository, the release asset needs an authenticated download (e.g. `gh release download
    model-v1 -p best.pt -D models/weights`); document whichever the team uses in src/inference/README.md.
"""

from __future__ import annotations

import hashlib
import sys
from pathlib import Path

RELEASE_URL = ""   # TODO(B, 3.3.2): e.g. https://github.com/<owner>/or-intelligence/releases/download/model-v1/best.pt
SHA256 = ""        # TODO(B, 3.3.2)
TARGET = Path("models/weights/best.pt")


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        while block := fh.read(1 << 20):
            h.update(block)
    return h.hexdigest()


def fetch(target: Path = TARGET) -> Path:
    if target.exists() and SHA256 and sha256(target) == SHA256:
        print(f"[OK] {target} already present and verified")
        return target
    raise NotImplementedError("WBS 3.3.2 (Member B): implement weights download + verification")


if __name__ == "__main__":
    fetch()
    sys.exit(0)
