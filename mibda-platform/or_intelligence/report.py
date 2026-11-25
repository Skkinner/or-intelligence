"""PDF case report (English, or Arabic when an Arabic-capable font and shaping libs are available)."""
from __future__ import annotations

import time
from pathlib import Path

from reportlab.graphics.shapes import Drawing, Line, Rect, String
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from . import procedures
from .timeline import fmt_time

try:  # optional: Arabic shaping
    import arabic_reshaper
    from bidi.algorithm import get_display
except Exception:  # pragma: no cover
    arabic_reshaper = None
    get_display = None

_FONTS = [
    ("C:/Windows/Fonts/tahoma.ttf", "C:/Windows/Fonts/tahomabd.ttf"),
    ("C:/Windows/Fonts/arial.ttf", "C:/Windows/Fonts/arialbd.ttf"),
    ("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"),
]

S = {
    "en": {
        "title": "MIBDA': case review report",
        "case": "Case", "procedure": "Procedure", "video": "Video ID", "source": "Analysis source",
        "detector": "Detector", "created": "Created", "tags": "Tags",
        "src_annotations": "Ground-truth annotation replay (demo, not model output)",
        "src_model": "Model predictions",
        "summary": "Summary", "duration": "Duration", "entries": "Instrument entries",
        "per_min": "Entries / min", "used": "Instruments used",
        "usage": "Instrument usage", "instrument": "Instrument", "active": "Active time",
        "pct": "% of case", "segments": "Segments", "longest": "Longest",
        "timeline": "Instrument timeline", "phases": "Surgical phases (from annotations)",
        "phase": "Phase", "start": "Start", "end": "End",
        "flags": "Points for the reviewer", "notes": "Reviewer notes", "clips": "Teaching clips",
        "none": "None.", "by": "By", "time": "Time", "text": "Note",
        "f_long_use": "Long continuous use of {inst}", "f_frequent_entries": "{v:.0f} instrument entries within a short window",
        "f_idle_gap": "No instrument visible for {v:.0f} s", "f_clipper_segments": "{inst} active in {v:.0f} separate segments",
        "disclaimer": "Educational review aid. Not a diagnostic or assessment system; the instructor makes the final judgment. "
                      "Statistics describe instrument presence only.",
        "sparse": "Note: frames in this case were sampled sparsely, so times are approximate.",
        "ar_fallback": "Arabic report needs an Arabic font and the arabic-reshaper / python-bidi packages; English was used.",
    },
    "ar": {
        "title": "مبضع: تقرير مراجعة الحالة",
        "case": "الحالة", "procedure": "الإجراء", "video": "معرّف الفيديو", "source": "مصدر التحليل",
        "detector": "الكاشف", "created": "تاريخ الإنشاء", "tags": "الوسوم",
        "src_annotations": "إعادة عرض التسميات الأصلية (تجريبي، وليس مخرجات نموذج)",
        "src_model": "تنبؤات النموذج",
        "summary": "الملخص", "duration": "المدة", "entries": "مرات دخول الأدوات",
        "per_min": "الدخول / دقيقة", "used": "الأدوات المستخدمة",
        "usage": "استخدام الأدوات", "instrument": "الأداة", "active": "وقت النشاط",
        "pct": "% من الحالة", "segments": "المقاطع", "longest": "الأطول",
        "timeline": "الخط الزمني للأدوات", "phases": "مراحل العملية (من التسميات)",
        "phase": "المرحلة", "start": "البداية", "end": "النهاية",
        "flags": "نقاط للمراجع", "notes": "ملاحظات المراجع", "clips": "مقاطع تعليمية",
        "none": "لا يوجد.", "by": "بواسطة", "time": "الوقت", "text": "الملاحظة",
        "f_long_use": "استخدام متواصل طويل: {inst}", "f_frequent_entries": "{v:.0f} دخول للأدوات خلال فترة قصيرة",
        "f_idle_gap": "لا توجد أداة ظاهرة لمدة {v:.0f} ثانية", "f_clipper_segments": "{inst} نشطة في {v:.0f} مقاطع منفصلة",
        "disclaimer": "أداة مساعدة للمراجعة التعليمية، وليست نظام تشخيص أو تقييم. القرار النهائي للمدرّب. "
                      "الإحصاءات تصف حضور الأدوات فقط.",
        "sparse": "ملاحظة: الإطارات في هذه الحالة مأخوذة بشكل متفرق، لذلك الأوقات تقريبية.",
        "ar_fallback": "",
    },
}


