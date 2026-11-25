"""Best-effort de-identification of free text before it leaves the platform for an external AI service.

Limits (stated in the UI and README): pattern based, NOT a certified anonymisation tool. It removes e-mail
addresses, phone numbers, long identifiers (MRN, national IDs), full dates, titled names and the display names
of platform users. Free-text names without a title can slip through, so doctors must not type patient names
into notes; the external call is also blocked unless an administrator enabled it (see llm.status()).
"""
from __future__ import annotations

import re

_PATTERNS = [
    (re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+"), "[EMAIL]"),
    (re.compile(r"(?i)\b(?:mrn|nid|ssn|file|record|id|رقم(?: الملف| الهوية)?)\s*[:#]?\s*\d[\d-]{3,}"), "[ID]"),
    (re.compile(r"(?<!\d)(?:\+?\d[\d\s().-]{7,}\d)(?!\d)"), "[PHONE]"),
    (re.compile(r"\b\d{6,}\b"), "[ID]"),
    (re.compile(r"\b\d{1,2}[/.-]\d{1,2}[/.-]\d{2,4}\b|\b\d{4}-\d{2}-\d{2}\b"), "[DATE]"),
    (re.compile(r"\b(?:Dr|Prof|Mr|Mrs|Ms|Miss)\.?\s+[A-Z][\w'-]+(?:\s+[A-Z][\w'-]+)?"), "[NAME]"),
    (re.compile(r"(?:د\.|دكتور|الدكتور|الدكتورة|الأستاذ|الأستاذة|السيد|السيدة)\s*\S+(?:\s+\S+)?"), "[NAME]"),
]


def deidentify(text: str | None, names: list[str] | tuple[str, ...] = ()) -> str:
    """Return `text` with identifiers masked. `names` are known person names (e.g. platform users) to mask."""
    out = str(text or "")
    for n in sorted({n.strip() for n in names if n and len(n.strip()) > 2}, key=len, reverse=True):
        out = re.sub(re.escape(n), "[CLINICIAN]", out, flags=re.IGNORECASE)
    for pat, repl in _PATTERNS:
        out = pat.sub(repl, out)
    return out


def user_names() -> list[str]:
    """Display names and usernames of all platform users (masked in anything sent out)."""
    from . import auth
    names: list[str] = []
    for u in auth.list_users():
        names += [u["display_name"], u["username"]]
        names += [part for part in u["display_name"].split() if len(part) > 3 and part.lower() not in ("dr.", "doctor")]
    return names
