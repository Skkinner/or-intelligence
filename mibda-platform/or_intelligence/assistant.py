"""Case-specific research assistant: retrieval-augmented answers from Claude, grounded in this case's own data."""
from __future__ import annotations

import re

from . import casecontext, deid, llm

SYSTEM = """You are a clinical documentation and research assistant inside a surgical video review platform.
You help doctors understand ONE surgical case, its AI video analysis, the doctor's own notes, and related PubMed papers.

Rules:
- Ground every statement about the case or about a paper in the numbered context blocks you are given, and cite them
  like [C1], [N2], [R3] right after the statement. Doctor notes are tagged N, system analysis P/I/F, papers R.
- Only the abstracts of papers are available, not the full text. Say so when a question needs the full text.
- If the context does not contain the answer, say clearly that there is not enough evidence in the case data or the
  retrieved references. Never invent findings, patient details, measurements, citations or papers.
- General surgical or medical background that is not in the context may be given briefly, but label it
  "General knowledge (not from this case's sources)" and do not cite it as a source.
- You support documentation and research only. Do not give a diagnosis or choose a treatment for a patient; if asked,
  say the treating clinician decides.
- Analysis marked "dataset annotations replayed" is not model output; say so if it matters.
- Answer in the language of the question. Be concise and structured."""


def _clean_history(history: list[dict], names: list[str], turns: int = 8) -> list[dict]:
    msgs = [{"role": m["role"], "content": deid.deidentify(m["content"], names)} for m in history if m["content"].strip()]
    msgs = msgs[-turns * 2:]
    while msgs and msgs[0]["role"] != "user":
        msgs.pop(0)
    return msgs


def ask(facts: dict, refs: list[dict], history: list[dict], question: str) -> dict:
    """-> {"text", "sources": [{"label","kind","text"}], "tokens_in", "tokens_out", "model"}. Raises llm.LLMError."""
    names = deid.user_names()
    chunks = casecontext.facts_to_chunks(facts, refs)
    picked = casecontext.rank_chunks(question, chunks)
    ctx = "\n".join(f"[{lab}] {txt}" for lab, _, txt in picked)
    msgs = _clean_history(history, names)
    msgs.append({"role": "user", "content": f"<case_context>\n{ctx}\n</case_context>\n\nQuestion: {deid.deidentify(question, names)}"})
    r = llm.complete(SYSTEM, msgs, max_tokens=1500)
    by_label = {lab: (kind, txt) for lab, kind, txt in picked}
    cited = []
    for lab in dict.fromkeys(re.findall(r"\[([A-Z]\d+)\]", r.text)):
        if lab in by_label:
            cited.append({"label": lab, "kind": by_label[lab][0], "text": by_label[lab][1]})
    return {"text": r.text, "sources": cited, "tokens_in": r.tokens_in, "tokens_out": r.tokens_out, "model": r.model,
            "uncited": not cited}
