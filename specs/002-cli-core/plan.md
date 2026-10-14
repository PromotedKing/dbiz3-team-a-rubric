# Implementation Plan: CLI core — nurse and doctor handle the cases

**Branch**: `sang/002-cli-core` | **Date**: 2026-10-14 | **Spec**: [spec.md](spec.md) (snapshot of `specs/spec-CLI.md` v1.7.0)

**Input**: Feature specification from `specs/002-cli-core/spec.md`

## Summary

Close the loop opened by `specs/001-alr-core`: on the clinical web, the **nurse** works through the "Cases to handle" queue (S-061), opens a case (S-064), marks it as viewed, sends guidance, escalates it to the mother's responsible doctor or closes it (**US-1, P1**); the **doctor** sees the escalated cases by default, reads the mother's context, sends guidance and closes them (**US-2, P1**). Both P1 stories are in this slice because they share the same two screens and the same status machine (BR-002, D-43); US-3 (Doctor's instructions form, P2) is out. Technical approach: same project and stack as `specs/001-alr-core/plan.md` — new package `app/mb360/cli/`, new routes and templates, same database built from schema + seed.

## Technical Context

**Language/Version**: Python 3.11+ (uv) — unchanged

**Primary Dependencies**: FastAPI, Jinja2, python-multipart, Uvicorn; tests pytest, httpx — unchanged, no new package

**Storage**: SQLite built from `data/schema/schema-MB360.sql` + `data/seed/*.csv` (unchanged; no new table or column)

**Testing**: pytest (unit tests for the status machine and permissions, integration tests through the HTTP layer, one seed test)

**Target Platform**: local laptop, Windows and macOS; `http://127.0.0.1:8000/staff`

**Project Type**: web application (same single project)

**Performance Goals**: demo scale (7 staff, 10 cases in the seed)

**Constraints**: no login until Session 11 (§10 Q11); no push / SMS (ALR-03); the doctor notification is not stored (DM-32); status only moves forward (BR-002); data/ read-only; "Alert" only on the mother's S-028 (ALR BR-010)

**Scale/Scope**: 2 screens (S-061, S-064) for 2 roles

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | How this plan complies | Status |
|---|---|---|
| I. The spec is the source of truth | Requirements only from `specs/002-cli-core/spec.md`; data from `data/` unchanged. Open points are recorded, not invented: Q5 (nurse default filter), Q10 (no active responsible doctor), Q11 (sign-in), Q12, Q13 | PASS |
| II. Business rules are test-first | Tests for BR-001 – BR-005, BR-007 – BR-009, the permission table and every scenario of US-1 (1 – 9) and US-2 (1 – 5), written and seen failing before the code | PASS (to enforce in tasks.md) |
| III. Thin vertical slices | US-1 + US-2 only (same screens, same rules); done when tests pass and quickstart.md runs from a clean clone | PASS |
| IV. Synthetic data and no secrets | Seed staff only; no password, no key | PASS |
| V. Humans approve every change | Branch `sang/002-cli-core`, pull request reviewed by a teammate | PASS |

Post-design re-check: PASS — no table, column or package added.

## Project Structure

### Documentation (this feature)

```text
specs/002-cli-core/
├── spec.md, plan.md, research.md, data-model.md, quickstart.md
├── contracts/http-routes.md
└── tasks.md            # /speckit-tasks
```

### Source Code (repository root)

```text
app/mb360/
├── main.py                    # + include the clinical routes
├── cli/
│   ├── __init__.py
│   ├── queue.py               # FR-002, FR-020: case list, filters, "Newest", threshold label
│   ├── case_detail.py         # FR-003, FR-007, FR-008, FR-010, FR-014, FR-015: S-064 data (+ chatbot transcript, D-78)
│   ├── actions.py             # FR-004, FR-016/021, FR-019, FR-024: status machine (BR-002, D-43) + permissions (BR-004)
│   └── routes.py              # contracts/http-routes.md
└── templates/
    ├── staff_select.html, staff_base.html
    ├── cases.html             # S-061
    └── case.html              # S-064
tests/
├── unit/test_cli_actions.py, test_cli_permissions.py, test_cli_queue.py
└── integration/test_cli_*.py
```

**Structure Decision**: a `cli` package next to `alr`, reusing `alr.thresholds` for the threshold label (CLI BR-007 points to ALR BR-004) and the same `db` / `clock`.

## Complexity Tracking

| Item | Why it matters | What the plan does until it is answered |
|---|---|---|
| §10 Q11 — web sign-in for clinical staff | The header must show the signed-in role + name (BR-005); permissions depend on it | Demo "staff selector" over the seed STAFF rows at `/staff`; the chosen staff_id is in the URL. No password, no session |
| §10 Q5 — default filter for the nurse | S-061 opens with some filter | "All" — the filter selected on the S-061 mockup (screen spec #6). The doctor's default "Escalated to doctor" is stated (CLI-02) |
| §10 Q10 (remaining part) — no active responsible doctor | "Escalate to doctor" needs `assigned_doctor_id` (D-68) | The escalation is refused with a message and nothing changes (no status, no history); a test documents it. The behaviour wanted by the Client stays open in Q10 |
| §10 Q12 — internal per-case note; §10 Q13 — list of all the mother's cases on S-064 | Optional parts of FR-004, FR-009, FR-013 | Not built in this slice |
| FR-008 chart | "graphical and chart-based" metric history | The slice shows the series as a table (date, value, source label) with the threshold from THRESHOLD_RULE; drawing the chart is a later polish task |
| Notifications to the mother on a status change / response (ALR FR-018, via CLI FR-005) | Part of FR-005 | Out of this slice: built with ALR US-2 ("My reports", S-009) so that creation and display of notifications are tested together |
| US-3 (Doctor's instructions form, FR-025) | P2 | Out of scope; the "Doctor's instructions" block on S-064 is view-only for both roles in this slice |
