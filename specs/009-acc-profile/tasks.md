# Tasks: ACC profile — Profile, edit, notification settings and notification list

**Input**: `specs/009-acc-profile/` — plan.md, spec.md (US-3, FR-025, FR-026), research.md, data-model.md, contracts/http-routes.md, quickstart.md

**Tests**: required by the constitution; each test task comes before the code it checks.

**Out of scope**: real TCI or EMR calls, delivery of notifications (S-010 SR-004), the structured notice detail (D-80, U9), logout (D-01).

## Phase 1: US-3 and the notification screens

### Tests (write first, see them fail)

- [X] T001 [P] `tests/unit/test_acc_profile.py` — FR-017, FR-023: `load` returns name, masked phone, record number, week, due date, source, height, link, consent, instructions; **BR-003**: `save` keeps the due date of a linked mother and changes it for a pending one; FR-020: invalid due date or height writes nothing; the LMP is cleared when the due date changes; S-010: allowed switches change, `report_response` and unknown keys are refused
- [X] T002 [P] `tests/unit/test_acc_notices.py` — FR-025: only her notifications, newest first, filter by type and "Unread", count of all unread; FR-026: opening marks read and keeps the first `read_at`, another mother's notification is refused, "all" marks only hers; targets of research R3
- [X] T003 [P] `tests/integration/test_acc_profile_pages.py` — pages and routes of the contract, no "Alert" word on S-009 (SR-002), no logout control (S-103 SR-001), the badge drops after opening

### Implementation

- [X] T004 `app/mb360/acc/profile.py` (T001)
- [X] T005 `app/mb360/acc/notices.py` (T002)
- [X] T006 `ui.t_known` reads `{field}` rows, nested values translated (research R4); labels in `docs/ui-label-reference.md`
- [X] T007 Routes in `acc/routes.py`; `profile.html`, `edit_profile.html`, `notif_settings.html`, `notices.html` on the package's components (T003)

## Phase 2: Polish

- [X] T008 Run the quickstart at phone width; build log entry; `start_feature.py --check`, `check_env.py --repo`
