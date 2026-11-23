<!-- Title format: [WBS 4.1.1] Temporal smoothing  ·  target branch: develop -->

## WBS task

Closes #<issue number> — WBS `x.y.z` · Owner: Member <A|B|C|D>

## What changed

-

## Scope check

- [ ] This PR only touches paths I own (see `TEAM_TASKS.md` / `.github/CODEOWNERS`)
- [ ] No `data/`, frames, videos, `*.pt` / `*.onnx` weights or secrets committed
- [ ] Contract files (`contracts/`) unchanged — or this is a separate contract PR approved by D + every affected consumer, logged in `contracts/CHANGELOG.md`
- [ ] Under ~400 changed lines where possible

## Tests and acceptance evidence

- [ ] `ruff check .` and `pytest -m "not gpu and not data"` pass locally (Python changes)
- [ ] `npm run build` and `npm test` pass in `web/` (web changes)
- [ ] Acceptance criteria from the issue ticked, with evidence below (numbers, screenshots, logs)

<!-- paste evidence here: metrics tables, screenshots (Arabic pages: required), command output -->

## Hand-off

- [ ] Tagged the member(s) who need this output (see "Hands off to" in the issue)
