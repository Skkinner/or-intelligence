"""Related medical literature from PubMed (NCBI E-utilities). Every item is a real PubMed record with a PMID and
a link; nothing is generated. Only generic procedure terms are sent to PubMed, never patient or case text.
"""
from __future__ import annotations

import re
import xml.etree.ElementTree as ET
from dataclasses import asdict, dataclass, field

import requests

EUTILS = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
HEADERS = {"User-Agent": "MIBDA-case-research/1.0"}

# PubMed term for the procedure (MeSH where one exists).
PROC_TERM = {
    "lap-chole": '"cholecystectomy, laparoscopic"[MeSH Terms]',
    "cataract": '"cataract extraction"[MeSH Terms]',
}
CATEGORIES = {"guideline": "Guideline", "review": "Review", "trial": "Clinical trial", "article": "Research article"}


@dataclass
class Reference:
    pmid: str
    title: str
    authors: list[str] = field(default_factory=list)
    journal: str = ""
    date: str = ""
    pub_types: list[str] = field(default_factory=list)
    abstract: str = ""
    doi: str = ""
    topic: str = ""                 # which search found it
    matched: list[str] = field(default_factory=list)   # case terms present in its title/abstract

    @property
    def url(self) -> str:
        return f"https://pubmed.ncbi.nlm.nih.gov/{self.pmid}/"

    @property
    def category(self) -> str:
        t = " ".join(self.pub_types).lower()
        if "guideline" in t or "consensus" in t:
            return "guideline"
        if "review" in t or "meta-analysis" in t:
            return "review"
        if "trial" in t:
            return "trial"
        return "article"

    def to_dict(self) -> dict:
        return {**asdict(self), "url": self.url, "category": self.category}

    @staticmethod
    def from_dict(d: dict) -> "Reference":
        keys = Reference.__dataclass_fields__
        return Reference(**{k: v for k, v in d.items() if k in keys})


def build_queries(proc_id: str, proc_label: str, phases: list[str], instruments: list[str]) -> list[tuple[str, str]]:
    """[(topic label, PubMed query)] from the procedure plus what the case actually contains."""
    base = PROC_TERM.get(proc_id) or f'"{proc_label}"[Title/Abstract]'
    qs = [("Clinical guidelines", f"{base} AND (guideline[pt] OR practice guideline[pt] OR consensus[Title])"),
          ("Surgical video AI", f'{base} AND ("surgical phase recognition" OR "surgical video" OR "deep learning")'),
          ("Surgical education", f'{base} AND ("surgical education" OR "surgical training" OR "video review" OR "video-based coaching")')]
    for ph in phases[:2]:
        qs.append((f"Phase: {ph}", f'{base} AND "{ph}"[Title/Abstract]'))
    for ins in instruments[:1]:
        qs.append((f"Instrument: {ins}", f'{base} AND {ins}[Title/Abstract]'))
    return qs


def _get(path: str, **params) -> requests.Response:
    r = requests.get(f"{EUTILS}/{path}", params={"tool": "mibda", **params}, headers=HEADERS, timeout=20)
    r.raise_for_status()
    return r


def search(query: str, retmax: int = 5) -> list[str]:
    data = _get("esearch.fcgi", db="pubmed", term=query, retmax=retmax, sort="relevance", retmode="json").json()
    return list(data.get("esearchresult", {}).get("idlist", []))


def _text(el) -> str:
    return "".join(el.itertext()).strip() if el is not None else ""


def parse_articles(xml_text: str) -> list[Reference]:
    out = []
    for art in ET.fromstring(xml_text).iter("PubmedArticle"):
        pmid = _text(art.find(".//MedlineCitation/PMID"))
        title = _text(art.find(".//ArticleTitle"))
        if not pmid or not title:
            continue
        authors = []
        for a in art.findall(".//AuthorList/Author"):
            last, ini = _text(a.find("LastName")), _text(a.find("Initials"))
            if last:
                authors.append(f"{last} {ini}".strip())
        y = _text(art.find(".//JournalIssue/PubDate/Year")) or (re.search(r"\d{4}", _text(art.find(".//JournalIssue/PubDate/MedlineDate"))) or [""])[0]
        m = _text(art.find(".//JournalIssue/PubDate/Month"))
        abstract = " ".join(_text(x) for x in art.findall(".//Abstract/AbstractText"))
        doi = next((_text(i) for i in art.findall(".//ArticleIdList/ArticleId") if i.get("IdType") == "doi"), "")
        out.append(Reference(pmid=pmid, title=title.rstrip("."), authors=authors, journal=_text(art.find(".//Journal/Title")),
                             date=f"{y} {m}".strip(), pub_types=[_text(p) for p in art.findall(".//PublicationType")],
                             abstract=abstract, doi=doi))
    return out


def fetch(pmids: list[str]) -> list[Reference]:
    if not pmids:
        return []
    return parse_articles(_get("efetch.fcgi", db="pubmed", id=",".join(pmids), retmode="xml").text)


def retrieve(queries: list[tuple[str, str]], case_terms: list[str], per_query: int = 4, total: int = 12) -> list[Reference]:
    """Run the searches, de-duplicate by PMID, keep each hit's topic and the case terms it mentions."""
    seen: dict[str, str] = {}
    for topic, q in queries:
        try:
            for pm in search(q, per_query):
                seen.setdefault(pm, topic)
        except requests.RequestException:
            continue
        if len(seen) >= total:
            break
    refs = fetch(list(seen)[:total])
    for r in refs:
        r.topic = seen.get(r.pmid, "")
        blob = f"{r.title} {r.abstract}".lower()
        r.matched = [t for t in case_terms if t and t.lower() in blob]
    return refs


def short_summary(ref: Reference, max_chars: int = 320) -> str:
    """The start of the paper's own abstract (not a generated summary)."""
    a = ref.abstract.strip()
    if not a:
        return ""
    if len(a) <= max_chars:
        return a
    cut = a[:max_chars].rsplit(" ", 1)[0]
    return cut + "…"
