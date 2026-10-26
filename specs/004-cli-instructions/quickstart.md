# Quickstart: CLI instructions (US-3)

Same install as `specs/001-alr-core/quickstart.md`, then:

```bash
uv run tools/start_feature.py --use specs/004-cli-instructions
uv run python -m pytest
uv run python -m uvicorn mb360.main:app --app-dir app --reload
```

## Validation scenarios

| # | Steps | Expected |
|---|---|---|
| 1 | `/staff` → **Dr. Phạm Quốc Dũng** → filter "All" → Ngô Thị Thảo's case → "Add / edit instruction": Blood glucose, note "Measure fasting every morning", template "Blood glucose guidance" → Save instruction | the instruction appears in "Doctor's instructions" with "Assigned 27/09/2026 · Dr. Phạm Quốc Dũng" |
| 2 | Mother side `/` → Ngô Thị Thảo → Doctor's instructions | Blood glucose card with the note; "+ Report metric" opens S-025A with Blood glucose |
| 3 | Report fasting glucose 6.0 | S-028 shows the "Blood glucose guidance" template |
| 4 | Nurse **Trần Thị B** opens the same case | instructions listed, no "Edit", no form |
