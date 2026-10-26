# Quickstart: ALR status (US-2)

Same install as `specs/001-alr-core/quickstart.md`, then:

```bash
uv run tools/start_feature.py --use specs/003-alr-status
uv run python -m pytest
uv run python -m uvicorn mb360.main:app --app-dir app --reload
```

Use `python -m` (Windows Smart App Control blocks the `.exe` shims — readiness report W1).

## Validation scenarios

| # | Steps | Expected |
|---|---|---|
| 1 | http://127.0.0.1:8000/ → **Nguyễn Thị Lan** → "My reports" | her reports and her chatbot case, newest first; "128/82 mmHg … No action needed" without a link |
| 2 | Filter "Resolved", then type "Chatbot" | only resolved rows; only chatbot rows |
| 3 | Open the resolved 150/95 report | S-026: progress Not viewed → Viewed (Nurse Trần Thị B) → "No doctor escalation needed" → Resolved; "Response from Nurse Trần Thị B"; no Safety note |
| 4 | Open her Not viewed symptom report | Viewed / Escalated / Resolved pending; Safety note shown |
| 5 | Clinical web `/staff` → nurse → mark her case as viewed and send guidance → back to S-026 | progress shows Viewed with the nurse; the response replaces the Safety note |
