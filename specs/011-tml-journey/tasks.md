# Tasks: TML journey — review by stage and keepsake album

**Input**: `specs/011-tml-journey/` — plan.md, spec.md (US-4), research.md, data-model.md, contracts/http-routes.md, quickstart.md

**Tests**: required by the constitution; each test task comes before the code it checks.

**Out of scope**: a server-generated PDF file (plan, Complexity Tracking), writing Messages to Baby (US-3, D-03), any edit (BR-001, BR-006).

## Phase 1: US-4

### Tests (write first, see them fail)

- [X] T001 [P] `tests/unit/test_tml_journey.py` — FR-013: boundaries of D-75, default stage, weeks without content left out, not-reached stage, full journey, counts; BR-007: only her own content, nothing written; all photos of an entry
- [X] T002 [P] `tests/integration/test_tml_journey_pages.py` — US-4 #1 – #4 and the contract; no edit control (BR-006); measurements with their report date (BR-003); no "Alert" word

### Implementation

- [X] T003 `app/mb360/tml/journey.py`; `weeks.week_content` (T001)
- [X] T004 Routes, `journey.html`, `album.html`, links on S-048 and S-103; labels in `docs/ui-label-reference.md` (T002)

## Phase 2: Polish

- [X] T005 Run the quickstart at phone width; build log entry; `start_feature.py --check`, `check_env.py --repo`; checklist limitations
