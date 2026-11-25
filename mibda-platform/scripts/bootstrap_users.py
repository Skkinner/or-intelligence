"""Create the platform's accounts from environment secrets (for online deployments).

Unlike seed_demo.py, no password is written in the code. For each role whose password variable is set,
the account is created if it does not exist yet:

  ORI_ADMIN_PASSWORD       -> user "admin"       (role admin)
  ORI_INSTRUCTOR_PASSWORD  -> user "instructor"  (role instructor)
  ORI_TRAINEE_PASSWORD     -> user "trainee"     (role trainee)

Passwords must be at least 8 characters. Set them as secrets on the host (e.g. Hugging Face Space secrets).
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from or_intelligence import auth, db  # noqa: E402

ACCOUNTS = [
    ("admin", "ORI_ADMIN_PASSWORD", "admin", "Admin"),
    ("instructor", "ORI_INSTRUCTOR_PASSWORD", "instructor", "Instructor"),
    ("trainee", "ORI_TRAINEE_PASSWORD", "trainee", "Trainee"),
]


def main() -> None:
    db.init_db()
    for username, var, role, name in ACCOUNTS:
        pw = os.environ.get(var, "")
        if not pw:
            continue
        if auth.user_exists(username):
            print(f"{username}: already exists")
            continue
        auth.create_user(username, pw, role, name)
        print(f"{username}: created")
    if not any(os.environ.get(v) for _, v, _, _ in ACCOUNTS) and os.environ.get("ORI_SEED_DEMO") != "1":
        print("No ORI_*_PASSWORD secrets set: no accounts created (nobody can sign in).")


if __name__ == "__main__":
    main()
