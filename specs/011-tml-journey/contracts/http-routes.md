# HTTP routes: TML journey

| Method | Path | Screen | Result |
|---|---|---|---|
| GET | `/m/{user_id}/journey?stage=` | S-105 | Stage chips, counts, week blocks; an unknown stage falls back to the current one; 303 to setup without a due date |
| GET | `/m/{user_id}/journey/album?stage=&print=1` | S-105 export | Print-ready page; 303 to S-105 when the stage has nothing to export; nothing stored |
