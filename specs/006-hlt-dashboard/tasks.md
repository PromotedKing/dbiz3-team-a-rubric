# Tasks: HLT dashboard — Health metrics and self-tracked metrics

**Input**: `specs/006-hlt-dashboard/` — plan.md, spec.md (US-1, US-2), research.md, data-model.md, contracts/http-routes.md, quickstart.md

**Tests**: required by the constitution; each test task comes before the code it checks.

**Out of scope**: US-3 (S-027 cards), US-4 (S-025 metric history), valid ranges (D-16).

## Phase 1: Setup

- [X] T001 Create `app/mb360/hlt/__init__.py`; no new dependency

## Phase 2: Foundational

- [X] T002 [P] Seed test in `tests/seed/test_seed_hlt.py`: Nguyễn Thị Lan's latest visit is 15/09/2026 with Blood pressure 132/84, Fetal heart rate 145, Weight 56.5, Urine protein Negative (From visit) and no blood glucose; her latest Self-entered Group 1 values are Weight 57.0, Temperature 36.8, Heart rate 82, Sleep "22:30-06:00"; THRESHOLD_RULE has one Display only row for fetal heart rate (110–160 bpm); no Group 1 record is Doctor-assigned (HLT BR-003 constraint)

## Phase 3: US-1 + US-2 (P1) 🎯

### Tests (write first, see them fail)

- [X] T003 [P] [US1] `tests/unit/test_hlt_dashboard.py` — **FR-001, FR-005, FR-008, BR-004, BR-005**: Lan's visit rows in the S-023 order with values, units, source From visit; Blood pressure and Urine protein labelled Normal (from THRESHOLD_RULE); fetal heart rate with reference "110–160 bpm" and no label; Blood glucose "—"; cards "2 metrics: Blood glucose, Blood pressure" and the number of cases not Resolved; self-tracked latest values with Sleep "7 h 30 min" and no label; a mother with no visit has no visit section rows; changing the Display only row to 100–170 changes the reference text (not hard-coded)
- [X] T004 [P] [US2] `tests/unit/test_hlt_self_tracked.py` — **FR-007, BR-003**: saving weight 57.4 and temperature 36.9 writes 2 Group 1 Self-entered records with units and gestational week, and **no** METRIC_REPORT, CARE_CASE or NOTIFICATION; sleep 22:00 → 06:30 is stored as "22:00-06:30" with `measured_at` = wake-up; errors: value "abc", value without its time, a time after now, bedtime without wake-up, wake-up before bedtime, all fields empty → nothing written; one `xfail(reason="D-16")` for a weight of 999
- [X] T005 [P] [US1] `tests/integration/test_hlt_pages.py` — **US-1 #1 – #4, US-2 #1 – #3, BR-001**: S-023 for Lan shows "Latest visit results", "From visit", "Visit date 15/09/2026 · not editable", the values and labels, "(reference range 110–160 bpm)", the two cards linking to S-027 and S-029, "Self-entered" values with "27/09/2026 · 07:30"; no edit control for visit values; "⟳ Refresh" → "Data updated."; a mother with no visit sees "No visit results yet."; S-024 shows the 4 metrics, "Measured at", Bedtime and Wake-up time, no blood pressure / blood glucose / urine protein / fetal heart rate / height field; POST valid → 303 to S-023 with "Metrics saved" and the new weight; POST invalid → 422 with `data-error-for`; Home links to S-023; the word "alert" is absent from S-023 and S-024

### Implementation

- [X] T006 [US1] `app/mb360/hlt/dashboard.py` (R1 – R3) — makes T003 pass
- [X] T007 [P] [US2] `app/mb360/hlt/self_tracked.py` (R4) — makes T004 pass
- [X] T008 [US1] `app/mb360/hlt/routes.py` + register in `main.py`; templates `health.html`, `self_tracked.html`; "Health metrics ›" on `home.html` — makes T005 pass

## Phase 4: Polish

- [X] T009 Walk quickstart.md scenarios 1 – 5
- [ ] T010 [P] Build log entries

## Dependencies

Phase 1 → 2 → 3 → 4. T003 → T006; T004 → T007; T005 → T008.
