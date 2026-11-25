import glob
import re
from pathlib import Path

from or_intelligence.i18n import STRINGS, tr

ROOT = Path(__file__).resolve().parent.parent
DYNAMIC = {"flag_long_use", "flag_frequent_entries", "flag_idle_gap", "flag_clipper_segments",
           "role_trainee", "role_instructor", "role_admin", "limit_1", "limit_2", "limit_3", "limit_4", "limit_5"}


def _used_keys() -> set[str]:
    keys = set(DYNAMIC)
    for f in glob.glob(str(ROOT / "app" / "**" / "*.py"), recursive=True):
        keys |= set(re.findall(r"\bT\(\s*[\"'](\w+)[\"']", Path(f).read_text(encoding="utf-8")))
    return {k for k in keys if not k.endswith("_")}      # "flag_" / "role_" are prefixes, not keys


def test_every_ui_key_exists_in_both_languages():
    used = _used_keys()
    for lang in ("en", "ar"):
        missing = sorted(k for k in used if k not in STRINGS[lang])
        assert not missing, f"{lang} is missing {missing}"


def test_languages_have_the_same_keys_and_placeholders():
    assert set(STRINGS["en"]) == set(STRINGS["ar"])
    for k, en in STRINGS["en"].items():
        ph = lambda s: sorted(re.findall(r"\{(\w+)", s))
        assert ph(en) == ph(STRINGS["ar"][k]), f"placeholder mismatch in {k}"


def test_tr_formats_and_falls_back():
    assert tr("n_results", "en", n=3) == "3 case(s)"
    assert tr("does_not_exist", "ar") == "does_not_exist"
    assert "عدد" not in tr("flag_idle_gap", "ar", inst="", v=130)     # formats without crashing
