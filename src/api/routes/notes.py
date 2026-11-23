"""Timestamped instructor notes (use case 2).

WBS 4.2.2 · Owner: Member C · Branch: feature/member-c-4.2.2-notes-search
Note = {id, video_id, t_sec, text, author, created_at}; persists across restarts (SQLite, src/api/db.py).
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

router = APIRouter(prefix="/api/videos/{video_id}/notes", tags=["notes"])

TODO = "WBS 4.2.2 (Member C): not implemented yet"


class NoteCreate(BaseModel):
    t_sec: float = Field(ge=0)
    text: str = Field(min_length=1, max_length=2000)
    author: str = "instructor"


@router.get("")
def list_notes(video_id: str) -> list[dict]:
    """Notes sorted by t_sec."""
    raise HTTPException(status_code=501, detail=TODO)


@router.post("", status_code=201)
def create_note(video_id: str, note: NoteCreate) -> dict:
    raise HTTPException(status_code=501, detail=TODO)


@router.delete("/{note_id}", status_code=204)
def delete_note(video_id: str, note_id: int) -> None:
    raise HTTPException(status_code=501, detail=TODO)
