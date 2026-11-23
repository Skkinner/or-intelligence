"""Per-case statistics comparison (use case 5). Consumed by Member A's Analytics page (5.2.2).

WBS 4.2.2 · Owner: Member C
GET /api/analytics?video_ids=a,b -> {"cases": [{video_id, stats}], "aggregate": {mean_per_tool_s, mean_switches}}
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query

router = APIRouter(prefix="/api", tags=["analytics"])


def aggregate_stats(cases: list[dict]) -> dict:
    """Mean per-tool seconds and mean switches across ``cases`` (each has a C5 ``stats`` block).

    TODO(C, 4.2.2)
    """
    raise NotImplementedError("WBS 4.2.2 (Member C)")


@router.get("/analytics")
def analytics(video_ids: str = Query(..., description="comma-separated ids")) -> dict:
    raise HTTPException(status_code=501, detail="WBS 4.2.2 (Member C): not implemented yet")
