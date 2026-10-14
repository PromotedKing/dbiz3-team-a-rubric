# Tasks: CLI core — nurse and doctor handle the cases

**Input**: `specs/002-cli-core/` — plan.md, spec.md (US-1, US-2), research.md, data-model.md, contracts/http-routes.md, quickstart.md

**Tests**: required by the constitution (Principle II). Every business rule of the slice and every acceptance scenario of US-1 and US-2 has a test task **before** the code task it checks.

**Out of scope** (plan.md Complexity Tracking): US-3 / FR-025 (Doctor's instructions form), notifications to the mother (ALR FR-018), Q12 internal note, Q13 list of all the mother's cases, the drawn chart of FR-008.

## Format: `[ID] [P?] [Story] Description`

---

## Phase 1: Setup

- [X] T001 Create the package `app/mb360/cli/__init__.py` (no new dependency — plan.md Technical Context)

## Phase 2: Foundational

### Tests first

- [X] T002 [P] Seed test in `tests/seed/test_seed_cli.py`: 7 STAFF rows (4 nurses, 3 doctors); 10 CARE_CASE rows — 4 Not viewed, 1 Viewed, 1 Escalated to doctor, 4 Resolved (`data/seed/seed-report.md`); case C7 history = Not viewed (System), Viewed and Escalated to doctor at the same minute by the same nurse, Resolved by a doctor (seed scenario "ALR BR-016 / D-43")
- [X] T003 [P] `tests/unit/test_cli_assignment.py` — D-68, R3: responsible doctor of U09 = Phạm Quốc Dũng; of U05 = Phạm Quốc Dũng (the earlier assignment ended 31/08/2026); U06 still has Phạm Quốc Dũng on 27/09/2026 (inclusive `valid_to`, §10 Q15) and none on 28/09/2026; U07 has none

### Code

- [X] T004 `app/mb360/cli/actions.py` — `responsible_doctor(conn, user_id, today)` (R3) — makes T003 pass
- [X] T005 `tests/conftest.py` — add fixture `staff_id(name)` returning the seed staff id by full name (no change to existing fixtures)

**Checkpoint**: `uv run pytest tests/seed tests/unit/test_cli_assignment.py` passes.

---

## Phase 3: US-1 — Nurse works through the case queue (P1) + US-2 — Doctor handles an escalated case (P1) 🎯

**Goal**: a case created by the mother is viewed, escalated, answered and closed by the right person, with the status moving forward only.

**Independent test**: quickstart.md scenarios 1 – 8; `uv run pytest` green.

### Tests (write first, see them fail)

- [X] T006 [P] [US1] `tests/unit/test_cli_actions.py` — **BR-002, D-43**: Mark as viewed Not viewed → Viewed (history row role Nurse, changed_by = nurse); Escalate from Not viewed writes Viewed then Escalated to doctor (same staff, same minute) and sets `assigned_doctor_id` = responsible doctor; Close by a nurse from Not viewed writes Viewed then Resolved with `closed_at`, `closed_by`; status never moves backwards (Mark as viewed on a Viewed / Escalated / Resolved case → refused, nothing written); escalation of a mother without an active responsible doctor → refused, nothing written (§10 Q10)
- [X] T007 [P] [US1] `tests/unit/test_cli_permissions.py` — **BR-001, BR-004 permission table, BR-008**: nurse may view / escalate / send guidance / close a case not escalated; nurse may **not** close an "Escalated to doctor" case; doctor may **not** mark as viewed or escalate; doctor may send guidance and close **only** "Escalated to doctor" cases; send guidance never changes the status; guidance needs a template or text, text ≤ 1000 (1001 refused)
- [X] T008 [P] [US1] `tests/unit/test_cli_queue.py` — **FR-002, FR-020, BR-007**: queue sorted newest first; filter Not viewed / Viewed / Escalated to doctor / Resolved / All returns only those statuses; threshold label from THRESHOLD_RULE for metric cases (RPT-006 140/90 → Above threshold), "Not assessed" for Symptom and Chatbot cases; content column = metric, symptoms or chatbot question; "Submitted at" of a chatbot case = case `created_at`
- [X] T009 [P] [US1] `tests/integration/test_cli_queue_page.py` — **US-1 #1 – #4, US-2 #1, BR-005**: `/staff` lists the 7 staff; nurse page header "Nurse: Trần Thị B", default filter All; doctor page header "Dr. Phạm Quốc Dũng", default filter Escalated to doctor and "Notifications (n)" = escalated cases assigned to him; `?status=Not viewed` shows only those rows; a filter with no case shows "No cases to handle."; "View report ›" links to S-064 of the case
- [X] T010 [P] [US1] `tests/integration/test_cli_nurse_actions.py` — **US-1 #5 – #9**: nurse on RPT-006's case: Mark as viewed → 303 and status Viewed; Escalate to doctor → status Escalated to doctor and `assigned_doctor_id` = Phạm Quốc Dũng; S-064 then has no "Close case" for the nurse and POST close → 403 / 409 with nothing written; Send guidance with a template → STAFF_RESPONSE row (responder_role Nurse), status unchanged; on a case not escalated, Close case → Resolved; the "Doctor's instructions" block has no "Edit" and no form
- [X] T011 [P] [US2] `tests/integration/test_cli_doctor_actions.py` — **US-2 #2 – #5, BR-001**: doctor S-064 has no "Mark as viewed" / "Escalate to doctor" buttons; on the seed escalated case C4 with its assigned doctor Nguyễn Văn A: Send guidance → response saved, status unchanged; Close case → Resolved, `closed_by` = doctor; on a Not viewed case the doctor has no handling buttons and POST guidance / close → 403 with nothing written
- [X] T012 [P] [US1] `tests/integration/test_cli_case_page.py` — **FR-003, FR-007, FR-008, FR-010, BR-009, CLI-01**: S-064 of RPT-006's case shows the mother's name, medical record number, week, due date, medical history, the Report block (140/90 mmHg, Above threshold, measured time, source Doctor-assigned, symptoms, status); metric history lists only "From visit" and "Doctor-assigned" values and the threshold 140/90 mmHg; no "Self-entered" value appears; S-064 of a chatbot case shows the question and every message of its conversation in time order; the word "alert" does not appear on S-061 or S-064 (ALR BR-010)
- [X] T013 [P] [US1] `tests/integration/test_cli_loop.py` — **end to end with `specs/001-alr-core`**: a mother submits a symptom report; the new case is first in the nurse queue as Not viewed; the nurse escalates it; it appears in the responsible doctor's default view; the doctor closes it

### Implementation (make the tests above pass)

- [ ] T014 [US1] `app/mb360/cli/actions.py` — Mark as viewed, Escalate, Send guidance, Close (R2), permission checks (BR-004), one transaction each — makes T006, T007 pass
- [ ] T015 [P] [US1] `app/mb360/cli/queue.py` — case list, filters, Newest, labels, content, doctor badge (R4, R5) — makes T008 pass
- [ ] T016 [P] [US1] `app/mb360/cli/case_detail.py` — S-064 data: profile, medical history, instructions, Report block or chatbot transcript (R6), metric history without Self-entered, visits
- [ ] T017 [US1] `app/mb360/cli/routes.py` + include in `app/mb360/main.py` — routes of contracts/http-routes.md; 303 / 403 / 409 / 422 — makes T009 – T011, T013 pass
- [ ] T018 [P] [US1] Templates `staff_select.html`, `cases.html` (S-061), `case.html` (S-064) — makes T012 pass

**Checkpoint**: `uv run pytest` — all pass (ALR tests included), 1 xfail (ALR Q9).

## Phase 4: Polish

- [ ] T019 Run quickstart.md scenarios 1 – 8 in the browser; fix quickstart.md if a step differs
- [ ] T020 [P] Build log entry and spec issues to `specs/spec-CLI.md` §10

## Dependencies

Phase 1 → 2 → 3 → 4. T006, T007 → T014; T008 → T015; T009 – T013 → T016 – T018. T004 before T014 (same file, extended).
