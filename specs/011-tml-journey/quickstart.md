# Quickstart: TML journey

```bash
uv sync
uv run python -m pytest
uv run python -m uvicorn mb360.main:app --app-dir app --reload
```

Open http://127.0.0.1:8000/, choose a mother, narrow the browser to phone width.

1. **Timeline › Hành trình của mẹ** (or **Hồ sơ › Xuất album kỷ niệm**): the current stage opens with its counts and weeks.
2. Change the stage. A stage not reached yet, or one with no content, disables the export.
3. **Xuất album PDF**: the album page opens with the browser's print sheet; choose "Save as PDF".
