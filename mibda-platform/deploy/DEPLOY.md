# Deploy: React on Vercel + FastAPI on this PC (Docker + Cloudflare Tunnel)

```text
Browser ──► Vercel (React, mibda-platform/web) ──/api/*──► Cloudflare Tunnel ──► this PC: Docker (FastAPI + YOLO)
```

Free. The backend runs in Docker on this PC in **public mode** (no demo login, no demo accounts, its own database).
A Cloudflare quick tunnel gives it a public HTTPS address. Vercel serves the React app and forwards `/api/*` there,
so the sign-in cookie works with no code changes. **The site works only while this PC, Docker Desktop and the tunnel
are running.**

## 1. Passwords (once)

Open `mibda-platform/.env` and type your own passwords (8+ characters, no spaces) after the `=` signs:

```text
ORI_INSTRUCTOR_PASSWORD=...
ORI_ADMIN_PASSWORD=...
```

`ORI_API_SECRET` is already filled in. `.env` is gitignored: never commit or share it.

## 2. Start the backend in public mode

From `mibda-platform/`:

```bash
docker compose -f docker-compose.public.yml up -d --build
```

Check <http://127.0.0.1:8090/api/meta>: it must answer `{"demo":false,...}`.

## 3. Open the tunnel

Install Cloudflare's tunnel tool once (official package):

```bash
winget install --id Cloudflare.cloudflared
```

Open a **new** terminal, then start the tunnel and leave that terminal open:

```bash
cloudflared tunnel --url http://127.0.0.1:8090
```

It prints an address like `https://some-random-words.trycloudflare.com`. That is your public backend address.
It **changes every time** you restart the tunnel (no Cloudflare account needed).

## 4. Point the React app at the tunnel

In `mibda-platform/web/vercel.json`, replace `https://HF-USERNAME-SPACE-NAME.hf.space` with your tunnel address,
keeping `/api/:path*` at the end. Commit and push. Repeat this step whenever the tunnel address changes
(Vercel redeploys automatically after each push).

## 5. Deploy the React app on Vercel (once)

1. <https://vercel.com/new> → **Import** the GitHub repository `or-intelligence` (allow Vercel access to it).
2. **Root Directory**: `mibda-platform/web`. Framework **Vite**; build and output come from `vercel.json`.
3. **Deploy**. No environment variables are needed on Vercel.
4. Open the Vercel URL → sign in as `instructor` with the password from step 1.

## Stop / restart

```bash
docker compose -f docker-compose.public.yml down
```

Stop the tunnel with `Ctrl+C` in its terminal. Data in public mode is kept between restarts (Docker volume
`mibda-public_public-data`).

## Notes

- Detection runs on this PC's CPU (about 120 ms per frame): use short clips (1–2 minutes) in Live analysis.
- Large video uploads pass through Vercel's forwarding: test with a short clip first.
- Model and data licence: CC BY-NC-SA 4.0, non-commercial use only. Educational aid, not diagnostic.
- Local demo (separate, demo accounts on): `docker compose up -d` → <http://localhost:8080>.

## Other hosts (paid)

The same image (`Dockerfile.api`) also runs on **Hugging Face Spaces** (Docker Spaces need a PRO plan; files in
`deploy/hf-space/`, folder built by `deploy/build_hf_space.sh`, weights from a private model repo via
`ORI_WEIGHTS_REPO` + `HF_TOKEN`) or on **Render** (instance with about 2 GB RAM plus a persistent disk).
