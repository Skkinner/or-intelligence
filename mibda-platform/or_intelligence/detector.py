"""Detectors: a real YOLO model, plus a clearly-labelled annotation replay for demos."""
from __future__ import annotations

from pathlib import Path
from typing import Protocol

import numpy as np

from .constants import INSTRUMENTS, N_INSTRUMENTS
from .models import Box


def class_map(model_names: dict | list | None) -> dict[int, int]:
    """Model class id -> platform instrument index, matched BY NAME when the model carries names (so a retrained model
    with a different class order still gets the right labels); identity when it has none or only generic ones."""
    if not model_names:
        return {i: i for i in range(N_INSTRUMENTS)}
    names = dict(enumerate(model_names)) if isinstance(model_names, (list, tuple)) else dict(model_names)
    wanted = {n.lower(): i for i, n in enumerate(INSTRUMENTS)}
    by_name = {int(k): wanted[str(v).strip().lower()] for k, v in names.items() if str(v).strip().lower() in wanted}
    return by_name if by_name else {i: i for i in range(N_INSTRUMENTS)}


class Detector(Protocol):
    name: str

    def detect(self, frame_bgr: np.ndarray) -> list[Box]: ...


class YoloDetector:
    """Wraps an Ultralytics YOLO model trained with `scripts/train.py`.

    The model's class ids must follow constants.INSTRUMENTS order.
    """

    def __init__(self, weights: str | Path, conf: float = 0.25, imgsz: int = 640, device: str | None = None):
        try:
            from ultralytics import YOLO
        except ImportError as e:  # pragma: no cover
            raise RuntimeError("Install ultralytics (requirements-train.txt) to run the model.") from e
        self.weights = Path(weights)
        if not self.weights.exists():
            raise FileNotFoundError(f"Weights not found: {self.weights}")
        self.model = YOLO(str(self.weights))
        self.conf = conf
        self.imgsz = imgsz
        self.device = device
        self.name = f"yolo:{self.weights.name}"
        self.class_names = dict(getattr(self.model, "names", {}) or {})
        self.id_map = class_map(self.class_names)          # class id -> instrument index (by name)

    def detect(self, frame_bgr: np.ndarray) -> list[Box]:
        res = self.model.predict(
            frame_bgr, conf=self.conf, imgsz=self.imgsz, device=self.device, verbose=False
        )[0]
        h, w = frame_bgr.shape[:2]
        out: list[Box] = []
        for xyxy, c, k in zip(res.boxes.xyxy.cpu().numpy(), res.boxes.conf.cpu().numpy(), res.boxes.cls.cpu().numpy()):
            k = self.id_map.get(int(k), -1)
            if not 0 <= k < N_INSTRUMENTS:
                continue
            x1, y1, x2, y2 = xyxy
            out.append(Box(k, float(x1 / w), float(y1 / h), float((x2 - x1) / w), float((y2 - y1) / h), float(c)))
        return out


def weights_available(path: str | Path) -> bool:
    return Path(path).exists()
