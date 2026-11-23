# Contributing

Small team, short deadline, simple rules: **one task = one branch = one PR**, and **only edit files you own**.

## Branches

| Branch | Purpose | Who merges |
|---|---|---|
| `main` | Releases only (tag `v1.0.0` on Wed 20:00) | Member D, via PR from `develop` |
| `develop` | Integration branch. All PRs go here. | Member D at the merge windows |
| `feature/member-<a\|b\|c\|d>-<wbs-id>-<slug>` | One per WBS task, e.g. `feature/member-c-4.1.1-smoothing` | — |

The exact branch name of every task is in its GitHub Issue and in [TEAM_TASKS.md](TEAM_TASKS.md).
Merge windows: **Mon 23:00 · Tue 13:00 · Tue 21:00 · Wed 12:00 · Wed 18:00 (feature freeze)**.

## 1. Clone (once)

```bash
git clone https://github.com/<owner>/or-intelligence.git
cd or-intelligence
git config user.name "Your Name"
git config user.email "you@example.com"
```

Then set up your environment (see README "Installation").

## 2. Start a task

Pick your issue (filter by label `member:a`, `member:b`, …). Then:

```bash
git switch develop
git pull
git switch -c feature/member-a-2.2.1-voc-to-yolo
```

## 3. Work

- Open the files listed in the issue under "Files to modify". Search for `TODO(<you>, <wbs>)`.
- Do not edit anyone else's files, including to "just fix" something. Open a Bug issue for the owner instead.
- Develop against `contracts/` and `tests/fixtures/`, not against teammates' unfinished code.
- Never commit `data/`, frames, videos, `*.pt`/`*.onnx` weights, `.env` or tokens. CI rejects them.

Before committing:

```bash
ruff check .
pytest -m "not gpu and not data"
cd web && npm run build && npm test && cd ..      # only if you changed web/
```

## 4. Commit and push

```bash
git add src/data/convert_voc_to_yolo.py tests/unit/data/test_convert.py
git commit -m "[WBS 2.2.1] Convert VOC boxes to YOLO labels"
git push -u origin feature/member-a-2.2.1-voc-to-yolo
```

Add files by name (not `git add .`) so you never commit data or someone else's file by accident.
Push often; a pushed branch is a backup.

## 5. Open a Pull Request

On GitHub, click **Compare & pull request**, or:

```bash
gh pr create --base develop --title "[WBS 2.2.1] VOC → YOLO conversion & class mapping" --body "Closes #<issue>"
```

- Base branch: **`develop`** (never `main`).
- Fill in the PR template: scope check, tests, acceptance evidence (numbers/screenshots).
- CODEOWNERS requests the right reviewer automatically. 1 approval + green CI are required.
- If your task hands off to someone, tag them in the PR.

## 6. Keep your branch up to date

If `develop` moved while you worked:

```bash
git fetch origin
git rebase origin/develop
git push --force-with-lease
```

`--force-with-lease` is only for **your own** feature branch. Never force-push `develop` or `main`.

## 7. After merge

```bash
git switch develop
git pull
git switch -c <next task branch>
```

The issue closes automatically through `Closes #<n>`.

## Shared-file rules

| Path | Owner | Rule |
|---|---|---|
| `contracts/` | D | Separate PR, approved by D **and** every affected consumer; log it in `contracts/CHANGELOG.md` |
| `web/package.json` | D | Member A requests new npm packages with a PR touching only `package.json` + lockfile |
| `requirements/base.txt` | D | Add packages only to your own `requirements/{data,ml,api}.txt` |
| `.github/` | D | CI and CODEOWNERS changes by D only (`node scripts/github/generate.mjs`) |
| `scripts/`, `docker/`, `docker-compose.yml` | D | Member C requests API start-up changes by issue; D implements |
| `src/inference/` | B | Member C imports `detect_video()`; signature changes need a contract PR first |
| `src/timeline/evaluate.py` | C | Member B calls it read-only for the benchmark |

## Blocked?

Blocked for more than 30 minutes: post in the team chat and tag the producer of the input you need.
Stand-ups: 09:00 Tue and Wed (10 min: yesterday / today / blocked).
