"""Unit tests for WBS 2.2.2 (Member A)."""

import pytest

from src.data import split


def test_leakage_check_rejects_shared_video():
    with pytest.raises(AssertionError):
        split.assert_no_leakage({"train": ["v01", "v02"], "val": ["v02"], "test": ["v03"]})


def test_leakage_check_accepts_disjoint_split():
    split.assert_no_leakage({"train": ["v01"], "val": ["v02"], "test": ["v03"]})


@pytest.mark.skip(reason="TODO WBS 2.2.2 (Member A): implement make_split")
def test_split_is_deterministic_and_complete():
    counts = {f"v{i:02d}": {c: 30 for c in range(6)} for i in range(1, 21)}
    a = split.make_split(counts, seed=42)
    b = split.make_split(counts, seed=42)
    assert a == b
    assert sorted(a["train"] + a["val"] + a["test"]) == sorted(counts)
    split.assert_no_leakage(a)


@pytest.mark.skip(reason="TODO WBS 2.2.2 (Member A): implement video_id_from_stem")
def test_video_id_from_stem():
    assert split.video_id_from_stem("v01_000123") == "v01"
