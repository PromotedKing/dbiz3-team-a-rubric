# Quickstart: TML timeline (US-1, US-2)

Same install as `specs/001-alr-core/quickstart.md`, then:

```bash
uv run tools/start_feature.py --use specs/007-tml-timeline
uv run python -m pytest
uv run python -m uvicorn mb360.main:app --app-dir app --reload
```

## Validation scenarios

| # | Steps | Expected |
|---|---|---|
| 1 | `/` → **Nguyễn Thị Lan** → Home → tap the week card | S-048 "Week 28", "27/09/2026 – 03/10/2026"; indicators of 27/09/2026 (Weight 57.0 kg · Self-entered …); "No visit this week."; Messages to Baby (From Mom, From Dad); 2 diary entries |
| 2 | "‹ Week 27" twice | Week 26 "13/09/2026 – 19/09/2026": visit card "Visit 15/09/2026" From visit, indicators of 15/09/2026 |
| 3 | Week 22 | visit card with the ultrasound placeholder, "Fetal length — 27 cm", "Estimated weight — 480 g", "Measurements per ultrasound report dated 18/08/2026" |
| 4 | From week 22 → "+ Add diary entry" | "Week 28 – current week", "Date 27/09/2026 (automatic)" |
| 5 | Content "Short walk today", mood Calm, one PNG photo → Save diary entry | "Diary entry saved"; back on week 28 with the new entry and its photo |
| 6 | Save with empty content | error; nothing saved |
