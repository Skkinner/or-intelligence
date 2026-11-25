"""Paths and default analysis parameters. Everything can be overridden by env vars."""
from __future__ import annotations

import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def _load_dotenv(path: Path) -> None:
    """Read KEY=value lines from a local .env file (never committed). Real environment variables win."""
    if not path.is_file():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.split("#", 1)[0].strip()
        if "=" in line:
            k, v = line.split("=", 1)
            if k.strip() and v.strip():
                os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


_load_dotenv(ROOT / ".env")
DATA_DIR = Path(os.environ.get("ORI_DATA_DIR", ROOT / "data"))
DB_PATH = Path(os.environ.get("ORI_DB", DATA_DIR / "app.db"))
UPLOAD_DIR = DATA_DIR / "uploads"
ANALYSIS_DIR = DATA_DIR / "analysis"
WEIGHTS_PATH = Path(os.environ.get("ORI_WEIGHTS", ROOT / "models" / "best.pt"))
METRICS_PATH = Path(os.environ.get("ORI_METRICS", ROOT / "models" / "metrics.json"))
DATASETS_YAML = ROOT / "datasets.yaml"
PROCEDURES_YAML = ROOT / "procedures.yaml"
PHASE_MODEL_PATH = Path(os.environ.get("ORI_PHASE_MODEL", ROOT / "models" / "phase_estimator.json"))
PHASE_METRICS_PATH = ROOT / "models" / "phase_metrics.json"

# Defaults for the timeline builder (editable per session in Settings).
DEFAULTS = {
    "conf": 0.25,          # minimum detection confidence
    "smooth": 3,           # majority-filter window, in samples (odd)
    "max_gap": 15.0,       # seconds: gaps shorter than this keep one segment
    "long_use_s": 300.0,   # review flag: continuous use of one instrument
    "switch_window_s": 60.0,
    "switch_count": 6,     # review flag: this many instrument entries inside the window
    "idle_gap_s": 120.0,   # review flag: no instrument for this long (dense sampling only)
    "sample_step_s": 1.0,  # video sampling step for uploads
}

DEFAULT_RETENTION_DAYS = 90


def ensure_dirs() -> None:
    for p in (DATA_DIR, UPLOAD_DIR, ANALYSIS_DIR):
        p.mkdir(parents=True, exist_ok=True)
