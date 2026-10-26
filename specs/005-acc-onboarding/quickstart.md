# Quickstart: ACC onboarding (US-1, US-2)

Same install as `specs/001-alr-core/quickstart.md`, then:

```bash
uv run tools/start_feature.py --use specs/005-acc-onboarding
uv run python -m pytest
uv run python -m uvicorn mb360.main:app --app-dir app --reload
```

Open http://127.0.0.1:8000/tci (simulated TCI app).

## Validation scenarios

| # | Steps | Expected |
|---|---|---|
| 1 | Simulate a new TCI account (any invented name, sex Female) → tap "Mother & Baby 360" | "Connect to your TCI account" sheet listing full name, date of birth, phone number; medical record number; prenatal visit results |
| 2 | Tap "Agree & continue" without ticking the box | error at the checkbox; nothing saved |
| 3 | Tick the box → "Agree & continue" | onboarding guide (4 pages) → "Skip" → Pregnancy setup |
| 4 | "I know the first day of my last period" → 01/04/2026 | card "Week 25 · day 4", "Today 27/09/2026 · Due 06/01/2027" |
| 5 | Confirm (height / weight empty) | Home "Hello, …!" with "Week 25" and "Due date: 06/01/2027" |
| 6 | Back to `/tci` → open as **Nguyễn Thị Lan** | Home directly (returning mother) |
| 7 | Open as **Hoàng Thu Trang** (no due date) | Pregnancy setup |
| 8 | Simulate an account with sex Male | "Mother & Baby 360 is for expectant mothers." + "Back to TCI app"; nothing saved |
| 9 | Tap "Later" on the consent sheet | back to `/tci`; nothing saved |
