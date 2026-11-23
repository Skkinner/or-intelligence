"""PDF report endpoint.

WBS 4.3.1 · Owner: Member C
GET /api/videos/{id}/report.pdf?lang=en|ar -> application/pdf (via src.reports.pdf_report.render_report)
"""

from __future__ import annotations

from typing import Literal

from fastapi import APIRouter, HTTPException

router = APIRouter(prefix="/api/videos", tags=["reports"])


@router.get("/{video_id}/report.pdf")
def report_pdf(video_id: str, lang: Literal["en", "ar"] = "en"):
    """Load timeline + notes, render to storage/reports/<id>_<lang>.pdf, return FileResponse(media_type="application/pdf").

    TODO(C, 4.3.1)
    """
    raise HTTPException(status_code=501, detail="WBS 4.3.1 (Member C): not implemented yet")
