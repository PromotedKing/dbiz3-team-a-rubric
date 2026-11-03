# Mother app v1.0.0: how to run and what to review

One complete mobile flow for the mother, built from `screens/ui-final/` (D-80, D-81).

## Run

```bash
uv sync
uv run python -m uvicorn mb360.server:app --app-dir app --port 8000
```

Open http://127.0.0.1:8000/ . On a computer it shows a phone frame; on a phone (same Wi-Fi, add `--host 0.0.0.0`) it fills the screen and can be added to the home screen. "Chạy lại từ lần mở đầu tiên" beside the frame restores the sample data. Data stays in `.local/` between restarts.

`mb360.main:app` is still the plain app of the seed and the tests. The clinical web is at `/staff`, on the same data: a nurse's or doctor's answer appears in the mother's app.

## The flow

TCI home → tile Mẹ & Bé 360 → consent → guide (3 pages) → pregnancy setup → Home. The next opening goes straight to Home.

| Tab | Screens |
|---|---|
| Trang chủ | Home, Report (4 tabs), Metric alert, Report status, Self-tracked metrics, Metric history, Health metrics, close dialog |
| Timeline | Week strip, Day detail, Add diary, My journey, Album |
| Chatbot | Conversation, danger card, hand-off to a nurse |
| Từ bác sĩ | Notices, Notice detail, My reports |
| Hồ sơ | Profile, Doctor's instructions, Edit profile, Notification settings |

## Before real use

- Medical text is invented sample data (guidance, doctors' answers, `LocalAnswers`): needs hospital review. Chatbot keywords are still provisional (D-47).
- Hotline number: `1900 xxxx` until the hospital gives one (BOT Q8).
- The TCI identity is simulated (spec-ACC §10 Q9); `mb360/tci_feed.py` stands in for the host app.
- The album is a print page; the browser saves the PDF (FR-014 partly met).
