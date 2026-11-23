"""FastAPI application entry point.

WBS 4.2.1 · Owner: Member C · Branch: feature/member-c-4.2.1-api   ⚠ critical integration point
Contract: contracts/openapi.yaml (C6). Run:  uvicorn src.api.main:app --reload --port 8000

Environment (see .env.example):
    INFERENCE_MODE=fixture | real    fixture replays tests/fixtures/sample_detections.jsonl (until best.pt, M4)
    STORAGE_DIR=storage              videos/, timelines/, detections/, app.db
"""

from __future__ import annotations

import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.routes import analytics, notes, reports, search, videos

app = FastAPI(title="OR Intelligence API", version="1.0.0-draft")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:8080"],  # Vite dev + preview
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(videos.router)
app.include_router(notes.router)
app.include_router(search.router)
app.include_router(analytics.router)
app.include_router(reports.router)


@app.get("/api/health")
def health() -> dict:
    """Liveness check used by the run scripts (7.1.1) and the smoke tests (6.3.1)."""
    return {"status": "ok", "inference_mode": os.getenv("INFERENCE_MODE", "fixture")}


# TODO(C, 4.2.1): on startup call db.init_db(); create STORAGE_DIR sub-folders.
