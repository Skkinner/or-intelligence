"""Golden tests for WBS 4.3.1 (Member C)."""

import json

import pytest

from src.common.contracts import FIXTURES_DIR
from src.reports.pdf_report import fmt_time
from src.reports.strings import STRINGS, t


def test_fmt_time():
    assert fmt_time(192) == "03:12"
    assert fmt_time(3725) == "1:02:05"


def test_strings_have_both_languages():
    for key, entry in STRINGS.items():
        assert set(entry) == {"en", "ar"}, key
    assert "not" in t("disclaimer", "en").lower()


@pytest.mark.skip(reason="TODO WBS 4.3.1 (Member C): implement render_report")
@pytest.mark.parametrize("lang", ["en", "ar"])
def test_pdf_contains_note_text(tmp_path, lang):
    pypdf = pytest.importorskip("pypdf")
    from src.reports.pdf_report import render_report

    timeline = json.loads((FIXTURES_DIR / "sample_timeline.json").read_text())
    notes = json.loads((FIXTURES_DIR / "sample_notes.json").read_text())
    out = render_report(timeline, notes, lang, str(tmp_path / f"r_{lang}.pdf"))
    text = "".join(p.extract_text() for p in pypdf.PdfReader(out).pages)
    assert "clip" in text.lower() or lang == "ar"
