"""The case facts the AI features are allowed to see, and the labelled evidence chunks built from them.

Everything here is de-identified text. Doctor-provided material (notes, comments) and system analysis are kept
apart so the report and the assistant can always say which is which.
"""
from __future__ import annotations

import re

from . import deid
from .timeline import fmt_time


def build_facts(case, analysis, notes, clips, proc, phases, usage, flags, metrics, lang: str = "en") -> dict:
    """Plain dict of everything known about the case. `case_ref` replaces the title (titles can hold identifiers)."""
    names = deid.user_names()
    clin: dict[str, str] = {}

    def who(n: str) -> str:
        return clin.setdefault(n, f"Clinician {chr(65 + len(clin))}")

    has_i = proc.n_instruments > 0
    return {
        "case_ref": f"Case #{case['id']}",
        "procedure": proc.label("en"),
        "duration_s": round(analysis.duration, 1),
        "analysis_source": ("model predictions" if case["source"] == "model"
                            else "dataset annotations replayed (not model output)"),
        "detector": case["detector"] or "",
        "sparse_sampling": not analysis.dense,
        "tags": deid.deidentify(case["tags"], names),
        "phases": [{"name": proc.phase_label(s.phase, "en"), "start_s": round(s.start, 1), "end_s": round(s.end, 1)}
                   for s in phases],
        "instruments": ([{"name": proc.instrument_label(proc.instrument_names.index(r.instrument), "en"),
                          "active_s": round(float(r.active_seconds), 1), "pct_of_case": float(r.pct_of_case),
                          "segments": int(r.segments)} for r in usage.itertuples()] if has_i else []),
        "instrument_entries": metrics.get("instrument_entries") if has_i else None,
        "flags": [{"kind": f.kind, "start_s": round(f.start, 1), "end_s": round(f.end, 1),
                   "instrument": proc.instrument_label(f.instrument, "en") if f.instrument is not None else "",
                   "value": round(float(f.value), 1)} for f in flags],
        "doctor_notes": [{"t_s": round(float(n["t_seconds"]), 1), "author": who(n["display_name"]),
                          "text": deid.deidentify(n["text"], names)} for n in notes],
        "clips": [{"start_s": round(float(c["start_s"]), 1), "end_s": round(float(c["end_s"]), 1),
                   "label": deid.deidentify(c["label"], names)} for c in clips],
    }


def facts_to_chunks(facts: dict, refs: list[dict] | None = None) -> list[tuple[str, str, str]]:
    """[(label, kind, text)]. Labels: C case, P phases, I instruments, F flags, N doctor note, K clip, R reference."""
    ch: list[tuple[str, str, str]] = []
    ov = (f"{facts['case_ref']}. Procedure: {facts['procedure']}. Duration {fmt_time(facts['duration_s'])}. "
          f"Analysis source: {facts['analysis_source']}."
          + (f" Detector: {facts['detector']}." if facts["detector"] else "")
          + (" Frames were sampled sparsely, so times are approximate." if facts["sparse_sampling"] else "")
          + (f" Tags: {facts['tags']}." if facts["tags"] else ""))
    ch.append(("C1", "case", ov))
    if facts["phases"]:
        ch.append(("P1", "analysis", "Surgical phases (start-end): " + "; ".join(
            f"{p['name']} {fmt_time(p['start_s'])}-{fmt_time(p['end_s'])}" for p in facts["phases"])))
    if facts["instruments"]:
        ch.append(("I1", "analysis", "Instrument usage: " + "; ".join(
            f"{i['name']} active {i['active_s']:.0f}s ({i['pct_of_case']}% of case, {i['segments']} segments)"
            for i in facts["instruments"])))
    for k, f in enumerate(facts["flags"], 1):
        who = f" {f['instrument']}" if f["instrument"] else ""
        ch.append((f"F{k}", "analysis", f"Review flag '{f['kind']}'{who} at {fmt_time(f['start_s'])}-{fmt_time(f['end_s'])} (value {f['value']})."))
    for k, n in enumerate(facts["doctor_notes"], 1):
        ch.append((f"N{k}", "doctor", f"Doctor's note at {fmt_time(n['t_s'])} by {n['author']}: {n['text']}"))
    for k, c in enumerate(facts["clips"], 1):
        ch.append((f"K{k}", "doctor", f"Teaching clip {fmt_time(c['start_s'])}-{fmt_time(c['end_s'])}: {c['label']}"))
    for k, r in enumerate(refs or [], 1):
        au = ", ".join(r.get("authors", [])[:4]) + (" et al." if len(r.get("authors", [])) > 4 else "")
        ch.append((f"R{k}", "reference", f"PubMed {r['pmid']}: {r['title']}. {au}. {r.get('journal', '')} {r.get('date', '')}. "
                   f"Abstract: {r.get('abstract') or '(no abstract available)'}"))
    return ch


_TOKEN = re.compile(r"[\w']+", re.UNICODE)


def _tokens(s: str) -> set[str]:
    return {t.lower() for t in _TOKEN.findall(s) if len(t) > 2}


def rank_chunks(question: str, chunks: list[tuple[str, str, str]], k: int = 10) -> list[tuple[str, str, str]]:
    """Keyword-overlap retrieval. The case overview is always kept; the rest are the best-matching chunks."""
    q = _tokens(question)
    scored = sorted(((len(q & _tokens(t)) / (1 + len(_tokens(t)) ** 0.5), i) for i, (_, _, t) in enumerate(chunks)),
                    reverse=True)
    keep = {0} | {i for s, i in scored[:k] if s > 0}
    if len(keep) < min(k, len(chunks)):          # nothing matched well: give the model the analysis chunks too
        keep |= {i for i, (_, kind, _) in enumerate(chunks) if kind in ("analysis", "doctor")}
    return [chunks[i] for i in sorted(keep)][: k + 4]
