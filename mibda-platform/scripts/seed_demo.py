"""Create demo accounts and import the CholecT50 challenge-validation videos as demo cases.

  python scripts/seed_demo.py --cholect50 <.../cholect50-challenge-val>

Demo accounts (local use only; change or delete them before any real deployment):
  admin       / DemoAdmin#2026
  instructor  / DemoInstructor#2026
  trainee     / DemoTrainee#2026
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from or_intelligence import auth, db, service  # noqa: E402

DEMO_USERS = [
    ("admin", "DemoAdmin#2026", "admin", "Admin"),
    ("instructor", "DemoInstructor#2026", "instructor", "Dr. Instructor"),
    ("trainee", "DemoTrainee#2026", "trainee", "Resident Trainee"),
]


def seed_users() -> None:
    db.init_db()
    for username, pw, role, name in DEMO_USERS:
        if not auth.user_exists(username):
            auth.create_user(username, pw, role, name)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--cholect50", default=None, help="folder with labels/ and videos/")
    ap.add_argument("--cataract101", default=None, help="unzipped Cataract-101 folder (run inspect_cataract101.py first)")
    ap.add_argument("--limit", type=int, default=None, help="with --cataract101: import only the first N videos")
    a = ap.parse_args()
    seed_users()
    print("Demo users ready.")
    admin = next(u for u in auth.list_users() if u["username"] == "admin")
    if a.cholect50:
        ids = service.import_cholect50(a.cholect50, admin["id"])
        print(f"Imported {len(ids)} new cholecystectomy case(s).")
    if a.cataract101:
        res = service.import_cataract101(a.cataract101, admin["id"], limit=a.limit)
        print(f"Imported {len(res['ids'])} new cataract case(s); skipped {len(res['skipped'])}; "
              f"videos without a matching CSV: {len(res['unmatched'])}")
        for name, why in list(res["skipped"].items())[:5]:
            print(f"  skipped {name}: {why}")


if __name__ == "__main__":
    main()
