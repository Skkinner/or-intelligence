#!/usr/bin/env bash
# Assemble the files of the Hugging Face Space (Docker SDK) into mibda-platform/deploy/out/hf-space/.
# Upload the CONTENTS of that folder to the Space. No secrets, data or model weights are copied.
set -euo pipefail
cd "$(dirname "$0")/.."

OUT=deploy/out/hf-space
rm -rf "$OUT"
mkdir -p "$OUT/models"

cp deploy/hf-space/README.md "$OUT/README.md"
cp Dockerfile.api "$OUT/Dockerfile"
cp .dockerignore requirements.txt datasets.yaml procedures.yaml "$OUT/"
cp -r api or_intelligence scripts "$OUT/"
cp models/phase_estimator.json models/phase_metrics.json "$OUT/models/"

find "$OUT" -name "__pycache__" -type d -prune -exec rm -rf {} +
find "$OUT" -name "*.pyc" -delete

# Safety check: nothing secret or heavy may end up in the Space.
if find "$OUT" \( -name ".env" -o -name "*.pt" -o -name "*.db" \) | grep -q .; then
  echo "ERROR: secret, weights or database file found in $OUT" >&2
  exit 1
fi
echo "Space files ready in mibda-platform/$OUT ($(find "$OUT" -type f | wc -l) files)"
