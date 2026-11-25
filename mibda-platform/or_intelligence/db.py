"""SQLite storage: users, cases, timestamped notes, teaching clips and an audit log."""
from __future__ import annotations

import json
import sqlite3
import time
from contextlib import contextmanager
from pathlib import Path

from . import config

SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    display_name TEXT NOT NULL,
    role TEXT NOT NULL CHECK (role IN ('trainee','instructor','admin')),
    salt TEXT NOT NULL,
    pw_hash TEXT NOT NULL,
    created_at INTEGER NOT NULL
);
CREATE TABLE IF NOT EXISTS cases (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    procedure TEXT NOT NULL DEFAULT 'laparoscopic cholecystectomy',
    video_id TEXT,
    media_kind TEXT NOT NULL CHECK (media_kind IN ('frames','video')),
    media_path TEXT NOT NULL,
    analysis_path TEXT NOT NULL,
    source TEXT NOT NULL,
    detector TEXT,
    owner_id INTEGER REFERENCES users(id),
    trainee_id INTEGER REFERENCES users(id),
    tags TEXT NOT NULL DEFAULT '',
    consent INTEGER NOT NULL DEFAULT 0,
    retention_days INTEGER,
    duration REAL NOT NULL DEFAULT 0,
    n_frames INTEGER NOT NULL DEFAULT 0,
    stats_json TEXT NOT NULL DEFAULT '{}',
    created_at INTEGER NOT NULL
);
CREATE TABLE IF NOT EXISTS notes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    case_id INTEGER NOT NULL REFERENCES cases(id) ON DELETE CASCADE,
    author_id INTEGER NOT NULL REFERENCES users(id),
    t_seconds REAL NOT NULL,
    text TEXT NOT NULL,
    created_at INTEGER NOT NULL
);
CREATE TABLE IF NOT EXISTS clips (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    case_id INTEGER NOT NULL REFERENCES cases(id) ON DELETE CASCADE,
    author_id INTEGER NOT NULL REFERENCES users(id),
    start_s REAL NOT NULL,
    end_s REAL NOT NULL,
    label TEXT NOT NULL,
    created_at INTEGER NOT NULL
);
CREATE TABLE IF NOT EXISTS audit (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    action TEXT NOT NULL,
    case_id INTEGER,
    detail TEXT NOT NULL DEFAULT '',
    at INTEGER NOT NULL
);
CREATE TABLE IF NOT EXISTS case_reports (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    case_id INTEGER NOT NULL REFERENCES cases(id) ON DELETE CASCADE,
    content_json TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'draft' CHECK (status IN ('draft','final')),
    model TEXT NOT NULL DEFAULT '',
    tokens_in INTEGER NOT NULL DEFAULT 0,
    tokens_out INTEGER NOT NULL DEFAULT 0,
    created_by INTEGER REFERENCES users(id),
    reviewed_by INTEGER REFERENCES users(id),
    created_at INTEGER NOT NULL,
    updated_at INTEGER NOT NULL
);
CREATE TABLE IF NOT EXISTS case_refs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    case_id INTEGER NOT NULL REFERENCES cases(id) ON DELETE CASCADE,
    items_json TEXT NOT NULL,
    fetched_at INTEGER NOT NULL
);
CREATE TABLE IF NOT EXISTS chat_messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    case_id INTEGER NOT NULL REFERENCES cases(id) ON DELETE CASCADE,
    user_id INTEGER NOT NULL REFERENCES users(id),
    role TEXT NOT NULL CHECK (role IN ('user','assistant')),
    content TEXT NOT NULL,
    sources_json TEXT NOT NULL DEFAULT '[]',
    tokens_in INTEGER NOT NULL DEFAULT 0,
    tokens_out INTEGER NOT NULL DEFAULT 0,
    created_at INTEGER NOT NULL
);
"""


def connect() -> sqlite3.Connection:
    config.ensure_dirs()
    conn = sqlite3.connect(config.DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


@contextmanager
def session():
    conn = connect()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_db() -> None:
    with session() as c:
        c.executescript(SCHEMA)


def now() -> int:
    return int(time.time())


# ---- audit ---------------------------------------------------------------
def log(user_id: int | None, action: str, case_id: int | None = None, detail: str = "") -> None:
    with session() as c:
        c.execute("INSERT INTO audit(user_id,action,case_id,detail,at) VALUES (?,?,?,?,?)",
                  (user_id, action, case_id, detail, now()))


def list_audit(limit: int = 200) -> list[sqlite3.Row]:
    with session() as c:
        return c.execute(
            "SELECT a.*, u.username FROM audit a LEFT JOIN users u ON u.id=a.user_id ORDER BY a.id DESC LIMIT ?",
            (limit,)).fetchall()


# ---- cases ---------------------------------------------------------------
def add_case(*, title: str, media_kind: str, media_path: str, analysis_path: str, source: str,
             owner_id: int | None, trainee_id: int | None = None, video_id: str | None = None,
             detector: str = "", tags: str = "", consent: bool = False, retention_days: int | None = None,
             duration: float = 0.0, n_frames: int = 0, stats: dict | None = None,
             procedure: str = "lap-chole") -> int:
    with session() as c:
        cur = c.execute(
            """INSERT INTO cases(title,procedure,video_id,media_kind,media_path,analysis_path,source,detector,
               owner_id,trainee_id,tags,consent,retention_days,duration,n_frames,stats_json,created_at)
               VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (title, procedure, video_id, media_kind, str(media_path), str(analysis_path), source, detector,
             owner_id, trainee_id, tags, int(consent), retention_days, duration, n_frames,
             json.dumps(stats or {}), now()))
        return int(cur.lastrowid)


