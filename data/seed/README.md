# Seed data — Mother & Baby 360

Mockup data for the schema `data/schema/schema-MB360.sql`. The model behind it is `data/data-model-MB360.md` (§10 describes the mockup data, §8 the business rules it exercises).

## Files

| File | Content |
|---|---|
| `NN_{TABLE}.csv` (26 files) | One file per table. `NN` is the foreign-key order, so the files load in filename order. UTF-8, LF, header = column names of the schema, rows sorted by primary key. An empty cell is NULL; BOOLEAN is `1` / `0`; dates are `YYYY-MM-DD`, date-times `YYYY-MM-DD HH:MM`. |
| `generate_seed.py` | The generator. Every CSV file and `seed-report.md` is written by it — do not edit them by hand. |
| `seed-report.md` | Written by the generator: load test, row kinds per table, the reason for every non-ordinary row, the edge-case register (every enumerated value, empty states, boundaries, business rules) and the scenario coverage. |

## Commands

Run from the repository root. Python 3.8 or later, standard library only; on Windows use `python` instead of `python3`. `uv run` works the same way.

```
python3 data/seed/generate_seed.py            # run every check, then (re)write the CSV files and seed-report.md
python3 data/seed/generate_seed.py --check    # run every check, write nothing, confirm the files equal a fresh run
python3 data/seed/generate_seed.py --db /tmp/mb360.db   # also write a loaded SQLite database (outside the repository)
python3 tools/check_data_model.py             # diagram check of the data model (section 5) and seed load
```

## Reproducibility

### Appointment demo cases (Part A, 10/11/2026)

U11 (`tci-000133`, Nguyễn Thị An Nhiên) has a simulated appointment at 09:00 on startup day + 1. U04 (`tci-000126`, Phạm Ngọc Mai) is the no-appointment control and keeps her stored EDD. Both are in the four CSV mothers. The server adds the Nguyễn Thị Mai persona, for five mothers on a fresh demo. The generator writes the fixture to `appointment-demo.json`; the host resolves relative dates with the Vietnam app clock at first install.

The 26 CSVs contain 141 rows. `seed-report.md` lists each reduced-demo row-kind and ENUM exception and the tests that cover the corresponding behavior where available.

The demo creates U11's unread `Appointment` notification at startup, and checks due reminders again on Home / S-009 access. This is request-driven demo behavior, not a background production delivery service. Disabled `appointment_reminder` prevents new reminders; received notices remain visible (demo assumption, S-010 Q4 still open). Reopening a database preserves its dates, switches and read state; a fresh Render deploy recreates tomorrow's case. Details, manual steps and limitations: `docs/build/appointment-part-a.md`.

`generate_seed.py --check` verifies the generated JSON as well as the CSVs and report. Never edit the JSON by hand either.

- No random numbers: the data is written out in the generator, with a fixed clock (2026-09-27 10:00). UUIDs are uuid5 of readable labels (U01, C1, RPT-002 …), so they never change.
- A re-run writes the same bytes: after `python3 data/seed/generate_seed.py`, `git status` shows no change (Session 6 test T2). The generator writes no database and no cache inside the repository.
- Before writing, the generator checks the foreign keys, the keys and the business rules listed in §8 of the data model, recomputes the threshold label of every report from THRESHOLD_RULE, then creates the schema in an empty in-memory SQLite database and loads every file in filename order with foreign keys on (gate G3). If anything fails it stops and writes nothing.

## Privacy

Every person and value is invented (see §11 of the data model). S01 "Trần Thị B" and S02 "Nguyễn Văn A" are the placeholder names drawn in the wireframes. Phone numbers follow the fictitious pattern 0900 000 1xx.
