# Research: ALR core (US-1)

Phase 0 of `/speckit-plan`. Each entry: decision, rationale, alternatives considered.

## R1. Stack

- **Decision**: Python 3.11+, FastAPI + Jinja2 server-rendered pages, SQLite (`sqlite3`), pytest + httpx; uv for the environment.
- **Rationale**: chosen by the team (14/10/2026). One language with the chatbot backend (BOT BR-003, Python); SQLite runs the existing `schema-MB360.sql` as it is; all tools are free and run on Windows and macOS; `uv sync` gives the same environment on every laptop.
- **Alternatives**: Flask (lighter, but FastAPI gives typed request models and a test client out of the box); Node.js + Express (two languages in one repository).

## R2. Building the database

- **Decision**: at start-up (and in each test) create a SQLite database, run `data/schema/schema-MB360.sql`, then load `data/seed/NN_TABLE.csv` in filename order with `PRAGMA foreign_keys = ON`. Empty CSV cells → NULL; booleans are 1 / 0 as in the seed.
- **Rationale**: the files are the source of truth (constitution I); filename order is foreign-key order (data model §10), so no ordering logic is needed. `tools/check_data_model.py` already loads the seed the same way, so the loader can follow it.
- **Alternatives**: an ORM with its own models (would redefine fields — forbidden by the plan argument); a pre-built `.db` file in Git (a generated binary that could drift from the CSV files).

## R3. Threshold check (BR-004)

- **Decision**: `thresholds.evaluate(metric, value, glucose_context)` reads THRESHOLD_RULE rows with `purpose = 'Report check'`, matching `metric` and `glucose_context`; blood pressure: two rows (systolic, diastolic) with `combine = any`, operator `≥`; blood glucose: one row per timing; urine protein: ordinal scale Negative < Trace < 1+ < 2+ < 3+ compared with the stored level. Returns `Normal` or `Above threshold`; a symptom report returns `Not assessed` (BR-005).
- **Rationale**: thresholds are configuration (D-52, AGENTS.md hard rule 7); the same algorithm is already proven against the seed in `generate_seed.py` (`over_threshold`).
- **Alternatives**: constants in code (forbidden).

## R4. Gestational week (FR-015)

- **Decision**: completed weeks = (280 − (EDD − today).days) // 7, from PREGNANCY_PROFILE.`edd`, clamped check 0 – 42.
- **Rationale**: the seed uses this rule (`week_at`, "seed assumption: 280-day pregnancy"); ACC §10 Q10 (Naegele) is still Pending SME, so the slice uses the same assumption as the seed and does not add a new one.
- **Alternatives**: store the week on the profile (data model says it is calculated, not stored — D-42, DM-42).

## R5. Report code (`report_code`, ALR §10 Q16 open)

- **Decision (provisional)**: `BC-` + month and day of `submitted_at` (`MMDD`) + `-` + 3-digit sequence = 1 + number of reports already stored that day + offset so that it never collides with the seed (unique constraint). One function, `reports.next_report_code()`, marked "provisional — ALR Q16".
- **Rationale**: the column is Required and unique; the wireframe (`BC-0926-015`) and the seed (`BC-0927-020`) use this shape. The rule is not invented as a requirement — it is a placeholder documented as such.
- **Alternatives**: random code (not readable on S-026 / S-064); leave empty (violates NOT NULL).

## R6. Storing a report (FR-020, FR-021) in one transaction

- **Decision**: one SQLite transaction writes HEALTH_METRIC_RECORD (metric report only: `source = 'Doctor-assigned'`, `metric_group = 'Group 2'`, `gestational_week`, `created_at = submitted_at`), METRIC_REPORT (`watch_flag_id` = the mother's active instruction for that metric), REPORT_SYMPTOM (one row per symptom), and — when BR-008 branch 1 or 2 applies — CARE_CASE (`status = 'Not viewed'`, `case_source` = Metric report / Symptom) + CASE_STATUS_HISTORY (`role = 'System'`, `changed_by` NULL).
- **Rationale**: the generator checks exactly these invariants on the seed (ALR FR-020 "stores record and report together", BR-006, BR-008, FR-021 first history row), so the code and the seed agree.
- **Alternatives**: separate writes (a failure could leave a report without its record).

## R7. Pages and the mother's identity

- **Decision**: Jinja2 templates for S-027 (list of active instructions + "+ Report metric" / "+ Report symptoms"), S-025A, S-028 (modal page), S-026 (minimal). Labels follow `docs/ui-label-reference.md` (English, as in the specs). The mother is chosen on a demo page `/` listing seed mothers (Complexity Tracking: login is Session 11).
- **Rationale**: the slice must be demonstrable end to end; server-rendered forms are testable through the HTTP client without a browser.
- **Alternatives**: JSON API + separate frontend (more moving parts than one story needs).

## R8. Valid ranges (ALR §10 Q9 open)

- **Decision**: no numeric range is enforced; a test documents the expected behaviour as `xfail(reason="ALR Q9 — valid ranges pending Client/SME")`.
- **Rationale**: constitution I — never invent a requirement.
- **Alternatives**: borrow ranges from the internet (would be a guess).
