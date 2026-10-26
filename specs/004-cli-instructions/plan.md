# Implementation Plan: CLI instructions — Doctor's instructions form + visit-result notification

**Branch**: `sang/004-cli-instructions` (based on `sang/003-alr-status`, PR #9) | **Date**: 2026-10-26 | **Spec**: [spec.md](spec.md) (snapshot of `specs/spec-CLI.md` v1.7.0)

**Input**: Feature specification from `specs/004-cli-instructions/spec.md`; ALR FR-019 / BR-003 from `specs/spec-ALR.md`

## Summary

Close the last business-rule gaps of the core modules for MVP Alpha gate G3:
- **CLI US-3 (P2), FR-025, CLI BR-006**: on S-064 a doctor adds or edits a "Doctor's instructions" entry (Watch-Flag) — metric to monitor (group 2), note for the mother, above-threshold guidance (template and / or custom text ≤ 1000); nurses only view. The mother then sees it on S-027 / S-025A and its guidance on S-028 (default template when none — D-24).
- **ALR BR-001**: the system never removes an instruction automatically; only a doctor adds / edits.
- **ALR FR-019 / BR-003**: a "Visit result" notification for the mother when a new Visit record is added, respecting "New visit results"; never called an "Alert". In the MVP visits are seed data and no screen inserts a visit (D-59), so FR-019 is a function the visit-insert path will call; it is tested directly.

Same stack and project. The branch starts from PR #9 because FR-019 reuses `alr/notifications.py`; merge #9 first.

## Technical Context

**Language/Version**: Python 3.11+ (uv) — unchanged · **Primary Dependencies**: unchanged · **Storage**: SQLite from schema + seed (unchanged) · **Testing**: pytest · **Target Platform**: local laptop · **Project Type**: web application (same project) · **Constraints**: data/ read-only; thresholds from THRESHOLD_RULE; "Alert" only on S-028 · **Scale/Scope**: S-064 form + one notification function

## Constitution Check

| Principle | How this plan complies | Status |
|---|---|---|
| I. The spec is the source of truth | CLI US-3 / FR-025 / BR-006, ALR BR-001, FR-019 / BR-003, S-064 #6 – #11, S-009 #9. Open points kept open: Watch-Flag `visit_id` (HLT §10 Q19) → left empty; note length (S-064 #9) → no limit; one active instruction per metric (DM-21 default) | PASS |
| II. Business rules are test-first | Tests for CLI BR-006, BR-001 (doctor only), ALR BR-001, BR-003, FR-019, US-3 scenarios 1 – 2, written and seen failing first | PASS |
| III. Thin vertical slices | One P2 story + one notification rule | PASS |
| IV. Synthetic data and no secrets | Seed only | PASS |
| V. Humans approve every change | Branch + pull request reviewed by a member who did not write it | PASS |

## Project Structure

```text
specs/004-cli-instructions/  spec.md, plan.md, research.md, data-model.md, quickstart.md, contracts/http-routes.md, tasks.md
app/mb360/cli/instructions.py      # FR-025: save / edit a Watch-Flag (doctor only)
app/mb360/alr/notifications.py     # + notify_visit_result (FR-019)
app/mb360/cli/routes.py, templates/case.html   # S-064 "Edit" + "Add / edit instruction" form
tests/unit/test_cli_instructions.py, test_alr_visit_notification.py
tests/integration/test_cli_instructions_page.py
```

## Complexity Tracking

| Item | Why it matters | What the plan does until it is answered |
|---|---|---|
| HLT §10 Q19 — which visit a new instruction is attached to | `visit_id` is optional | Left empty for an instruction added on S-064; an edited instruction keeps its visit |
| S-064 #9 — maximum length of the note | Textarea | No limit (TEXT in the data model) |
| DM-21 default — one active instruction per (mother, metric) | Adding a metric that already has an active instruction | The form edits that instruction instead of adding a second one |
| Removing / deactivating an instruction | BR-001 says only a doctor may remove one; FR-025 covers add / edit only | Not built; no "Remove" button |
| FR-019 trigger | No visit-insert path in the MVP (D-59) | `notify_visit_result(conn, visit_id, now)` is ready for that path and tested directly; seed visits are not re-notified at start-up (the seed already holds their notifications) |
