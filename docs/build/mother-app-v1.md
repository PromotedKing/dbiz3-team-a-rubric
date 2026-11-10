# Mother app v1.0.0: how to run and what to review

One complete mobile flow for the mother, built from `screens/ui-final/` (D-80, D-81).

## Run

```bash
uv sync
uv run python -m uvicorn mb360.server:app --app-dir app --port 8000
```

Open http://127.0.0.1:8000/ . On a computer it shows a phone frame; on a phone (same Wi-Fi, add `--host 0.0.0.0`) it fills the screen and can be added to the home screen. "Chạy lại từ lần mở đầu tiên" beside the frame restores the sample data. Data stays in `.local/` between restarts.

Tests: `uv run python -m pytest` → `470 passed, 2 xfailed` (09/11/2026; one warning from Starlette about `httpx`, harmless).

`mb360.main:app` is still the plain app of the seed and the tests. The clinical web is at `/staff`, on the same data: a nurse's or doctor's answer appears in the mother's app.

## Put it on the internet

Render Web Service from `render.yaml` (why: `adr-hosting.md`; errors met: `local-vs-internet.md`).

1. On render.com, sign in with GitHub and allow access to this repository.
2. **New → Blueprint**, choose the repository; Render reads `render.yaml`. Apply it.
3. Read the generated `MB360_STAFF_PASSWORD` on the service's Environment page. `/staff`, the reset button and `/tci/accounts` ask for it (any user name). Share it only inside the team.
4. Chatbot with Groq, free (D-84): on https://console.groq.com/keys create a key, then on Render's **Environment** page add `GROQ_API_KEY` (never in the repository). `GROQ_MODEL` is set by `render.yaml`. Groq is used first when its key is set.
5. Chatbot with Gemini instead (D-83): on https://aistudio.google.com/apikey click **Create API key**, then on Render's **Environment** page add `GEMINI_API_KEY` with that key (never in the repository). `GEMINI_MODEL` is set by `render.yaml`. The panel beside the phone shows which chatbot answers. To check a key on a team machine: put it in a local `.env` (git-ignored) and run `uv run python app/mb360/bot/llm.py`.
6. Open the `https://….onrender.com` link on a phone over mobile data and run one flow. Add what fails to `local-vs-internet.md`.

Every push to the branch named in `render.yaml` deploys again and returns the data to the sample state.

**Tell the people who try it:** on Render's free plan the data is not kept. A deploy, a restart, or the service waking up after 15 minutes without visits brings back the sample data, so reports, diary entries and photos made during a test can disappear (`adr-hosting.md`). The first page after a pause takes about a minute.

`render.yaml` deploys `branch: sang/mother-app-v1`. After PRs #15 – #20 are merged, change it to `branch: main` in a pull request (`merge-guide.md` §4), then check on Render that the service follows `main`.

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

## Clinical overview UI review — 11/11/2026

User-approved visual update: neutral bordered KPI cards, orange reserved for above-threshold cases, muted chart bars with explicit labels/counts, consistent typography/spacing and dropdown chevron. Section order stays: KPIs → status/attention → Handle next/By source; By source has content-driven height. Counts, filters, case priority order and destinations are unchanged. Internal THRESHOLD_RULE implementation text is removed from the displayed KPI; threshold evaluation still uses the rule table. Downstream files: `templates/staff_dashboard.html`, `static/staff.css`. No schema, seed or clinical-rule changes.
