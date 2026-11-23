"""Download raw datasets reproducibly.

WBS 2.1.1 · Owner: Member A · Branch: feature/member-a-2.1.1-download
Depends on: 1.3.1 (licence decision), 1.2.1 (repo scaffold)

Usage:
    python -m src.data.download --dataset m2cai16 --out data/raw/
    python -m src.data.download --dataset cholec80 --out data/raw/   # may only verify a manual copy

Inputs : dataset URLs and checksums from configs/data.yaml (licences in docs/data/LICENSES_AND_ETHICS.md)
Outputs: data/raw/m2cai16_tool_locations/, data/raw/cholec80/ (gitignored, never committed)

Acceptance (from the WBS):
    - `python -m src.data.verify` passes on a clean machine after download.
    - Nothing under data/ is tracked by Git.
"""

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path

import yaml

CONFIG_PATH = Path("configs/data.yaml")


def load_config(path: Path = CONFIG_PATH) -> dict:
    with open(path, encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def sha256(path: Path, chunk: int = 1 << 20) -> str:
    """SHA-256 of a file; record results in configs/data.yaml under `checksums:`."""
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        while block := fh.read(chunk):
            h.update(block)
    return h.hexdigest()


def download_dataset(name: str, out_dir: Path) -> Path:
    """Download (or locate a manual copy of) dataset ``name`` into ``out_dir`` and return its folder.

    TODO(A, 2.1.1):
      1. Read the dataset entry from configs/data.yaml (url, archive name, sha256, manual: bool).
      2. If `manual: true` (e.g. Cholec80 licence), do not download: print instructions and only
         check the expected folder exists.
      3. Otherwise stream-download with requests + tqdm, verify sha256, extract to out_dir/<name>/.
      4. Skip work if the extracted folder already exists and the checksum matches.
    """
    raise NotImplementedError("WBS 2.1.1 (Member A): implement dataset download")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--dataset", required=True, choices=["m2cai16", "cholec80"])
    parser.add_argument("--out", type=Path, default=Path("data/raw"))
    args = parser.parse_args()
    folder = download_dataset(args.dataset, args.out)
    print(f"Dataset ready at {folder}")


if __name__ == "__main__":
    main()
