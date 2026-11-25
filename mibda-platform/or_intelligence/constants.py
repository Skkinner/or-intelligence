"""Class names shared by every dataset adapter, the detector and the UI.

Instrument ids 0..5 match the CholecT50 / CholecInstanceSeg label order.
"""
from __future__ import annotations

INSTRUMENTS = ["grasper", "bipolar", "hook", "scissors", "clipper", "irrigator"]
N_INSTRUMENTS = len(INSTRUMENTS)
INSTRUMENT_ID = {n: i for i, n in enumerate(INSTRUMENTS)}

INSTRUMENT_AR = {
    "grasper": "ماسك (Grasper)",
    "bipolar": "ملقط ثنائي القطب",
    "hook": "خطّاف",
    "scissors": "مقص",
    "clipper": "أداة تدبيس",
    "irrigator": "أداة ري وشفط",
}

INSTRUMENT_COLORS = {
    "grasper": "#5C061C",
    "bipolar": "#C25B6E",
    "hook": "#CD7F32",
    "scissors": "#A8788A",
    "clipper": "#E3A868",
    "irrigator": "#5E8466",
}

# Phase names as used by CholecT50 (the dataset spells "carlot").
PHASES = [
    "preparation",
    "carlot-triangle-dissection",
    "clipping-and-cutting",
    "gallbladder-dissection",
    "gallbladder-packaging",
    "cleaning-and-coagulation",
    "gallbladder-extraction",
]
PHASE_EN = [
    "Preparation",
    "Calot triangle dissection",
    "Clipping and cutting",
    "Gallbladder dissection",
    "Gallbladder packaging",
    "Cleaning and coagulation",
    "Gallbladder extraction",
]
PHASE_AR = [
    "التحضير",
    "تشريح مثلث كالو",
    "التدبيس والقطع",
    "فصل المرارة عن الكبد",
    "تعبئة المرارة في الكيس",
    "التنظيف والكيّ",
    "إخراج المرارة",
]
PHASE_COLORS = ["#5C061C", "#CD7F32", "#C25B6E", "#A8788A", "#E3A868", "#E8C79A", "#A6836A"]

VERBS = [
    "grasp", "retract", "dissect", "coagulate", "clip",
    "cut", "aspirate", "irrigate", "pack", "null_verb",
]
VERB_AR = {
    "grasp": "مسك", "retract": "سحب", "dissect": "تشريح", "coagulate": "كيّ",
    "clip": "تدبيس", "cut": "قطع", "aspirate": "شفط", "irrigate": "ري",
    "pack": "تعبئة", "null_verb": "-",
}
TARGETS = [
    "gallbladder", "cystic_plate", "cystic_duct", "cystic_artery", "cystic_pedicle",
    "blood_vessel", "fluid", "abdominal_wall_cavity", "liver", "adhesion",
    "omentum", "peritoneum", "gut", "specimen_bag", "null_target",
]


def instrument_label(idx: int, lang: str = "en") -> str:
    name = INSTRUMENTS[idx]
    return INSTRUMENT_AR[name] if lang == "ar" else name.capitalize()


def phase_label(idx: int | None, lang: str = "en") -> str:
    if idx is None or not 0 <= idx < len(PHASES):
        return "-"
    return PHASE_AR[idx] if lang == "ar" else PHASE_EN[idx]
