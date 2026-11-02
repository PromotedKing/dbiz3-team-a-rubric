# Tasks: HLT history — Doctor's instructions and metric history

**Input**: `specs/010-hlt-history/` — plan.md, spec.md (US-3, US-4), research.md, data-model.md, contracts/http-routes.md, quickstart.md

**Tests**: required by the constitution; each test task comes before the code it checks.

**Out of scope**: editing any value (BR-001), tapping a measurement, statistics for urine protein and sleep (HLT Q12).

## Phase 1: US-3 + US-4

### Tests (write first, see them fail)

- [X] T001 [P] `tests/unit/test_hlt_history.py` — FR-010: range is inclusive, default 30 days; FR-011: blood pressure separately, none for urine protein and sleep; BR-003: no label and no line for group 1; BR-005: fetal heart rate only "From visit", reference lines, no label; FR-012: lines read from THRESHOLD_RULE (changing the rule moves the line), glucose line only for one context; chart geometry; S-027 cards
- [X] T002 [P] `tests/integration/test_hlt_history_page.py` — US-4 #1 – #4 and the contract; US-3 #1 – #3; no "Alert" word; no input that edits a value

### Implementation

- [X] T003 `app/mb360/hlt/history.py` (T001)
- [X] T004 Routes, `history.html`, `instructions.html`, links on S-023 and S-008; labels in `docs/ui-label-reference.md` (T002)

## Phase 2: Polish

- [X] T005 Run the quickstart at phone width; build log entry; `start_feature.py --check`, `check_env.py --repo`
