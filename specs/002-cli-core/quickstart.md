# Quickstart: CLI core (US-1, US-2)

Same install as `specs/001-alr-core/quickstart.md` (§1 – §3): `git clone …`, `uv sync`, then:

```bash
uv run tools/start_feature.py --use specs/002-cli-core
uv run pytest
uv run uvicorn mb360.main:app --app-dir app --reload
```

Open http://127.0.0.1:8000/staff (clinical web) — the mother side stays at http://127.0.0.1:8000/.

## Validation scenarios

| # | Steps | Expected |
|---|---|---|
| 1 | Choose nurse **Trần Thị B** | S-061 "Cases to handle", header "Nurse: Trần Thị B", filter All, newest first |
| 2 | Click "Not viewed" | only Not viewed cases (Ngô Thị Thảo's 140/90 case among them) |
| 3 | Open Ngô Thị Thảo's case → "Mark as viewed" | status Viewed |
| 4 | "Escalate to doctor" | status Escalated to doctor; "Close case" no longer available to the nurse |
| 5 | Back to `/staff`, choose **Dr. Phạm Quốc Dũng** (her responsible doctor) | default filter Escalated to doctor; "Notifications" count includes her case |
| 6 | Open it → "Send guidance" with a template → "Close case" | the response is saved, status unchanged after guidance; Resolved after close |
| 7 | Open a chatbot case (nurse) | the mother's question and the whole conversation |
| 8 | Mother side: report a new symptom for any mother, then refresh the nurse queue | the new case appears at the top, Not viewed |
