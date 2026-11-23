"""Library search by instrument (use case 3), e.g. "show all clipping segments".

WBS 4.2.2 · Owner: Member C
GET /api/search?tool=clipper&min_s=5 -> [{video_id, start, end, tool}] sorted by video_id then start.
Acceptance: tool=clipper on fixtures returns exactly the clipper segments.
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query

router = APIRouter(prefix="/api", tags=["search"])


def search_timelines(timelines: list[dict], tool: str, min_s: float = 0.0) -> list[dict]:
    """Pure function (easy to unit-test): scan C5 timelines and return matching segments.

    TODO(C, 4.2.2)
    """
    raise NotImplementedError("WBS 4.2.2 (Member C)")


@router.get("/search")
def search(tool: str = Query(...), min_s: float = Query(0.0, ge=0)) -> list[dict]:
    """Load every stored timeline from storage/timelines/ and call search_timelines."""
    raise HTTPException(status_code=501, detail="WBS 4.2.2 (Member C): not implemented yet")
