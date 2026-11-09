# HTTP routes: HLT history

| Method | Path | Screen | Result |
|---|---|---|---|
| GET | `/m/{user_id}/history?metric=&from=&to=&context=` | S-025 | Chart, statistics, measurements; an unknown metric falls back to Blood pressure; `from` after `to`: 200 with a field error and no data |
| GET | `/m/{user_id}/instructions` | S-027 | Cards with doctor, date, latest report, history link |
