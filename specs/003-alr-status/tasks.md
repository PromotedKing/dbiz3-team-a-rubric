# Tasks: ALR status — "My reports" and report status

**Input**: `specs/003-alr-status/` — plan.md, spec.md (US-2), research.md, data-model.md, contracts/http-routes.md, quickstart.md

**Tests**: required by the constitution (Principle II); each test task comes before the code task it checks.

**Out of scope**: S-009 notification list and settings (ACC FR-025 – FR-027), FR-019 / FR-022 notifications, S-008 / S-023 cards.

## Phase 1: Setup

- [ ] T001 No new package or dependency (plan.md); confirm `uv run python -m pytest` is green on `main` before starting (110 passed, 1 xfailed)

## Phase 2: Foundational

- [ ] T002 [P] Seed test in `tests/seed/test_seed_alr_status.py`: Nguyễn Thị Lan (U01) has 3 reports (RPT-001 Normal without a case, RPT-002 → C1 Resolved, RPT-010 → Not viewed) and 1 chatbot case (Not viewed); C1 history = Not viewed, Viewed (Nurse Trần Thị B, 26/09/2026 20:25), Resolved (20:40), no "Escalated to doctor"; C1 has response SR1 from Trần Thị B (`data/seed/seed-report.md`, scenario "ALR US-2")

## Phase 3: US-2 — View the status of my reports (P1) 🎯

**Goal**: the mother follows what happened to each report and chatbot question; she is notified when her case moves.

**Independent test**: quickstart.md scenarios 1 – 5; `uv run python -m pytest` green.

### Tests (write first, see them fail)

- [ ] T003 [P] [US2] `tests/unit/test_alr_my_reports.py` — **FR-002, FR-003, BR-005, BR-009**: Lan's rows newest first (4 rows); RPT-001 row "No action needed", no case, label Normal; RPT-002 row label Above threshold, value "150/95 mmHg", status Resolved; RPT-010 row label Not assessed with its symptoms; chatbot row "Chatbot", question text, no label, status Not viewed; status filter (Resolved → 1 row; Not viewed → 2 rows; a "No action needed" row only under All); type filter (Blood pressure → 2, Symptom → 1, Chatbot → 1)
- [ ] T004 [P] [US2] `tests/unit/test_alr_status.py` — **BR-012, BR-011, FR-007**: C1 progress = Not viewed done ("Report submitted", 26/09/2026 · 20:17), Viewed done ("Nurse Trần Thị B", 20:25), Escalated to doctor **skipped** ("No doctor escalation needed"), Resolved done (20:40); RPT-010's case: Not viewed done, the 3 other steps pending; C7 (escalated then closed by a doctor): all 4 steps done, Resolved by "Dr. Nguyễn Văn A"; C1 responses = 1 "Response from Nurse Trần Thị B" with the guidance text and the Safety note is not shown; RPT-010's case shows the Safety note and no response
- [ ] T005 [P] [US2] `tests/unit/test_alr_notifications.py` — **FR-018**: on case creation a Report notification with `case_id`, title "Your Blood pressure report has been sent to clinical staff", subtitle "150/95 mmHg · Above threshold"; on a staff response title "Nurse Trần Thị B responded to your Blood pressure report"; on a status change title "Your Blood pressure report is Viewed"; nothing when the mother's "Report responses" switch is off; title ≤ 100 and subtitle ≤ 200 characters
- [ ] T006 [P] [US2] `tests/integration/test_alr_my_reports_page.py` — **US-2 #1**: `/m/{lan}/my-reports` shows the 4 rows newest first, chips with "All" active, "No action needed" row has no link to S-026, other rows link to S-026 (report) or the chatbot case page; `?status=Resolved` and `?type=Chatbot` filter; a mother with no report (U07) sees "You have not submitted any reports."; S-027, S-028 and S-026 link to "My reports"; the word "alert" is absent from S-029 (BR-010)
- [ ] T007 [P] [US2] `tests/integration/test_alr_status_page.py` — **US-2 #2, #3, FR-005**: S-026 of RPT-002 shows code BC-0926-015, status Resolved, "Blood pressure", "Above threshold", "150/95 mmHg", measured and submitted times, symptoms, the 4 progress steps with "No doctor escalation needed", "Response from Nurse Trần Thị B", no Safety note, "Emergency call"; S-026 of RPT-010 shows the Safety note and pending steps; the chatbot case page shows "Chatbot", "Your question:" with the question and the progress; the word "alert" is absent from S-026
- [ ] T008 [P] [US2] `tests/integration/test_alr_notifications_flow.py` — **FR-018 through the earlier actions**: a mother's above-threshold report (001) creates 1 notification; nurse Mark as viewed, Send guidance, Close (002) create 1 notification each (3); escalate from Not viewed creates 1 (not 2); after the nurse sends guidance, the mother's S-026 shows the response and hides the Safety note

### Implementation

- [ ] T009 [US2] `app/mb360/alr/notifications.py` — `notify()` per research R5 — makes T005 pass
- [ ] T010 [US2] Call `notifications.notify` from `app/mb360/alr/cases.py` (creation) and `app/mb360/cli/actions.py` (status change, response) inside their transactions — makes T008 notification counts pass
- [ ] T011 [P] [US2] `app/mb360/alr/my_reports.py` — rows, filters, order (R2, R6) — makes T003 pass
- [ ] T012 [P] [US2] `app/mb360/alr/status.py` — progress steps, responses, Safety note (R3, R4) — makes T004 pass
- [ ] T013 [US2] Routes in `app/mb360/main.py`: `/m/{user_id}/my-reports`, S-026 for a report (replaces the minimal page) and `/m/{user_id}/cases/{case_id}` for a chatbot case; "My reports" links on S-027, S-028, S-026 — makes T006, T007 pass
- [ ] T014 [P] [US2] Templates `my_reports.html` (S-029) and `report_status.html` (S-026 full, report and chatbot variants)

## Phase 4: Polish

- [ ] T015 Walk quickstart.md scenarios 1 – 5 in the browser
- [ ] T016 [P] Build log entry; update `docs/build/mvp-alpha-checklist.md` G2 / G3 and limitations 1 – 2

## Dependencies

Phase 1 → 2 → 3 → 4. T003 → T011; T004 → T012; T005 → T009 → T010; T006, T007 → T013, T014; T008 → T010, T013.