def get_case(case_id: int) -> sqlite3.Row | None:
    with session() as c:
        return c.execute("SELECT * FROM cases WHERE id=?", (case_id,)).fetchone()


def find_public_case(video_id: str, dataset_tag: str) -> sqlite3.Row | None:
    """A case already imported from a public dataset (avoids importing the same video twice)."""
    with session() as c:
        return c.execute(
            "SELECT * FROM cases WHERE video_id=? AND tags LIKE ? AND tags LIKE '%public-dataset%'",
            (video_id, f"%{dataset_tag}%")).fetchone()


def can_view(user: dict, case: sqlite3.Row) -> bool:
    if user["role"] in ("admin", "instructor"):
        return True
    return user["id"] in (case["owner_id"], case["trainee_id"])


def list_cases(user: dict) -> list[sqlite3.Row]:
    with session() as c:
        if user["role"] in ("admin", "instructor"):
            return c.execute("SELECT * FROM cases ORDER BY created_at DESC, id DESC").fetchall()
        return c.execute(
            "SELECT * FROM cases WHERE owner_id=? OR trainee_id=? ORDER BY created_at DESC, id DESC",
            (user["id"], user["id"])).fetchall()


def update_case(case_id: int, **fields) -> None:
    allowed = {"title", "tags", "trainee_id", "analysis_path", "source", "detector", "duration", "n_frames", "stats_json", "retention_days"}
    sets = {k: v for k, v in fields.items() if k in allowed}
    if not sets:
        return
    if "stats_json" in sets and not isinstance(sets["stats_json"], str):
        sets["stats_json"] = json.dumps(sets["stats_json"])
    with session() as c:
        c.execute(f"UPDATE cases SET {', '.join(k + '=?' for k in sets)} WHERE id=?", (*sets.values(), case_id))


def delete_case(case_id: int, delete_files: bool = True) -> None:
    case = get_case(case_id)
    if case is None:
        return
    with session() as c:
        c.execute("DELETE FROM cases WHERE id=?", (case_id,))
    if delete_files:
        _remove_owned_files(case)


def _remove_owned_files(case: sqlite3.Row) -> None:
    """Only ever delete files that live inside the platform's own data folders."""
    for p, base in ((case["analysis_path"], config.ANALYSIS_DIR), (case["media_path"], config.UPLOAD_DIR)):
        try:
            path = Path(p).resolve()
            if path.is_file() and base.resolve() in path.parents:
                path.unlink()
        except OSError:
            pass


def purge_expired(now_ts: int | None = None) -> int:
    """Delete cases whose retention period has passed. Returns how many were removed."""
    now_ts = now_ts or now()
    with session() as c:
        rows = c.execute("SELECT * FROM cases WHERE retention_days IS NOT NULL").fetchall()
    n = 0
    for r in rows:
        if r["created_at"] + r["retention_days"] * 86400 <= now_ts:
            delete_case(r["id"])
            n += 1
    return n


# ---- notes / clips -------------------------------------------------------
def add_note(case_id: int, author_id: int, t: float, text: str) -> int:
    with session() as c:
        cur = c.execute("INSERT INTO notes(case_id,author_id,t_seconds,text,created_at) VALUES (?,?,?,?,?)",
                        (case_id, author_id, t, text.strip(), now()))
        return int(cur.lastrowid)


