"""Procedure library loaded from procedures.yaml. A procedure defines its phases and instruments."""
from __future__ import annotations

from dataclasses import dataclass, field
from functools import lru_cache

import yaml

from . import config

PALETTE = ["#5C061C", "#CD7F32", "#C25B6E", "#A8788A", "#E3A868", "#E8C79A",
           "#A6836A", "#5E8466", "#D9A3AE", "#8F6B7A", "#9BAE7C", "#B88A6A"]
DEFAULT_ID = "lap-chole"


@dataclass
class Procedure:
    id: str
    status: str                       # ready | adapter-untested | planned
    name: dict
    specialty: dict
    datasets: list[str] = field(default_factory=list)
    capabilities: dict = field(default_factory=dict)
    phases: list[dict] = field(default_factory=list)          # [{en, ar}]
    instruments: list[dict] = field(default_factory=list)     # [{name, ar, color}]

    def __post_init__(self) -> None:
        if self.id == DEFAULT_ID and not self.phases:
            from . import constants as c   # built-in definition for the original procedure
            self.phases = [{"en": e, "ar": a} for e, a in zip(c.PHASE_EN, c.PHASE_AR)]
            self.instruments = [{"name": n, "ar": c.INSTRUMENT_AR[n], "color": c.INSTRUMENT_COLORS[n]} for n in c.INSTRUMENTS]

    # ---- sizes / names
    @property
    def n_phases(self) -> int:
        return len(self.phases)

    @property
    def n_instruments(self) -> int:
        return len(self.instruments)

    @property
    def instrument_names(self) -> list[str]:
        return [i["name"] for i in self.instruments]

    def label(self, lang: str = "en") -> str:
        return self.name.get(lang) or self.name["en"]

    def specialty_label(self, lang: str = "en") -> str:
        return self.specialty.get(lang) or self.specialty["en"]

    def instrument_label(self, i: int, lang: str = "en") -> str:
        d = self.instruments[i]
        return (d.get("ar") if lang == "ar" else None) or d["name"].capitalize()

    def phase_label(self, i: int | None, lang: str = "en") -> str:
        if i is None or not 0 <= i < self.n_phases:
            return "-"
        d = self.phases[i]
        return d.get(lang) or d["en"]

    def phase_color(self, i: int) -> str:
        if self.id == DEFAULT_ID:
            from . import constants as c
            return c.PHASE_COLORS[i % len(c.PHASE_COLORS)]
        return PALETTE[i % len(PALETTE)]

    def instrument_color(self, i: int) -> str:
        return self.instruments[i].get("color") or PALETTE[i % len(PALETTE)]


@lru_cache(maxsize=1)
def load_all() -> tuple[Procedure, ...]:
    data = yaml.safe_load(config.PROCEDURES_YAML.read_text(encoding="utf-8"))["procedures"]
    return tuple(Procedure(**d) for d in data)


def get(proc_id: str | None) -> Procedure | None:
    return next((p for p in load_all() if p.id == proc_id), None)


def resolve(value: str | None) -> Procedure:
    """Procedure for a stored value: an id, or a legacy free-text name. Falls back to the default."""
    p = get(value)
    if p:
        return p
    text = (value or "").lower()
    for p in load_all():
        if any(k in text for k in {"lap-chole": ("cholecyst",), "cataract": ("cataract",)}.get(p.id, ())):
            return p
    return get(DEFAULT_ID)


def dataset_registry() -> dict[str, dict]:
    data = yaml.safe_load(config.DATASETS_YAML.read_text(encoding="utf-8"))["datasets"]
    return {d["id"]: d for d in data}
