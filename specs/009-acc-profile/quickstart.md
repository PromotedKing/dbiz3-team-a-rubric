# Quickstart: ACC profile

```bash
uv sync
uv run python -m pytest
uv run python -m uvicorn mb360.main:app --app-dir app --reload
```

Open http://127.0.0.1:8000/, choose a mother, narrow the browser to phone width.

1. **Hồ sơ** tab: name, medical record number, week, due date, hospital record link.
2. **Sửa ›**: name and phone are read-only; for a linked mother the due date is locked; change the height, **Lưu thay đổi**.
3. **Nhắc nhở & thông báo**: "Phản hồi báo cáo" is locked on; toggle another switch, reload, it stays.
4. **Từ bác sĩ** tab: filter by type, open a notification (it becomes read, the badge drops), **Đánh dấu đã đọc tất cả**.
