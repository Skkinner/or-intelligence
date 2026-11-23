#!/usr/bin/env bash
# Owner: Member D (8.1.4). Builds docs/report/report.pdf with pandoc.
set -euo pipefail
cd "$(dirname "$0")"
pandoc main.md 00_intro.md 01_data.md 02_model.md 03_system.md 04_frontend_conclusion.md \
  --resource-path=..:../data:../model:../timeline --toc -o report.pdf
echo "wrote docs/report/report.pdf"
