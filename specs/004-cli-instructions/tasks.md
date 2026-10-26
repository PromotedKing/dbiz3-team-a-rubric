# Tasks: CLI instructions + ALR FR-019

**Input**: `specs/004-cli-instructions/` — plan.md, spec.md (US-3), research.md, data-model.md, contracts/http-routes.md, quickstart.md; `specs/spec-ALR.md` FR-019, BR-001, BR-003

**Tests**: required by the constitution; each test task comes before the code it checks.

**Out of scope**: removing / deactivating an instruction; choosing a visit for a new instruction (HLT §10 Q19); a visit-insert path (D-59).

## Phase 1: Setup

- [X] T001 Confirm the branch contains PR #9 (`alr/notifications.py` exists) and `uv run python -m pytest` is green (143 passed, 1 xfailed)

## Phase 2: Foundational

- [X] T002 [P] Seed test in `tests/seed/test_seed_instructions.py`: 9 WATCH_FLAG rows, 8 active (W08 inactive); one active instruction per (mother, metric) (DM-21); W07 has no template and no custom text; Visit result notifications exist in the seed for visits (so start-up must not create more)

## Phase 3: US-3 — Doctor adds / edits Doctor's instructions (P2) + ALR FR-019

### Tests (write first, see them fail)

- [X] T003 [P] [US3] `tests/unit/test_cli_instructions.py` — **FR-025, CLI BR-001, BR-006, DM-21**: a doctor adds a Blood glucose instruction for U09 (note, template) → new active WATCH_FLAG, `flagged_by` = doctor, `flagged_at` = 2026-09-27, `visit_id` empty; saving Blood pressure for U09 again updates W09 (no second active row); a nurse → ActionError 403, nothing written; metric "Weight" → 422; custom text 1001 characters → 422, 1000 → saved; unknown template → 422; neither template nor text → saved (S-028 then uses the default template — D-24)
- [X] T004 [P] [US3] `tests/unit/test_alr_watch_flags_kept.py` — **ALR BR-001**: after a report above threshold, escalate and close, the mother's WATCH_FLAG rows are unchanged (same count, all still active)
- [X] T005 [P] [US3] `tests/unit/test_alr_visit_notification.py` — **ALR FR-019, BR-003**: `notify_visit_result` for a seed visit of U01 writes one NOTIFICATION `type` = Visit result, `visit_id` set, title "New visit results available", subtitle "Visit 15/09/2026"; nothing when `new_visit_result` = 0; the title and subtitle do not contain "alert" and carry no threshold label
- [X] T006 [P] [US3] `tests/integration/test_cli_instructions_page.py` — **US-3 #1, #2; S-064 #6 – #11**: a doctor sees "Edit" on each instruction row and the "Add / edit instruction" form with the group-2 metrics, the templates and "Save instruction"; POST adds the instruction → 303, it is listed on S-064 with "Assigned 27/09/2026 · Dr. Phạm Quốc Dũng"; the mother's S-027 shows it and S-025A offers the metric; after an above-threshold report S-028 shows the chosen template, or the default template when the instruction has no guidance; a nurse's S-064 has no "Edit" and no form and her POST → 403 with nothing written

### Implementation

- [X] T007 [US3] `app/mb360/cli/instructions.py` — `save_instruction()` (R1) — makes T003, T004 pass
- [X] T008 [P] [US3] `notify_visit_result()` in `app/mb360/alr/notifications.py` (R3) — makes T005 pass
- [X] T009 [US3] Route `POST /staff/{staff_id}/cases/{case_id}/instructions` in `app/mb360/cli/routes.py`; S-064 template: "Edit" per row (doctor), "Add / edit instruction" form (doctor only), "Assigned dd/mm/yyyy · Dr. name" — makes T006 pass

## Phase 4: Polish

- [ ] T010 Walk quickstart.md scenarios 1 – 4
- [ ] T011 [P] Build log entry; MVP Alpha checklist G3 (ALR BR-001, BR-003, CLI BR-006 now tested)

## Dependencies

Phase 1 → 2 → 3 → 4. T003, T004 → T007; T005 → T008; T006 → T009.
