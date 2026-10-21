# Implementation Plan: ALR status — "My reports" and report status

**Branch**: `sang/003-alr-status` | **Date**: 2026-10-21 | **Spec**: [spec.md](spec.md) (snapshot of `specs/spec-ALR.md` v1.8.0)

**Input**: Feature specification from `specs/003-alr-status/spec.md`

## Summary

Build ALR **US-2 (P1) "View the status of my reports"**: the mother opens **S-029 "My reports"** (her reports and chatbot cases, filters by status and type, "No action needed" for Normal reports without symptoms) and **S-026 "Report status"** (report or chatbot question, 4-step handling progress with time and actor, skipped "Escalated to doctor" step, response from clinical staff or the "Safety note"). In the same slice, ALR **FR-018**: a "Report" notification for the mother when her case is created, changes status or receives a staff response, respecting her "Report responses" setting — the notification is created by the actions of `specs/001-alr-core` and `specs/002-cli-core`; its list (S-009) belongs to ACC and is not built. Same stack and project as `specs/001-alr-core/plan.md`.

## Technical Context

**Language/Version**: Python 3.11+ (uv) — unchanged

**Primary Dependencies**: FastAPI, Jinja2, python-multipart, Uvicorn; pytest, httpx — unchanged

**Storage**: SQLite from `data/schema/schema-MB360.sql` + seed (unchanged)

**Testing**: pytest (unit: list rows, progress steps, notification rules; integration: S-029, S-026, notifications created by the earlier actions; seed test)

**Target Platform**: local laptop, Windows and macOS

**Project Type**: web application (same project)

**Performance Goals**: demo scale

**Constraints**: data/ read-only; "Alert" only on S-028 (BR-010); 3 threshold labels (BR-005); one status set (BR-012); no push channel — notifications are rows "delivered via the TCI app" (X-05)

**Scale/Scope**: 2 mother screens (S-029, S-026) + notification creation

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | How this plan complies | Status |
|---|---|---|
| I. The spec is the source of truth | Requirements from `specs/003-alr-status/spec.md` (US-2, FR-001 – FR-003, FR-005 – FR-007, FR-018, BR-005, BR-009, BR-011, BR-012) and the screen specs S-029, S-026, S-009 (notification wording). Open points recorded: Safety note content and hotline number (S-026 #18, #19), FR-003 default order (§10 Q17), wording of status-change notifications (new §10 Q23) | PASS |
| II. Business rules are test-first | Tests for BR-005, BR-009, BR-011, BR-012, FR-018 and US-2 scenarios 1 – 3, written and seen failing first | PASS (enforced in tasks.md) |
| III. Thin vertical slices | One user story + the notification it needs; done when tests pass and quickstart.md runs | PASS |
| IV. Synthetic data and no secrets | Seed only; no key | PASS |
| V. Humans approve every change | Branch `sang/003-alr-status`; pull request reviewed by a member who did not write it (MVP Alpha G6) | PASS |

Post-design re-check: PASS — no table, column or package added.

## Project Structure

```text
specs/003-alr-status/  spec.md, plan.md, research.md, data-model.md, quickstart.md, contracts/http-routes.md, tasks.md
app/mb360/alr/
├── my_reports.py        # FR-002, FR-003: rows of S-029
├── status.py            # FR-005, FR-007, BR-011, BR-012: S-026 data and progress steps
└── notifications.py     # FR-018: create "Report" notifications (called by alr.cases and cli.actions)
app/mb360/templates/     # my_reports.html (S-029); report_status.html rewritten (S-026 full)
tests/unit/test_alr_my_reports.py, test_alr_status.py, test_alr_notifications.py
tests/integration/test_alr_my_reports_page.py, test_alr_status_page.py, test_alr_notifications_flow.py
```

**Structure Decision**: new modules in the existing `alr` package; `cli.actions` and `alr.cases` call `alr.notifications` inside their own transaction (X-02: ALR defines the data, CLI performs the action).

## Complexity Tracking

| Item | Why it matters | What the plan does until it is answered |
|---|---|---|
| S-026 #19 Safety note content (D-25, hospital-approved) | Shown while there is no response (BR-011) | A placeholder box "Safety note — content to be supplied by the hospital" |
| S-026 #18 hotline number (BOT §10 Q8) | "Emergency call: 1900 xxxx" | Shown as text with the placeholder number; no `tel:` link to a number that does not exist |
| FR-003 default order (§10 Q17) | List order of S-029 | Newest submission first — the order the S-029 screen spec states (§4 Default) |
| Wording of status-change notifications (new §10 Q23) | S-009 draws only "responded" (#8) and "sent to clinical staff" (#11) | Use #8 and #11 as drawn; for Viewed / Escalated to doctor / Resolved without a response: title "Your {metric} report is {status}", subtitle "Report {code}". Copied to `specs/spec-ALR.md` §10 Q23 |
| Entry points S-008 / S-023 "My reports" card | Not built (HLT / ACC) | A "My reports" link on S-027, S-028 and S-026 |
| S-009 notification list | ACC FR-025 – FR-027 (not a core module) | Out of scope; tests read the NOTIFICATION rows |