def _register_font() -> tuple[str, str] | None:
    for regular, bold in _FONTS:
        if Path(regular).exists():
            try:
                pdfmetrics.registerFont(TTFont("ORI-Font", regular))
                pdfmetrics.registerFont(TTFont("ORI-Font-Bold", bold if Path(bold).exists() else regular))
                return "ORI-Font", "ORI-Font-Bold"
            except Exception:
                continue
    return None


def build_report(path: str | Path, *, case: dict, duration: float, intervals, usage_df, phases, flags,
                 notes, clips, metrics: dict, dense: bool, lang: str = "en",
                 proc: procedures.Procedure | None = None) -> str:
    """Write the PDF. Returns the language actually used ('en' or 'ar')."""
    proc = proc or procedures.get(procedures.DEFAULT_ID)
    has_instr = proc.n_instruments > 0
    fonts = None
    if lang == "ar":
        fonts = _register_font() if (arabic_reshaper and get_display) else None
        if fonts is None:
            lang = "en"
            fallback_note = True
        else:
            fallback_note = False
    else:
        fallback_note = False
    ar = lang == "ar"
    L = S[lang]
    base_font, bold_font = fonts if ar else ("Helvetica", "Helvetica-Bold")

    def sh(text: str) -> str:
        text = str(text)
        if not ar:
            return text
        return get_display(arabic_reshaper.reshape(text))

    ss = getSampleStyleSheet()
    align = TA_RIGHT if ar else TA_LEFT
    body = ParagraphStyle("b", parent=ss["Normal"], fontName=base_font, fontSize=9.5, leading=13, alignment=align)
    small = ParagraphStyle("s", parent=body, fontSize=8, leading=10.5, textColor=colors.HexColor("#555555"))
    h1 = ParagraphStyle("h1", parent=body, fontName=bold_font, fontSize=17, leading=21, spaceAfter=6)
    h2 = ParagraphStyle("h2", parent=body, fontName=bold_font, fontSize=11.5, leading=15, spaceBefore=10, spaceAfter=4,
                        textColor=colors.HexColor("#B26A24"))
    cell = ParagraphStyle("c", parent=body, fontSize=8.5, leading=11)
    head = ParagraphStyle("hc", parent=cell, fontName=bold_font, textColor=colors.white)

    def P(t, st=body):
        return Paragraph(sh(t).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"), st)

    def table(rows, widths, header=True):
        data = [[P(c, head if (header and r == 0) else cell) for c in row] for r, row in enumerate(rows)]
        t = Table(data, colWidths=widths, repeatRows=1 if header else 0)
        style = [("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#c9d3d1")), ("VALIGN", (0, 0), (-1, -1), "TOP"),
                 ("TOPPADDING", (0, 0), (-1, -1), 3), ("BOTTOMPADDING", (0, 0), (-1, -1), 3)]
        if header:
            style += [("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#B26A24")),
                      ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#eaf7f5")])]
        t.setStyle(TableStyle(style))
        return t

    width = A4[0] - 4 * cm
    story = [P(L["title"], h1)]
    src = L["src_model"] if case.get("source") == "model" else L["src_annotations"]
    story.append(table([
        [L["case"], case.get("title", "")], [L["procedure"], proc.label(lang)],
        [L["video"], case.get("video_id") or "-"], [L["source"], src],
        [L["detector"], case.get("detector") or "-"], [L["tags"], case.get("tags") or "-"],
        [L["created"], time.strftime("%Y-%m-%d %H:%M", time.localtime(case.get("created_at", time.time())))],
    ], [width * 0.28, width * 0.72], header=False))
    if fallback_note:
        story += [Spacer(1, 4), P(S["en"]["ar_fallback"], small)]

    story.append(P(L["summary"], h2))
    summary_rows = [[L["duration"], fmt_time(duration)]]
    if has_instr:
        summary_rows += [[L["entries"], metrics["instrument_entries"]], [L["per_min"], metrics["entries_per_min"]],
                         [L["used"], metrics["instruments_used"]]]
    story.append(table(summary_rows, [width * 0.5, width * 0.5], header=False))
    if not dense:
        story += [Spacer(1, 3), P(L["sparse"], small)]

    if has_instr:
        story.append(P(L["usage"], h2))
        rows = [[L["instrument"], L["active"], L["pct"], L["segments"], L["longest"]]]
        for r in usage_df.itertuples():
            i = proc.instrument_names.index(r.instrument)
            rows.append([proc.instrument_label(i, lang), f"{r.active_seconds:.0f} s", f"{r.pct_of_case}%", r.segments, f"{r.longest_segment:.0f} s"])
        story.append(table(rows, [width * 0.30, width * 0.18, width * 0.16, width * 0.16, width * 0.20]))

    story.append(P(L["timeline"], h2))
    story.append(_gantt(intervals, phases, duration, width, lang, sh, base_font, proc))

    if phases:
        story.append(P(L["phases"], h2))
        prow = [[L["phase"], L["start"], L["end"]]]
        for s in phases:
            prow.append([proc.phase_label(s.phase, lang), fmt_time(s.start), fmt_time(s.end)])
        story.append(table(prow, [width * 0.5, width * 0.25, width * 0.25]))

    story.append(P(L["flags"], h2))
    if flags:
        for f in flags:
            inst = proc.instrument_label(f.instrument, lang) if f.instrument is not None else ""
            msg = L["f_" + f.kind].format(inst=inst, v=f.value)
            story.append(P(f"[{fmt_time(f.start)} - {fmt_time(f.end)}] {msg}", body))
    else:
        story.append(P(L["none"], body))

    story.append(P(L["notes"], h2))
    if notes:
        story.append(table([[L["time"], L["by"], L["text"]]] + [[fmt_time(n["t_seconds"]), n["display_name"], n["text"]] for n in notes],
                           [width * 0.12, width * 0.23, width * 0.65]))
    else:
        story.append(P(L["none"], body))

    story.append(P(L["clips"], h2))
    if clips:
        story.append(table([[L["start"], L["end"], L["text"]]] + [[fmt_time(c["start_s"]), fmt_time(c["end_s"]), c["label"]] for c in clips],
                           [width * 0.15, width * 0.15, width * 0.70]))
    else:
        story.append(P(L["none"], body))

    story += [Spacer(1, 10), P(L["disclaimer"], small)]

    def footer(canvas, doc):
        canvas.saveState()
        canvas.setFont("Helvetica", 8)
        canvas.setFillColor(colors.grey)
        canvas.drawString(2 * cm, 1.2 * cm, "MIBDA'")
        canvas.drawRightString(A4[0] - 2 * cm, 1.2 * cm, str(doc.page))
        canvas.restoreState()

    SimpleDocTemplate(str(path), pagesize=A4, leftMargin=2 * cm, rightMargin=2 * cm, topMargin=1.8 * cm,
                      bottomMargin=1.8 * cm, title="MIBDA report").build(story, onFirstPage=footer, onLaterPages=footer)
    return lang


