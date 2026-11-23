"""Report strings in English and Arabic. Owner: Member C (WBS 4.3.1).

TODO(C, 4.3.1): complete the Arabic column (Member A reviews it in 5.2.3). Keep keys identical in both languages.
"""

from __future__ import annotations

STRINGS: dict[str, dict[str, str]] = {
    "title": {"en": "Surgical Video Review Report", "ar": ""},
    "video": {"en": "Video", "ar": ""},
    "duration": {"en": "Duration", "ar": ""},
    "timeline": {"en": "Instrument timeline", "ar": ""},
    "stats": {"en": "Instrument statistics", "ar": ""},
    "tool": {"en": "Instrument", "ar": ""},
    "time_used": {"en": "Time used", "ar": ""},
    "segments": {"en": "Segments", "ar": ""},
    "switches": {"en": "Tool switches", "ar": ""},
    "notes": {"en": "Instructor notes", "ar": ""},
    "disclaimer": {
        "en": "Educational review tool. Not a diagnostic or clinical decision-making system.",
        "ar": "",
    },
}


def t(key: str, lang: str = "en") -> str:
    """Translated string; falls back to English if the Arabic entry is still empty."""
    entry = STRINGS[key]
    return entry.get(lang) or entry["en"]
