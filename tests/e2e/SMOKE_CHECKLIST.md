# End-to-end smoke checklist (Owner: Member D, WBS 6.3.1)

Run on the integrated build (`scripts/run_local.*`, INFERENCE_MODE=real). File each failure as a Bug issue for the owning member (fix by Wed 18:00).

| # | Use case | Steps | Pass |
|---|---|---|---|
| 1 | Review | upload → status done → timeline visible; click a clipper bar seeks the video | ☐ |
| 2 | Notes + report | add a note → appears on the timeline and in the EN and AR PDF | ☐ |
| 3 | Library | search clipper → result opens Review at the timestamp | ☐ |
| 4 | Unusual patterns | long irrigation segment is highlighted | ☐ |
| 5 | Analytics | 2 cases compared, totals match the API | ☐ |

Automated: `tests/e2e/core.spec.ts` (upload → timeline → click bar).

