"""Local accounts with salted PBKDF2 password hashes and three roles."""
from __future__ import annotations

import hashlib
import hmac
import os
import sqlite3

from . import db

ROLES = ("trainee", "instructor", "admin")
_ITER = 200_000


def _hash(password: str, salt: bytes) -> str:
    return hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, _ITER).hex()


def create_user(username: str, password: str, role: str, display_name: str | None = None) -> int:
    if role not in ROLES:
        raise ValueError(f"role must be one of {ROLES}")
    username = username.strip().lower()
    if not username or len(password) < 8:
        raise ValueError("username required and password must be at least 8 characters")
    salt = os.urandom(16)
    with db.session() as c:
        cur = c.execute(
            "INSERT INTO users(username,display_name,role,salt,pw_hash,created_at) VALUES (?,?,?,?,?,?)",
            (username, display_name or username, role, salt.hex(), _hash(password, salt), db.now()))
        return int(cur.lastrowid)


def _row_to_user(r: sqlite3.Row) -> dict:
    return {"id": r["id"], "username": r["username"], "display_name": r["display_name"], "role": r["role"]}


def authenticate(username: str, password: str) -> dict | None:
    with db.session() as c:
        r = c.execute("SELECT * FROM users WHERE username=?", (username.strip().lower(),)).fetchone()
    if r is None:
        # keep timing similar for unknown users
        _hash(password, b"\x00" * 16)
        return None
    ok = hmac.compare_digest(_hash(password, bytes.fromhex(r["salt"])), r["pw_hash"])
    return _row_to_user(r) if ok else None


def list_users() -> list[dict]:
    with db.session() as c:
        return [_row_to_user(r) for r in c.execute("SELECT * FROM users ORDER BY id").fetchall()]


def get_user(user_id: int) -> dict | None:
    with db.session() as c:
        r = c.execute("SELECT * FROM users WHERE id=?", (user_id,)).fetchone()
    return _row_to_user(r) if r else None


def user_exists(username: str) -> bool:
    with db.session() as c:
        return c.execute("SELECT 1 FROM users WHERE username=?", (username.strip().lower(),)).fetchone() is not None
