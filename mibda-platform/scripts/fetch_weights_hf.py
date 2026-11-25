"""Download the detector weights from a (private) Hugging Face model repository at startup.

  ORI_WEIGHTS_REPO   e.g. "your-name/mibda-weights" (a model repo holding best.pt)
  HF_TOKEN           read token for that repo (a Space secret; never commit it)

Does nothing when ORI_WEIGHTS_REPO is not set or the weights file already exists.
"""
from __future__ import annotations

import os
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from or_intelligence import config  # noqa: E402


def main() -> None:
    repo = os.environ.get("ORI_WEIGHTS_REPO", "").strip()
    if not repo:
        return
    dest = config.WEIGHTS_PATH
    if dest.exists():
        print(f"weights: {dest} already present")
        return
    from huggingface_hub import hf_hub_download

    path = hf_hub_download(repo_id=repo, filename="best.pt", token=os.environ.get("HF_TOKEN") or None)
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(path, dest)
    print(f"weights: downloaded best.pt from {repo}")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:  # the app still starts; Live analysis then reports that the detector is missing
        print(f"weights: download failed ({type(e).__name__}: {e})")
