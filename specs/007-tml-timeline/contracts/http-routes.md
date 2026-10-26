# HTTP routes: TML timeline (US-1, US-2)

| Method | Path | Screen | Behaviour | Spec |
|---|---|---|---|---|
| GET | `/m/{user_id}/timeline?week=&saved=` | S-048 | current week by default; "‹ Week N−1" / "Week N+1 ›" (hidden at 0 / 42); "Week N" + date range; indicators by day; visit cards or "No visit this week."; Messages to Baby (read-only); diary entries + "+ Add diary entry"; "Diary entry saved" when `saved=1` | FR-002 – FR-006, FR-012 |
| GET | `/m/{user_id}/diary/new` | S-051 / S-052 | "Week N – current week", "Date dd/mm/yyyy (automatic)", content, mood, photos (Take photo / Library = file input), Cancel / Save diary entry | FR-008, FR-009 |
| POST | `/m/{user_id}/diary` | S-051 → S-053 | multipart: `text`, `mood`, `photos` (0 – 5 files); invalid → 422 with field errors, nothing saved; valid → 303 `/m/{user_id}/timeline?saved=1` | FR-009, FR-010, BR-002, BR-005 |
| GET | `/media/{path}` | — | serves an uploaded photo from `media/` | FR-009 |

S-008: the week card links to S-048 (D-75).
