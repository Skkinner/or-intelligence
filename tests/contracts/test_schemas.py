"""Contract tests (Owner: Member D, WBS 1.2.2): fixtures must validate against the schemas in contracts/."""

import json

import jsonschema
import pytest
import yaml

from src.common.contracts import (
    CONTRACTS_DIR,
    FIXTURES_DIR,
    class_colors,
    class_names,
    iter_jsonl,
    load_schema,
)

EXPECTED = ["grasper", "bipolar", "hook", "scissors", "clipper", "irrigator"]


def test_class_map_is_the_six_instruments():
    assert class_names() == EXPECTED
    assert set(class_colors()) == set(EXPECTED)


@pytest.mark.parametrize("name", ["detections", "timeline"])
def test_schemas_are_valid_json_schema(name):
    jsonschema.Draft202012Validator.check_schema(load_schema(name))


def test_detection_fixture_validates():
    validator = jsonschema.Draft202012Validator(load_schema("detections"))
    rows = list(iter_jsonl(FIXTURES_DIR / "sample_detections.jsonl"))
    assert len(rows) == 600
    for row in rows:
        validator.validate(row)


@pytest.mark.parametrize("fname", ["sample_timeline.json", "sample_timeline_case02.json"])
def test_timeline_fixtures_validate(fname):
    timeline = json.loads((FIXTURES_DIR / fname).read_text(encoding="utf-8"))
    jsonschema.validate(timeline, load_schema("timeline"))
    for tool, segs in timeline["tools"].items():
        assert timeline["stats"]["per_tool_segments"][tool] == len(segs)


def test_presence_fixture_matches_c3():
    lines = (FIXTURES_DIR / "sample_presence.csv").read_text(encoding="utf-8").strip().splitlines()
    assert lines[0] == "t_sec," + ",".join(EXPECTED)
    for line in lines[1:]:
        values = line.split(",")
        assert len(values) == 7 and set(values[1:]) <= {"0", "1"}


def test_openapi_parses_and_lists_c6_paths():
    spec = yaml.safe_load((CONTRACTS_DIR / "openapi.yaml").read_text(encoding="utf-8"))
    assert spec["openapi"].startswith("3.")
    for path in ["/api/videos", "/api/videos/{id}", "/api/videos/{id}/file", "/api/videos/{id}/timeline",
                 "/api/videos/{id}/notes", "/api/videos/{id}/notes/{note_id}", "/api/videos/{id}/report.pdf",
                 "/api/search", "/api/analytics"]:
        assert path in spec["paths"], path
