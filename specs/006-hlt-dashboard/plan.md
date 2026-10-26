# Implementation Plan: HLT dashboard — Health metrics and self-tracked metrics

**Branch**: `sang/006-hlt-dashboard` (based on `sang/005-acc-onboarding`, PR #11) | **Date**: 2026-10-26 | **Spec**: [spec.md](spec.md) (snapshot of `specs/spec-HLT.md`)

**Input**: Feature specification from `specs/006-hlt-dashboard/spec.md`

## Summary

Build HLT **US-1 (P1)** "View the Health metrics screen" (S-023: latest visit results with source label and threshold labels, fetal heart rate with its reference range only, the "Doctor's instructions" and "My reports" cards, the latest self-tracked metrics, Refresh) and **US-2 (P1)** "Enter self-tracked metrics (optional)" (S-024: weight, temperature, heart rate, sleep; stored as Group 1, Self-entered; never threshold-checked, never a report). S-008 gets the "Health metrics ›" link. Same stack and project; based on PR #11 because the Home page lives there.

## Technical Context

**Language/Version**: Python 3.11+ (uv) — unchanged · **Primary Dependencies**: unchanged · **Storage**: SQLite from schema + seed (unchanged) · **Testing**: pytest · **Target Platform**: local laptop · **Project Type**: web application (same project) · **Constraints**: data/ read-only; threshold labels from THRESHOLD_RULE (ALR BR-004); the 110 – 160 bpm reference range read from THRESHOLD_RULE (`purpose` = Display only), never a label (D-12); "Alert" only on S-028 · **Scale/Scope**: S-023, S-024

## Constitution Check

| Principle | How this plan complies | Status |
|---|---|---|
| I. The spec is the source of truth | HLT US-1 #1 – #4, US-2 #1 – #3, FR-001 – FR-005, FR-007, FR-008, BR-001 – BR-005; screen specs S-023, S-024. Open points kept open: valid ranges (D-16), empty-section and refresh wording, measured-time default and future times, sleep rules — see Complexity Tracking | PASS |
| II. Business rules are test-first | Tests for BR-001, BR-003, BR-004, BR-005, FR-001 labels and every scenario of US-1 and US-2, written and seen failing first | PASS |
| III. Thin vertical slices | Two P1 stories on two screens | PASS |
| IV. Synthetic data and no secrets | Seed only | PASS |
| V. Humans approve every change | Branch + pull request reviewed by a member who did not write it (Ánh, HLT owner) | PASS |

## Project Structure

```text
specs/006-hlt-dashboard/  spec.md, plan.md, research.md, data-model.md, quickstart.md, contracts/http-routes.md, tasks.md
app/mb360/hlt/
├── __init__.py
├── dashboard.py     # FR-001, FR-004, FR-005, FR-008: S-023 data
├── self_tracked.py  # FR-007, BR-003: validate and store S-024 values
└── routes.py
app/mb360/templates/  health.html (S-023), self_tracked.html (S-024); home.html + "Health metrics ›"
tests/unit/test_hlt_dashboard.py, test_hlt_self_tracked.py
tests/integration/test_hlt_pages.py
```

## Complexity Tracking

| Item | Why it matters | What the plan does until it is answered |
|---|---|---|
| D-16 — valid ranges of group 1 values (US-2 #3) | Field errors | Only "is a number" is checked; one test is `xfail` with reason "D-16" |
| S-024 #6 — "Measured at" default and future times | Required when a value is entered | Prefilled with now; required when its value is entered; a time after now is refused because the schema rejects a record measured after it is created (HLT §6, same as ALR build log issue #3) |
| S-024 #12, #13 — sleep: both times required, wake-up after bedtime (proposed) | A duration needs both | Both are required when one is entered; wake-up must be after bedtime and less than 24 h later; stored as one formatted value "HH:MM-HH:MM" with `measured_at` = wake-up time, like the seed (DM-22) |
| S-024 #15 — all fields empty | Nothing to save | The form comes back with "Enter at least one metric." and nothing is saved |
| S-023 — empty "Self-tracked metrics" wording; Refresh confirmation wording | Text not drawn | "No self-tracked metrics yet." with "+ Enter self-tracked metrics"; "Data updated." |
| S-023 #11 — the drawing shows no label for urine protein | FR-001 says group 2 values carry the threshold label | Every group 2 visit value shows its label (FR-001), urine protein included |
| US-3 (S-027 cards), US-4 (S-025 metric history) | P2 | Out of scope; "View metric history" is not shown yet |
