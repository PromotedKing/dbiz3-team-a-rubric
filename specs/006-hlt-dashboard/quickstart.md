# Quickstart: HLT dashboard (US-1, US-2)

Same install as `specs/001-alr-core/quickstart.md`, then:

```bash
uv run tools/start_feature.py --use specs/006-hlt-dashboard
uv run python -m pytest
uv run python -m uvicorn mb360.main:app --app-dir app --reload
```

## Validation scenarios

| # | Steps | Expected |
|---|---|---|
| 1 | `/` → **Nguyễn Thị Lan** → Home → "Health metrics ›" | S-023: Latest visit results 15/09/2026 "From visit": Blood pressure 132/84 mmHg Normal, Fetal heart rate 145 bpm (reference range 110–160 bpm) with no label, Weight 56.5 kg, Blood glucose —, Urine protein Negative Normal; "2 metrics: Blood glucose, Blood pressure"; My reports card; Self-tracked: Weight 57.0 kg, Temperature 36.8 °C, Heart rate 82 bpm, Sleep 7 h 30 min |
| 2 | "⟳ Refresh" | "Data updated." |
| 3 | "+ Enter self-tracked metrics" → weight 57.4 → Save metrics | "Metrics saved"; Weight card 57.4 kg; no report, no case |
| 4 | Sleep: bedtime only → Save | error: wake-up time needed |
| 5 | Hoàng Thu Trang after her setup (no visit) | "No visit results yet." |
