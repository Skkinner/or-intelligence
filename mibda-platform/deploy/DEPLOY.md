# Deploy: React on Vercel + FastAPI on Hugging Face Spaces

```text
Browser ──► Vercel (React, mibda-platform/web) ──/api/*──► Hugging Face Space (Docker: FastAPI + YOLO)
```

The browser only talks to Vercel. Vercel forwards `/api/*` to the Space, so the sign-in cookie works with no code
changes. Secrets live only in the Space settings: never in Git, never on Vercel.

## 1. Private model repo for the weights (Hugging Face)

1. <https://huggingface.co/new> → **Model** → name `mibda-weights` → **Private** → Create.
2. **Files → Add file → Upload files** → upload `mibda-platform/models/best.pt` → Commit.
3. Avatar → **Settings → Access Tokens → Create new token** → *Fine-grained* → give **read** access to
   `mibda-weights` only → copy the token (you paste it into the Space in step 3, nowhere else).

## 2. Create the Space

1. <https://huggingface.co/new-space> → name `mibda-api` → SDK **Docker** → template **Blank** →
   hardware **CPU basic (free)** → visibility **Public** (Vercel must be able to reach it).
   A public Space shows its code under *Files*; the weights stay private (step 1) and secrets are never shown.
2. Your API address is `https://<hf-username>-mibda-api.hf.space` (lower case).

## 3. Space secrets

Space → **Settings → Variables and secrets → New secret**:

| Name | Value |
|---|---|
| `ORI_API_SECRET` | a long random string (e.g. 64 random hex characters) |
| `ORI_INSTRUCTOR_PASSWORD` | password for user `instructor` (8+ characters) |
| `ORI_ADMIN_PASSWORD` | password for user `admin` (optional) |
| `ORI_TRAINEE_PASSWORD` | password for user `trainee` (optional) |
| `ORI_WEIGHTS_REPO` | `<hf-username>/mibda-weights` |
| `HF_TOKEN` | the read token from step 1 |
| `ANTHROPIC_API_KEY` | your Claude API key (optional, for the AI case report) |
| `ORI_ALLOW_EXTERNAL_AI` | `1` (optional, enables the AI case report) |

Do **not** set `ORI_DEMO_MODE` or `ORI_SEED_DEMO` online: they allow sign-in without a secret password.

## 4. Upload the backend to the Space

From `mibda-platform/` (Git Bash):

```bash
bash deploy/build_hf_space.sh
```

Then Space → **Files → Add file → Upload files** → drag in **everything inside** `mibda-platform/deploy/out/hf-space/`
(`Dockerfile`, `README.md`, `api/`, `or_intelligence/`, `scripts/`, `models/`, `requirements.txt`, the two `.yaml`
files) → Commit. Replace the Space's own README.md when asked.

The Space builds (about 10 minutes the first time). When it shows **Running**, open
`https://<hf-username>-mibda-api.hf.space/api/meta`: it should answer `{"demo":false,...}`.
The **Logs** tab should show `instructor: created` and `weights: downloaded best.pt`.

## 5. Point the React app at the Space

In `mibda-platform/web/vercel.json`, replace `HF-USERNAME-SPACE-NAME` with your Space address, e.g.
`https://<hf-username>-mibda-api.hf.space/api/:path*`. Commit and push this change to GitHub.

## 6. Deploy the React app on Vercel

1. <https://vercel.com/new> → **Import** the GitHub repository `or-intelligence` (allow Vercel access to it).
2. **Root Directory**: `mibda-platform/web` → Framework **Vite** (build `npm run build`, output `dist`
   come from `vercel.json`).
3. **Deploy**. No environment variables are needed on Vercel.
4. Open the Vercel URL → sign in as `instructor` with the password from step 3.

## Limits of the free setup

- Cases, notes and accounts made in the app are **reset when the Space restarts** (accounts from secrets come back
  automatically). Persistent storage is a paid Space option.
- A free Space **sleeps** after a period without visitors; the first request then takes a minute or two.
- Detection runs on CPU (about 120 ms per frame): use short clips (1–2 minutes) in Live analysis.
- Large video uploads pass through Vercel's forwarding: test with a short clip first.
- Model and data licence: CC BY-NC-SA 4.0, non-commercial use only. Educational aid, not diagnostic.

## Local run (unchanged)

`docker compose up -d` in `mibda-platform/` → <http://localhost:8080> (demo accounts and one-click demo login are
on locally only).
