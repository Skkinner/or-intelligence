#!/usr/bin/env bash
# Owner: Member D (WBS 7.1.1). One-command local run: API on :8000, web on :8080 (proxying /api).
# Usage: ./scripts/run_local.sh            (INFERENCE_MODE=fixture by default; set real after M4)
set -euo pipefail
cd "$(dirname "$0")/.."

export INFERENCE_MODE="${INFERENCE_MODE:-fixture}"
export STORAGE_DIR="${STORAGE_DIR:-storage}"

# TODO(D, 7.1.1): create/activate .venv and install requirements/api.txt (+ ml.txt for real mode)
if [ "$INFERENCE_MODE" = "real" ]; then
  python -m src.inference.fetch_weights   # Member B, 3.3.2
fi

python -m uvicorn src.api.main:app --host 0.0.0.0 --port 8000 &
API_PID=$!
trap 'kill $API_PID 2>/dev/null || true' EXIT

cd web
[ -d node_modules ] || npm ci
VITE_API_MOCK=0 npm run build
npm run preview -- --host 0.0.0.0
