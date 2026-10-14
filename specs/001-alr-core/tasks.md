# Tasks: ALR core — submit a metric or symptom report

**Input**: `specs/001-alr-core/` — plan.md, spec.md (US-1), research.md, data-model.md, contracts/http-routes.md, quickstart.md

**Tests**: required by the constitution (Principle II). Every business rule of the slice and every US-1 acceptance scenario has a test task that comes **before** the code task it checks; the test must be seen failing first.

**Out of scope** (plan.md Complexity Tracking): US-2, US-3 (Won't), FR-018, FR-022, CLI actions (FR-004, FR-009, FR-016). They have no task here.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: can run in parallel (different files, no dependency on an unfinished task)
- **[US1]**: user story 1 of spec.md

---

## Phase 1: Setup

- [ ] T001 Create `pyproject.toml` (uv project, Python ≥ 3.11; dependencies fastapi, jinja2, python-multipart, uvicorn; dev dependencies pytest, httpx; pytest `testpaths = ["tests"]`, `pythonpath = ["app"]`) and run `uv sync`
- [ ] T002 [P] Create the package skeleton `app/mb360/__init__.py`, `app/mb360/alr/__init__.py`, `app/mb360/templates/`, and `tests/unit/`, `tests/integration/`, `tests/seed/`
- [ ] T003 [P] Check `.gitignore` ignores `.venv/`, `__pycache__/`, `.pytest_cache/` and any `*.db` file; add the missing lines

---

## Phase 2: Foundational (blocks US-1)

### Tests first

- [ ] T004 [P] Seed test in `tests/seed/test_seed_load.py`: the database built from `data/schema/schema-MB360.sql` + `data/seed/*.csv` (filename order, foreign keys on) has 26 tables and **272 rows**; report `BC-0927-020` (RPT-006, exactly 140/90) has a CARE_CASE with `case_source` = Metric report (seed C6) — values stated by `data/seed/seed-report.md`
- [ ] T005 [P] Clock test in `tests/unit/test_clock.py`: default now = 2026-09-27 10:00 (seed NOW); a test can override it

### Code

- [ ] T006 `tests/conftest.py`: fixture `db` = fresh in-memory SQLite built by `mb360.db.build()`; fixture `client` = FastAPI TestClient using that database and a fixed clock
- [ ] T007 `app/mb360/db.py`: `build(path=":memory:")` runs the schema then loads every `data/seed/NN_TABLE.csv` in filename order (empty cell → NULL), `PRAGMA foreign_keys = ON`; no write to `data/` (research R2) — makes T004 pass
- [ ] T008 [P] `app/mb360/clock.py`: `now()` returns the seed NOW unless overridden — makes T005 pass

**Checkpoint**: `uv run pytest tests/seed tests/unit/test_clock.py` passes.

---

## Phase 3: User Story 1 — Submit a metric or symptom report (P1) 🎯 MVP

**Goal**: the mother reports a flagged Group 2 metric or symptoms; the system stores it, checks the threshold, creates a case when needed and routes her (BR-008).

**Independent test**: quickstart.md §6 scenarios 1 – 6 in the browser; `uv run pytest` green except the `xfail` of ALR Q9.

### Tests for US-1 (write first, see them fail)

- [ ] T009 [P] [US1] `tests/unit/test_thresholds.py` — **BR-004, BR-005**: blood pressure 140/90 → Above threshold, 139/89 → Normal, 140/80 and 120/90 → Above threshold (systolic OR diastolic); blood glucose fasting 5.3 / post_1h 7.8 / post_2h 6.7 → Above threshold, 0.1 below each → Normal; urine protein Negative and Trace → Normal, 1+ → Above threshold; symptom report → Not assessed; **thresholds come from THRESHOLD_RULE**: after updating the systolic row to 150 in the test database, 145/80 → Normal (AGENTS.md hard rule 7)
- [ ] T010 [P] [US1] `tests/unit/test_validation.py` — **FR-013, FR-014, BR-017**: blood glucose without `glucose_context` → error; no symptom selected → error "Please select your symptoms" on the symptom field; "No symptoms" together with another symptom → error; "Other" without text → error; "Other" text of 101 characters → error, 100 → valid; blood pressure needs two whole numbers; urine protein only Negative / Trace / 1+ / 2+ / 3+; `measured_at` required (no rule on future times — not in the spec); one test marked `xfail(reason="ALR Q9 — valid ranges pending Client/SME")` for a systolic of 999
- [ ] T011 [P] [US1] `tests/unit/test_routing.py` — **BR-008, BR-002**: (Above threshold, any symptoms) → S-028 and case source Metric report; (Normal, ≥ 1 symptom) → S-026 and case source Symptom; (Normal, "No symptoms") → S-027 and no case; (Not assessed symptom report, ≥ 1 symptom) → S-026, case source Symptom
- [ ] T012 [P] [US1] `tests/unit/test_gestational_week.py` — **FR-015**: week = (280 − (EDD − today)) // 7 (research R4) for U09 (EDD 14/02/2027) at the seed NOW
- [ ] T013 [P] [US1] `tests/integration/test_report_above_threshold.py` — **US-1 scenario 4, FR-020, FR-021, BR-006**: U09 posts blood pressure 141/88, "No symptoms" → 303 to `/m/{user}/reports/{id}/alert`; one HEALTH_METRIC_RECORD (Group 2, Doctor-assigned, gestational week, `created_at` = `submitted_at`), one METRIC_REPORT with `watch_flag_id` = W09 and a unique `report_code`, one REPORT_SYMPTOM "No symptoms", one CARE_CASE "Not viewed" / Metric report, one CASE_STATUS_HISTORY row (role System, `changed_by` NULL)
- [ ] T014 [P] [US1] `tests/integration/test_report_symptoms.py` — **US-1 scenario 5, BR-007**: U09 posts 120/80 with "Palpitations" → 303 to S-026 showing "Report submitted" and "Not viewed"; case source Symptom. Parametrised over every D-73 symptom (Vaginal bleeding … Other): each one creates a case; and a symptom-mode report (no value, no Health Metric Record, no `watch_flag_id`) with "Absence of fetal movement" creates a Symptom case
- [ ] T015 [P] [US1] `tests/integration/test_report_no_case.py` — **US-1 scenario 6, BR-008 branch 3, BR-009**: U09 posts 120/80 with "No symptoms" → 303 to S-027 with "Report submitted"; report and record stored, no CARE_CASE, no history row
- [ ] T016 [P] [US1] `tests/integration/test_report_invalid.py` — **US-1 scenario 7, BR-017**: posting with no symptom → 422, S-025A shown with the error under the symptom field, row counts of the 5 written tables unchanged
- [ ] T017 [P] [US1] `tests/integration/test_report_form.py` — **US-1 scenarios 1 – 3, FR-010 – FR-013, BR-006**: S-027 of U01 lists Blood pressure and Blood glucose cards + "+ Report symptoms"; S-025A "Change metric" lists only U01's active instructions + symptom mode (not Urine protein; U05's inactive W08 never counts); instruction box shown for a metric, hidden in symptom mode; threshold card text built from THRESHOLD_RULE (≥ 140/90 mmHg; glucose card follows the selected timing; ≥ 1+); hidden in symptom mode; U06 (no instruction) gets symptom mode only; a POST for a metric without an active instruction → 422
- [ ] T018 [P] [US1] `tests/integration/test_metric_alert.py` — **FR-007, BR-002, BR-010, BR-013, BR-014**: S-028 after U01's above-threshold blood pressure shows value, measured time, threshold, "Your report has been sent to clinical staff" and the guidance of W01 (template G02); after U04's report (W07 has no guidance) it shows the default template (`is_default` = 1); the word "Alert" appears on S-028 and on no other page of the slice; "Close" returns to S-027 and the report and case still exist

