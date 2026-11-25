"""Plain data containers. Boxes are normalized (0..1), top-left x/y plus width/height."""
from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path


@dataclass
class Box:
    instrument: int
    x: float
    y: float
    w: float
    h: float
    conf: float = 1.0
    verb: int | None = None
    target: int | None = None
    triplet: int | None = None


@dataclass
class FrameResult:
    t: float                      # seconds from the start of the case
    image: str | None = None      # file name (frames cases) or None (video cases)
    boxes: list[Box] = field(default_factory=list)
    phase: int | None = None
    phase_conf: float | None = None   # estimator confidence in `phase` (None for ground-truth labels)


@dataclass
class CaseAnalysis:
    video_id: str
    source: str                   # "annotations" (ground-truth replay) or "model"
    duration: float
    frames: list[FrameResult]
    detector: str = ""
    params: dict = field(default_factory=dict)
    procedure: str = "lap-chole"  # procedure id (procedures.yaml); older files without it are cholecystectomy

    @property
    def dense(self) -> bool:
        """True when frames were sampled at a regular step (so gaps carry meaning)."""
        return bool(self.params.get("dense", True))

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: dict) -> "CaseAnalysis":
        frames = [
            FrameResult(
                t=f["t"], image=f.get("image"), phase=f.get("phase"), phase_conf=f.get("phase_conf"),
                boxes=[Box(**b) for b in f.get("boxes", [])],
            )
            for f in d["frames"]
        ]
        return cls(
            video_id=d["video_id"], source=d["source"], duration=d["duration"],
            frames=frames, detector=d.get("detector", ""), params=d.get("params", {}),
            procedure=d.get("procedure", "lap-chole"),
        )

    def save(self, path: str | Path) -> None:
        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(self.to_dict()), encoding="utf-8")

    @classmethod
    def load(cls, path: str | Path) -> "CaseAnalysis":
        return cls.from_dict(json.loads(Path(path).read_text(encoding="utf-8")))
