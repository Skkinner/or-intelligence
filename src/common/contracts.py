"""Read-only helpers for the shared contracts in ``contracts/``.

Owner: Member D (WBS 1.2.2). Everyone imports this; nobody else edits it.
Use these helpers instead of hard-coding class ids, names or colours.
"""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
CONTRACTS_DIR = REPO_ROOT / "contracts"
FIXTURES_DIR = REPO_ROOT / "tests" / "fixtures"


@lru_cache(maxsize=None)
def load_classes() -> dict[str, Any]:
    """Return the parsed ``contracts/classes.json`` (C1)."""
    return json.loads((CONTRACTS_DIR / "classes.json").read_text(encoding="utf-8"))


def class_names() -> list[str]:
    """Class names ordered by id: ``["grasper", "bipolar", "hook", "scissors", "clipper", "irrigator"]``."""
    classes = load_classes()["classes"]
    return [classes[str(i)] for i in range(len(classes))]


def name_to_id() -> dict[str, int]:
    """``{"grasper": 0, ...}``."""
    return {name: i for i, name in enumerate(class_names())}


def class_colors() -> dict[str, str]:
    """UI / PDF colour per tool name."""
    return dict(load_classes()["colors"])


@lru_cache(maxsize=None)
def load_schema(name: str) -> dict[str, Any]:
    """Load a JSON schema from ``contracts/``, e.g. ``load_schema("timeline")``."""
    return json.loads((CONTRACTS_DIR / f"{name}.schema.json").read_text(encoding="utf-8"))


def validate(instance: Any, schema_name: str) -> None:
    """Raise ``jsonschema.ValidationError`` if ``instance`` does not match the named contract."""
    import jsonschema

    jsonschema.validate(instance=instance, schema=load_schema(schema_name))


def iter_jsonl(path: str | Path):
    """Yield one dict per non-empty line of a ``.jsonl`` file (e.g. detections, contract C4)."""
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                yield json.loads(line)
