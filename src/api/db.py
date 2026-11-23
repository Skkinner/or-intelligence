"""SQLite persistence (SQLModel): Video and Note tables.

WBS 4.2.1 · Owner: Member C
Notes must persist across server restarts (4.2.2 acceptance) -> file DB at $STORAGE_DIR/app.db.
"""

from __future__ import annotations

import os
from datetime import datetime, timezone
from pathlib import Path

from sqlmodel import Field, Session, SQLModel, create_engine

STORAGE_DIR = Path(os.getenv("STORAGE_DIR", "storage"))


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Video(SQLModel, table=True):
    id: str = Field(primary_key=True)
    title: str
    status: str = "queued"           # queued | processing | done | failed
    progress: float = 0.0
    duration_s: float | None = None
    error: str | None = None
    created_at: datetime = Field(default_factory=_utcnow)


class Note(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    video_id: str = Field(foreign_key="video.id", index=True)
    t_sec: float
    text: str
    author: str = "instructor"
    created_at: datetime = Field(default_factory=_utcnow)


_engine = None


def get_engine():
    global _engine
    if _engine is None:
        STORAGE_DIR.mkdir(parents=True, exist_ok=True)
        _engine = create_engine(f"sqlite:///{STORAGE_DIR / 'app.db'}", connect_args={"check_same_thread": False})
    return _engine


def init_db() -> None:
    SQLModel.metadata.create_all(get_engine())


def get_session():
    """FastAPI dependency: ``session: Session = Depends(get_session)``."""
    with Session(get_engine()) as session:
        yield session