def list_notes(case_id: int) -> list[sqlite3.Row]:
    with session() as c:
        return c.execute(
            "SELECT n.*, u.display_name FROM notes n JOIN users u ON u.id=n.author_id WHERE case_id=? ORDER BY t_seconds, n.id",
            (case_id,)).fetchall()


def delete_note(note_id: int, user: dict) -> None:
    with session() as c:
        if user["role"] == "admin":
            c.execute("DELETE FROM notes WHERE id=?", (note_id,))
        else:
            c.execute("DELETE FROM notes WHERE id=? AND author_id=?", (note_id, user["id"]))


def add_clip(case_id: int, author_id: int, start: float, end: float, label: str) -> int:
    if end < start:
        start, end = end, start
    with session() as c:
        cur = c.execute("INSERT INTO clips(case_id,author_id,start_s,end_s,label,created_at) VALUES (?,?,?,?,?,?)",
                        (case_id, author_id, start, end, label.strip(), now()))
        return int(cur.lastrowid)


def list_clips(case_id: int) -> list[sqlite3.Row]:
    with session() as c:
        return c.execute(
            "SELECT c.*, u.display_name FROM clips c JOIN users u ON u.id=c.author_id WHERE case_id=? ORDER BY start_s",
            (case_id,)).fetchall()


def delete_clip(clip_id: int, user: dict) -> None:
    with session() as c:
        if user["role"] == "admin":
            c.execute("DELETE FROM clips WHERE id=?", (clip_id,))
        else:
            c.execute("DELETE FROM clips WHERE id=? AND author_id=?", (clip_id, user["id"]))


# ---- AI reports / references / assistant chat -----------------------------
def add_report(case_id: int, content: dict, user_id: int, *, model: str = "", tokens_in: int = 0, tokens_out: int = 0) -> int:
    with session() as c:
        cur = c.execute(
            "INSERT INTO case_reports(case_id,content_json,status,model,tokens_in,tokens_out,created_by,created_at,updated_at)"
            " VALUES (?,?,?,?,?,?,?,?,?)",
            (case_id, json.dumps(content, ensure_ascii=False), "draft", model, tokens_in, tokens_out, user_id, now(), now()))
        return int(cur.lastrowid)


def latest_report(case_id: int) -> sqlite3.Row | None:
    with session() as c:
        return c.execute("SELECT * FROM case_reports WHERE case_id=? ORDER BY id DESC LIMIT 1", (case_id,)).fetchone()


def update_report(report_id: int, content: dict, *, status: str | None = None, reviewed_by: int | None = None) -> None:
    with session() as c:
        c.execute("UPDATE case_reports SET content_json=?, updated_at=? WHERE id=?",
                  (json.dumps(content, ensure_ascii=False), now(), report_id))
        if status:
            c.execute("UPDATE case_reports SET status=?, reviewed_by=? WHERE id=?", (status, reviewed_by, report_id))


def save_refs(case_id: int, items: list[dict]) -> None:
    with session() as c:
        c.execute("DELETE FROM case_refs WHERE case_id=?", (case_id,))
        c.execute("INSERT INTO case_refs(case_id,items_json,fetched_at) VALUES (?,?,?)",
                  (case_id, json.dumps(items, ensure_ascii=False), now()))


def load_refs(case_id: int) -> tuple[list[dict], int] | None:
    with session() as c:
        r = c.execute("SELECT * FROM case_refs WHERE case_id=? ORDER BY id DESC LIMIT 1", (case_id,)).fetchone()
    return (json.loads(r["items_json"]), r["fetched_at"]) if r else None


def add_chat(case_id: int, user_id: int, role: str, content: str, sources: list | None = None,
             tokens_in: int = 0, tokens_out: int = 0) -> int:
    with session() as c:
        cur = c.execute(
            "INSERT INTO chat_messages(case_id,user_id,role,content,sources_json,tokens_in,tokens_out,created_at) VALUES (?,?,?,?,?,?,?,?)",
            (case_id, user_id, role, content, json.dumps(sources or [], ensure_ascii=False), tokens_in, tokens_out, now()))
        return int(cur.lastrowid)


def list_chat(case_id: int, user_id: int) -> list[sqlite3.Row]:
    """Each doctor sees only their own conversation about a case."""
    with session() as c:
        return c.execute("SELECT * FROM chat_messages WHERE case_id=? AND user_id=? ORDER BY id", (case_id, user_id)).fetchall()


def clear_chat(case_id: int, user_id: int) -> None:
    with session() as c:
        c.execute("DELETE FROM chat_messages WHERE case_id=? AND user_id=?", (case_id, user_id))
