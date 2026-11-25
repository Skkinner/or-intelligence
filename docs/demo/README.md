# Live demo (WBS 7.2.1, 8.2.2)

The demo is given **live** from the `mibda-platform/` app. No recorded demo video is submitted.

## Before the demo

- `mibda-platform/models/best.pt` is in place (live detection needs it).
- `mibda-platform/.env` has `ANTHROPIC_API_KEY` and `ORI_ALLOW_EXTERNAL_AI=1` (only for the AI case report).
- Demo cases are seeded (`python scripts/seed_demo.py ...`, see `mibda-platform/README.md`).
- Start the app from inside `mibda-platform/`: `streamlit run app/main.py`
  (or the API + React app: `python -m uvicorn api.main:app --port 8000`, then `cd web; npm run dev`).

## Demo script (the 5 use cases)

1. **Use case 1:** open a case in Review → click a bar on the instrument timeline → the video jumps to that moment.
2. **Use case 2:** add a timestamped note → export the PDF report in English and Arabic → generate the AI case
   report with Claude, approve it, export it.
3. **Use case 3:** Library → moment search for "clipper" → every clipping segment across cases.
4. **Use case 4:** review flags on the timeline (long use, frequent instrument entries).
5. **Use case 5:** Operation tracker / Compare → time per instrument and per phase across cases.