def _gantt(intervals, phases, duration, width, lang, sh, font, proc) -> Drawing:
    row_h, pad_l, top = 15, 96, 10
    n_instr = proc.n_instruments
    rows = n_instr + (1 if phases else 0)
    height = rows * row_h + 30
    d = Drawing(width, height)
    plot_w = width - pad_l - 6
    scale = plot_w / duration if duration > 0 else 1.0
    for i in range(n_instr):
        y = height - top - (i + 1) * row_h
        d.add(Rect(pad_l, y, plot_w, row_h - 3, fillColor=colors.HexColor("#f4f7f6"), strokeColor=None))
        d.add(String(pad_l - 4, y + 3, sh(proc.instrument_label(i, lang)), fontName=font, fontSize=7.5, textAnchor="end"))
        for iv in (v for v in intervals if v.instrument == i):
            d.add(Rect(pad_l + iv.start * scale, y, max(1.2, iv.duration * scale), row_h - 3,
                       fillColor=colors.HexColor(proc.instrument_color(i)), strokeColor=None))
    if phases:
        y = height - top - (n_instr + 1) * row_h
        d.add(String(pad_l - 4, y + 3, sh("Phase" if lang == "en" else "المرحلة"), fontName=font, fontSize=7.5, textAnchor="end"))
        for s in phases:
            d.add(Rect(pad_l + s.start * scale, y, max(1.2, (s.end - s.start) * scale), row_h - 3,
                       fillColor=colors.HexColor(proc.phase_color(s.phase)), strokeColor=None))
    step = max(60, int(duration / 8 / 60) * 60 or 60)
    t = 0
    while t <= duration:
        x = pad_l + t * scale
        d.add(Line(x, 12, x, 16, strokeColor=colors.grey, strokeWidth=0.5))
        d.add(String(x, 3, fmt_time(t), fontName="Helvetica", fontSize=6.5, textAnchor="middle"))
        t += step
    return d