### Implementation for US-1 (make the tests above pass, in this order)

- [ ] T019 [US1] `app/mb360/alr/thresholds.py` — `evaluate(db, metric, value, glucose_context)` per research R3 — makes T009 pass
- [ ] T020 [P] [US1] `app/mb360/alr/validation.py` — form rules of T010 (no numeric range: ALR Q9) — makes T010 pass
- [ ] T021 [P] [US1] `app/mb360/alr/routing.py` — BR-008 decision (target screen + case source or none) — makes T011 pass
- [ ] T022 [US1] `app/mb360/alr/reports.py` — `gestational_week()` (R4), `next_report_code()` (R5, provisional — ALR Q16), `store_report()` writing HEALTH_METRIC_RECORD + METRIC_REPORT + REPORT_SYMPTOM in one transaction (R6) — makes T012 pass
- [ ] T023 [US1] `app/mb360/alr/cases.py` — `open_case()` writing CARE_CASE + first CASE_STATUS_HISTORY row in the same transaction as T022 (FR-021)
- [ ] T024 [US1] `app/mb360/main.py` — routes of `contracts/http-routes.md` (`/`, S-027, S-025A GET / POST, S-028, S-026), 422 on invalid input, 303 redirects per BR-008 — makes T013 – T016 pass
- [ ] T025 [P] [US1] Templates `app/mb360/templates/base.html`, `select_mother.html`, `instructions.html` (S-027), `report_form.html` (S-025A) — labels from `docs/ui-label-reference.md` (English), dates `dd/mm/yyyy · HH:mm` — makes T017 pass
- [ ] T026 [P] [US1] Templates `metric_alert.html` (S-028) and `report_status.html` (S-026, minimal) — "Alert" only in `metric_alert.html` — makes T018 pass

**Checkpoint**: `uv run pytest` — all pass, 1 xfail (ALR Q9).

---

## Phase 4: Polish

- [ ] T027 Run quickstart.md from a fresh clone on one Windows and one macOS laptop (gate G1 of `docs/build/mvp-alpha-checklist.md`); fix the commands in quickstart.md if a step differs
- [ ] T028 [P] Add the run to `docs/build/build-log.md` (tests line, commit) and any spec gap found to `specs/spec-ALR.md` §10 (never fixed silently in code)

---

## Dependencies

- Phase 1 → Phase 2 → Phase 3 → Phase 4.
- In Phase 3, every test task (T009 – T018) comes before the code task that makes it pass: T009 → T019; T010 → T020; T011 → T021; T012 → T022; T013 – T016 → T022, T023, T024; T017 → T025; T018 → T026.
- T022 and T023 share one transaction: T023 starts after T022.

## Parallel examples

- Tests T009 – T018 are in different files and can be written at the same time.
- After T019: T020, T021 in parallel; templates T025 and T026 in parallel once T024 exists.

## Implementation strategy

MVP = Phase 1 + 2 + 3 (US-1 only). Stop after Phase 3, validate with quickstart.md, open the pull request. US-2 ("My reports", full S-026) is the next slice of ALR.
