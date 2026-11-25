"""UI strings (English / Arabic). Missing keys fall back to English, then to the key itself."""
from __future__ import annotations

from ._strings_ar import AR
from ._strings_en import EN

STRINGS = {"en": EN, "ar": AR}


def tr(key: str, lang: str = "en", **kw) -> str:
    s = STRINGS.get(lang, EN).get(key) or EN.get(key) or key
    return s.format(**kw) if kw else s
