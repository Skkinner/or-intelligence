#!/bin/sh
# Container entry point for the FastAPI backend.
set -e
cd "$(dirname "$0")/.."

# Local only: demo accounts with the passwords written in seed_demo.py.
if [ "$ORI_SEED_DEMO" = "1" ]; then python scripts/seed_demo.py; fi

# Online: accounts from ORI_*_PASSWORD secrets, weights from a private model repo.
python scripts/bootstrap_users.py
python scripts/fetch_weights_hf.py

exec uvicorn api.main:app --host 0.0.0.0 --port "${PORT:-8000}" --proxy-headers --forwarded-allow-ips "*"
