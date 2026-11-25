"""Best-effort privacy helpers for frames that leave the platform (previews, exports).

Limits (also stated in the UI): this is NOT a certified anonymization tool. Real
deployments need consent, de-identified recordings and a data-protection review.
"""
from __future__ import annotations

import numpy as np

try:
    import cv2
except Exception:  # pragma: no cover - cv2 is optional at import time
    cv2 = None

_cascade = None


def is_blank(img_bgr: np.ndarray, thr: float = 6.0) -> bool:
    """Fully black frames: how CholecT50 censors extra-abdominal views."""
    return float(img_bgr.mean()) < thr


def _get_cascade():
    global _cascade
    if _cascade is None and cv2 is not None:
        try:
            path = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
            c = cv2.CascadeClassifier(path)
            _cascade = c if not c.empty() else False
        except Exception:
            _cascade = False
    return _cascade or None


def blur_faces(img_bgr: np.ndarray) -> tuple[np.ndarray, int]:
    """Blur detected faces (OR staff visible when the camera leaves the body)."""
    cascade = _get_cascade()
    if cascade is None:
        return img_bgr, 0
    gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
    faces = cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(40, 40))
    out = img_bgr.copy()
    for (x, y, w, h) in faces:
        roi = out[y:y + h, x:x + w]
        k = max(15, (min(w, h) // 3) | 1)
        out[y:y + h, x:x + w] = cv2.GaussianBlur(roi, (k, k), 0)
    return out, int(len(faces))


def sanitize(img_bgr: np.ndarray) -> tuple[np.ndarray, dict]:
    info = {"blank": is_blank(img_bgr), "faces_blurred": 0}
    if info["blank"]:
        return img_bgr, info
    out, n = blur_faces(img_bgr)
    info["faces_blurred"] = n
    return out, info
