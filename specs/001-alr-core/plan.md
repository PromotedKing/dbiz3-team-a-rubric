# Implementation Plan: ALR core — submit a metric or symptom report

**Branch**: `sang/001-alr-core` | **Date**: 2026-10-14 | **Spec**: [spec.md](spec.md) (snapshot of `specs/spec-ALR.md` v1.8.0)

**Input**: Feature specification from `specs/001-alr-core/spec.md`

## Summary

Build ALR user story **US-1 (P1) "Submit a metric or symptom report"** end to end: the mother opens the report screen (S-025A) from her Doctor's instructions (S-027), reports a flagged Group 2 metric (blood pressure, blood glucose, urine protein) or symptoms, the system validates the input, stores the report (FR-020), checks the value against THRESHOLD_RULE (BR-004), creates a "Not viewed" case when the report is above threshold or has a symptom (FR-021, BR-007, BR-008), and routes the mother to S-028 "Metric alert", S-026 "Report status" or back to S-027. Technical approach: one Python web application (FastAPI, server-rendered pages) over SQLite, created from `data/schema/schema-MB360.sql` and loaded from the seed CSV files; rules live in plain Python functions tested with pytest.

## Technical Context

**Language/Version**: Python 3.11 or later (managed with uv)

**Primary Dependencies**: FastAPI, Jinja2 (server-rendered pages), python-multipart (HTML forms), Uvicorn (dev server); tests: pytest, httpx (FastAPI TestClient)

**Storage**: SQLite 3 (standard library `sqlite3`), database built from `data/schema/schema-MB360.sql` and the 26 seed files `data/seed/NN_TABLE.csv` loaded in filename order — no schema change, no new table

**Testing**: pytest (unit tests for the rules, integration tests through the HTTP layer, one seed test)

**Target Platform**: local laptop, Windows and macOS; browser at `http://127.0.0.1:8000`

**Project Type**: web application (single project: one Python package serving pages and logic)

**Performance Goals**: demo scale — a report is stored and routed in under 1 s on a laptop

**Constraints**: free tools only; no paid account; no login and no deployment until Session 11; thresholds read from THRESHOLD_RULE, never hard-coded (AGENTS.md hard rule 7); the word "Alert" only on S-028 (BR-010); seed and schema are read-only

**Scale/Scope**: seed data only (10 mothers, 272 rows); 4 mother screens touched (S-027 entry, S-025A, S-028, S-026 minimal)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | How this plan complies | Status |
|---|---|---|
| I. The spec is the source of truth | Requirements only from `specs/001-alr-core/spec.md` (snapshot of `specs/spec-ALR.md`); data only from `data/` (schema + seed, unchanged). Open points are not invented: ALR Q9 (valid ranges), Q14 (note length), Q16 (report code) are recorded below and in research.md | PASS |
| II. Business rules are test-first | Every BR of the slice (BR-002, BR-004 – BR-008, BR-010, BR-013, BR-014, BR-017) and every US-1 acceptance scenario (1 – 7) gets a test written and seen failing before the code (tasks.md will order test tasks first) | PASS (to enforce in /speckit-tasks) |
| III. Thin vertical slices | One user story (US-1), end to end: page → rule → SQLite; done when its tests pass and quickstart.md works from a clean clone | PASS |
| IV. Synthetic data and no secrets | Only the seed in `data/seed/`; no API key needed for this slice; `.env` stays out of Git | PASS |
| V. Humans approve every change | Work on `sang/001-alr-core`; changed files shown with reasons; a teammate reviews the pull request | PASS |

Post-design re-check (after Phase 1): still PASS — the design adds no table, no column and no dependency outside the list above.

## Project Structure

### Documentation (this feature)

```text
specs/001-alr-core/
├── spec.md              # snapshot of specs/spec-ALR.md (do not edit; start_feature.py --refresh)
├── plan.md              # this file
├── research.md          # Phase 0 decisions
├── data-model.md        # tables this slice reads / writes (points to data/data-model-MB360.md)
├── quickstart.md        # install, check seed, test, run — Windows and macOS
├── contracts/
│   └── http-routes.md   # pages and form posts of the slice
└── tasks.md             # Phase 2 output (/speckit-tasks — not created here)
```

### Source Code (repository root)

```text
pyproject.toml                 # uv project: dependencies and pytest settings
app/
└── mb360/
    ├── __init__.py
    ├── main.py                # FastAPI app, routes of contracts/http-routes.md
    ├── db.py                  # build SQLite from schema-MB360.sql, load data/seed/*.csv in filename order
    ├── clock.py               # "now" for the demo (seed NOW = 2026-09-27 10:00), injectable in tests
    ├── alr/
    │   ├── thresholds.py      # BR-004: evaluate a value against THRESHOLD_RULE rows
    │   ├── validation.py      # FR-013, FR-014, BR-017: form rules
    │   ├── reports.py         # FR-020 store report (+ Health Metric Record), FR-015 gestational week
    │   ├── cases.py           # FR-021 create case + first status-history row; BR-007, BR-008
    │   └── routing.py         # BR-008 → S-028 / S-026 / S-027
    └── templates/             # S-027 (entry list), S-025A, S-028, S-026 (minimal) — Jinja2
tests/
├── conftest.py                # fresh in-memory database from schema + seed per test
├── unit/                      # thresholds, validation, routing
├── integration/               # form post → database rows → page shown
└── seed/                      # seed loads (272 rows); RPT-006 (140/90) opens C6
```

**Structure Decision**: single project (`app/mb360/` + `tests/`). There is one actor (the mother) and server-rendered pages, so a separate frontend is not needed. The chatbot service (BOT, later feature) can join the same Python project.

## Complexity Tracking

> Items the spec leaves open, or that need something the spec does not give. None is resolved by guessing.

| Item | Why it matters for this slice | What the plan does until it is answered |
|---|---|---|
| ALR §10 Q9 — valid input ranges (D-16, Pending SME) | FR-014 must block typing errors | Validation checks only presence, format and type (numbers, systolic / diastolic pair, urine protein level, glucose timing, "Other" ≤ 100). No range is invented. One test is `xfail` with reason "ALR Q9" until the Client answers; then a `## Clarifications` section in `specs/spec-ALR.md` + `start_feature.py --refresh` |
| ALR §10 Q16 — rule for `report_code` | METRIC_REPORT.`report_code` is Required and unique | Provisional generator following the pattern of the seed and the wireframe (`BC-MMDD-NNN`), isolated in one function, flagged "provisional (ALR Q16)" in research.md R5 |
| ALR §10 Q14 — maximum length of `note` | Note field on S-025A | Stored as TEXT without a limit (data model) |
| Login (Session 11) | The mother's identity normally comes from the TCI session (ACC FR-015) | A demo "mother selector" over the seed USER_ACCOUNT rows; no password, no SESSION row written |
| "Now" for the demo | Seed timestamps are around 2026-09-27; the gestational week (FR-015) depends on the date | `clock.py` returns the seed NOW by default; tests inject a fixed time |
| Out of scope of US-1 | Keep the slice thin | US-2 (My reports list, full S-026), FR-018 notifications, FR-022 reminders, CLI actions (FR-004, FR-009, FR-016) are later slices; S-026 shows only report details + status "Not viewed" |
