# Quickstart: HLT history

```bash
uv sync
uv run python -m pytest
uv run python -m uvicorn mb360.main:app --app-dir app --reload
```

Open http://127.0.0.1:8000/, choose a mother, narrow the browser to phone width.

1. **Chỉ số sức khỏe › Xem lịch sử chỉ số**: blood pressure with the 140/90 line, statistics and measurements.
2. Change the dates: list, statistics and chart follow. A range with no data shows the empty state.
3. Choose **Cân nặng**: no threshold line, no threshold label. Choose **Tim thai**: reference lines, no label.
4. **Chỉ dẫn của bác sĩ**: each card shows the doctor, the date, the latest report and a history link.
