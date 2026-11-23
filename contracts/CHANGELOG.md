# Contracts changelog

Owner: **Member D** (WBS 1.2.2). Every change to `contracts/` is its own PR, approved by D **and** every affected consumer.

## 1.0.0-draft — repository setup (Mon 23 Nov 2026)

Initial drafts of C1–C6, taken from the WBS "Interface contracts" section. Fixtures in `tests/fixtures/` are synthetic and validate against these schemas.

| File | Contract | Producer | Consumers |
|---|---|---|---|
| `classes.json` | C1 class map + UI colours | D | A, B, C, D |
| `dataset_layout.md` | C2 YOLO dataset layout | A | B |
| `presence.schema.md` | C3 timeline ground-truth CSV | A | C |
| `detections.schema.json` | C4 detections.jsonl + `detect_video()` signature | B | C |
| `timeline.schema.json` | C5 timeline JSON | C | C, D, A |
| `openapi.yaml` | C6 HTTP API | D drafts, C implements | D, A |

Freeze target: **Mon 23 Nov 23:00 (milestone M1)**.

### Sign-off (WBS 1.2.2 acceptance criterion — tick these in the 1.2.2 PR)

- [ ] Member A — C1, C2, C3
- [ ] Member B — C1, C4
- [ ] Member C — C3, C4, C5, C6
- [ ] Member D — C1, C5, C6

Bump `version` in `classes.json` / `openapi.yaml` to `1.0.0` once all four boxes are ticked.

## Template for later changes

```
## 1.0.1 — <date> — <PR link>
Changed: <file + field>
Why: <reason>
Approved by: D, <every affected consumer>
```
