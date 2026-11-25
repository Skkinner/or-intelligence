---
title: MIBDA API
emoji: 🩺
colorFrom: red
colorTo: yellow
sdk: docker
app_port: 8000
pinned: false
short_description: Backend API of the MIBDA' surgical video review platform
---

# MIBDA' API (backend)

FastAPI backend of the MIBDA' surgical video review platform: instrument detection (YOLOv8s), timeline, notes,
PDF reports (EN/AR) and the AI case report. The web interface is deployed separately and calls this API under `/api`.

Educational review aid, not a diagnostic system. Trained on public research data (CC BY-NC-SA 4.0): non-commercial use only.

## Space secrets (Settings → Variables and secrets)

| Name | Purpose |
|---|---|
| `ORI_API_SECRET` | Long random string that signs sign-in cookies |
| `ORI_ADMIN_PASSWORD`, `ORI_INSTRUCTOR_PASSWORD`, `ORI_TRAINEE_PASSWORD` | Create the `admin`, `instructor`, `trainee` accounts (8+ characters) |
| `ORI_WEIGHTS_REPO` | Private model repo that holds `best.pt` |
| `HF_TOKEN` | Read token for that model repo |
| `ANTHROPIC_API_KEY` | Claude API key for the AI case report (optional) |
| `ORI_ALLOW_EXTERNAL_AI` | `1` to allow the AI case report (optional) |

Data (cases, notes, accounts created at runtime) is stored inside the container and is reset when the Space restarts.
