"""Video endpoints: upload, list, status, file streaming (HTTP Range), timeline.

WBS 4.2.1 · Owner: Member C · Contract: contracts/openapi.yaml (C6)
"""

from __future__ import annotations

from fastapi import APIRouter, BackgroundTasks, File, HTTPException, Request, UploadFile

router = APIRouter(prefix="/api/videos", tags=["videos"])

TODO = "WBS 4.2.1 (Member C): not implemented yet"


@router.post("", status_code=202)
async def upload_video(background: BackgroundTasks, file: UploadFile = File(...), title: str | None = None) -> dict:
    """Save to storage/videos/<id>.mp4, insert Video(status=queued), schedule jobs.process_video(id).

    Returns ``{"id": <id>, "status": "queued"}``.
    """
    raise HTTPException(status_code=501, detail=TODO)


@router.get("")
def list_videos() -> list[dict]:
    """``[{id, title, status, duration_s, created_at}]`` newest first."""
    raise HTTPException(status_code=501, detail=TODO)


@router.get("/{video_id}")
def get_status(video_id: str) -> dict:
    """``{id, status, progress, error}``; 404 if unknown."""
    raise HTTPException(status_code=501, detail=TODO)


@router.get("/{video_id}/file")
def get_file(video_id: str, request: Request):
    """Stream the video with HTTP Range support (206 Partial Content) so the browser can seek."""
    raise HTTPException(status_code=501, detail=TODO)


@router.get("/{video_id}/timeline")
def get_timeline(video_id: str) -> dict:
    """Return the stored C5 timeline; 409 if not done yet."""
    raise HTTPException(status_code=501, detail=TODO)
