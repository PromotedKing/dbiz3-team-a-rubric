# Tasks: ACC onboarding — open the sub-app, consent, guide, pregnancy setup

**Input**: `specs/005-acc-onboarding/` — plan.md, spec.md (US-1, US-2), research.md, data-model.md, contracts/http-routes.md, quickstart.md

**Tests**: required by the constitution; each test task comes before the code it checks.

**Out of scope**: US-3 profile (S-103, S-011), BR-003, S-083 close, S-043 session expired, S-009 / S-010, the other modules' parts of S-008.

## Phase 1: Setup

- [X] T001 Create `app/mb360/acc/__init__.py`; no new dependency

## Phase 2: Foundational

- [X] T002 [P] Seed test in `tests/seed/test_seed_acc.py`: 10 USER_ACCOUNT rows, all `sex` = Female (BR-007, D-71); every account has ≥ 1 CONSENT_RECORD and one NOTIFICATION_PREFERENCE; Hoàng Thu Trang (U07) has no PREGNANCY_PROFILE (seed scenario "ACC BR-006"); the 7 ordinary seed SESSION rows last 12 hours (U06, U07, U08 are edge cases)

## Phase 3: US-1 + US-2 (P1) 🎯

### Tests (write first, see them fail)

- [X] T003 [P] [US1] `tests/unit/test_acc_entry.py` — **FR-015, FR-011, BR-004, BR-006, BR-007, DM-18, DM-41**: `open_subapp` for a new Female identity → "consent", nothing written; for a Male identity → "not_female", nothing written; for Nguyễn Thị Lan → "home", a SESSION row (12 h), copy refreshed (a changed phone is saved); for Hoàng Thu Trang → "setup"; `agree` unticked → refused, nothing written; `agree` ticked → USER_ACCOUNT (copy, Female, Mother), CONSENT_RECORD (accepted 1, `tci_data_permission` 1, `terms_version` empty), NOTIFICATION_PREFERENCE (1, 1, 1, 0), SESSION; agreeing twice with the same TCI reference does not create a second account
- [X] T004 [P] [US2] `tests/unit/test_acc_setup.py` — **FR-004, FR-005, D-72, Q10 provisional**: EDD 20/12/2026 at 27/09/2026 → Week 28 · day 0; LMP 01/04/2026 → EDD 06/01/2027, Week 25 · day 4; EDD in the past → error; EDD more than 280 days ahead (week < 0) → error; neither date → error; height / weight "abc" → error; first visit date after today or before EDD − 280 days → error; a valid save writes PREGNANCY_PROFILE (Self-entered, height, first visit date) and the weight as a Group 1 Self-entered HEALTH_METRIC_RECORD with the gestational week; height and weight may be empty (no weight record then)
- [X] T005 [P] [US1] `tests/integration/test_acc_onboarding_flow.py` — **US-1 #1 – #6**: `/tci` lists the seed accounts and the simulate form; opening as a new account shows "Connect to your TCI account" with full name, date of birth, phone number, medical record number, prenatal visit results and no password field; unticked → 422 with `data-error-for="agree"`, no account; "Later" → 303 `/tci`, no account; agree → 303 to S-104; S-104 shows 4 pages with Next / Skip / Get started; Skip → setup (no due date); a Male identity → "Mother & Baby 360 is for expectant mothers." and "Back to TCI app", no account; Nguyễn Thị Lan → 303 to her Home
- [X] T006 [P] [US2] `tests/integration/test_acc_setup_page.py` — **US-2 #1 – #6**: setup with `?date_type=EDD&date=2026-12-20` shows "Calculated by the system", "Week 28 · day 0", "Today 27/09/2026 · Due 20/12/2026"; LMP shows the calculated due date; POST with a past EDD → 422 with the field error, nothing saved; valid POST → 303 Home; a mother who has a due date is sent from setup to Home (BR-006); the first-visit-date field is on the page
- [X] T007 [P] [US2] `tests/integration/test_acc_home_page.py` — **FR-016, FR-017, BR-006**: Lan's Home shows "Hello, Lan!", "Week 28", "Due date: 20/12/2026", her Doctor's instructions (Blood pressure, Blood glucose) linking to S-027 and "My reports" linking to S-029; Hoàng Thu Trang's Home redirects to setup; the word "alert" is absent from S-001, S-104, setup and Home pages

### Implementation

- [X] T008 [US1] `app/mb360/acc/entry.py` — `open_subapp`, `agree`, session (R2, R3) — makes T003 pass
- [X] T009 [P] [US2] `app/mb360/acc/setup.py` — `calculate`, `validate`, `save` (R5) — makes T004 pass
- [X] T010 [US1] `app/mb360/acc/routes.py` + register in `main.py` — routes of contracts/http-routes.md — makes T005 – T007 pass
- [X] T011 [P] [US1] templates `tci_home.html`, `consent.html`, `not_female.html`, `guide.html`, `setup.html`, `home.html`

## Phase 4: Polish

- [X] T012 Walk quickstart.md scenarios 1 – 9 in the browser
- [ ] T013 [P] Build log entries; MVP Alpha checklist limitation 3 and 12 updated

## Dependencies

Phase 1 → 2 → 3 → 4. T003 → T008; T004 → T009; T005 – T007 → T010, T011.
