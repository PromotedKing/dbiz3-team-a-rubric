# Quickstart: ALR core (US-1)

From a fresh clone, on Windows (PowerShell or Git Bash) or macOS (Terminal). The commands are the same on both; only the prerequisite install differs.

## 1. Prerequisites (once per laptop)

- Python 3.11 or later and uv (already checked by T1: `uv run tools/check_env.py --repo`).
- Git.

## 2. Install

```bash
git clone https://github.com/PromotedKing/dbiz3-team-a-rubric.git
cd dbiz3-team-a-rubric
uv sync                                              # creates .venv with the packages of pyproject.toml
uv run tools/start_feature.py --use specs/001-alr-core   # make this the active Spec Kit feature on this laptop
```

## 3. Check the seed (the data the app loads)

```bash
uv run data/seed/generate_seed.py --check   # expect: OK — 26 tables, 272 rows; ... nothing written
```

The app builds its SQLite database from `data/schema/schema-MB360.sql` and `data/seed/*.csv` at start-up; there is no separate load command and no database file in Git.

## 4. Run the tests

```bash
uv run python -m pytest
```

Expected once the slice is built: all tests pass; one test is `xfail` (valid ranges, ALR §10 Q9).

## 5. Start the app

```bash
uv run python -m uvicorn mb360.main:app --app-dir app --reload
```

Use `python -m uvicorn` instead of the `uvicorn.exe` shim: Windows Smart App Control blocks the unsigned shim that uv creates (readiness report W1).

Open http://127.0.0.1:8000, choose a mother, then follow the validation scenarios.

## 6. Validation scenarios (US-1)

| # | Steps | Expected |
|---|---|---|
| 1 | Choose **Ngô Thị Thảo** (U09) → "+ Report metric" on Blood pressure → 141/88, symptoms "No symptoms" → Submit | S-028 "Metric alert"; a new case "Not viewed" |
| 2 | Same mother → Blood pressure 120/80, symptom "Palpitations" → Submit | "Report submitted" → S-026 with status "Not viewed" (Symptom case, BR-007) |
| 3 | Same mother → Blood pressure 120/80, "No symptoms" → Submit | "Report submitted" → back to S-027; no case |
| 4 | A mother with a blood-glucose instruction (U03) → glucose without choosing the timing → Submit | field error; nothing stored |
| 5 | Any mother → Submit with no symptom selected | error under the symptom field (BR-017) |
| 6 | A mother with no instruction (U06) → S-027 | only "+ Report symptoms" is available |

Seed facts the tests also check: 272 rows load; report RPT-006 (exactly 140/90) has case C6.
