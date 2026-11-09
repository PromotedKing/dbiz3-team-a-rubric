# Implementation Plan: ACC profile — Profile, edit, notification settings and notification list

**Branch**: `sang/009-acc-profile` (based on `sang/tci-ui-shell`, PR #15) | **Date**: 2026-11-02 | **Spec**: [spec.md](spec.md) (snapshot of `specs/spec-ACC.md`)

**Input**: Feature specification from `specs/009-acc-profile/spec.md`; look from `screens/ui-final` (Màn 9, 12, 24, 25) as D-80 limits it.

## Summary

Build ACC **US-3 (P2)** "View and edit my profile" (S-103, S-011, FR-001, FR-002, FR-017, FR-020, FR-022 – FR-024, BR-003), the notification settings S-010 (FR-027) and the notification list S-009 behind the "From doctor" tab (FR-025, FR-026). No new table or column: PREGNANCY_PROFILE, EMR_LINKAGE_REQUEST, CONSENT_RECORD, NOTIFICATION_PREFERENCE, NOTIFICATION and WATCH_FLAG are read; only the height, the due date when not linked, the preference switches and `read_at` are written.

## Technical Context

**Language/Version**: Python 3.11+ (uv) — unchanged · **Primary Dependencies**: unchanged · **Storage**: SQLite from schema + seed (unchanged) · **Testing**: pytest · **Target**: FastAPI + Jinja2 pages, phone width

## Constitution Check

| Principle | How this plan complies | Status |
|---|---|---|
| I. The spec is the source of truth | ACC US-3 #1, #2, FR-025, FR-026, BR-002, BR-003; screen specs S-009, S-010, S-011, S-103. Open points stay open (table below) | PASS |
| II. Business rules are test-first | Tests for BR-003, FR-020, FR-025, FR-026 and the switches written and seen failing first | PASS |
| III. Thin vertical slices | One mother-side area: the "Profile" and "From doctor" tabs | PASS |
| IV. Synthetic data and no secrets | Seed data only; the phone number is masked on screen | PASS |
| V. Humans approve every change | Branch + pull request reviewed by a member who did not write it (Trung reviews ACC) | PASS |

## Project Structure

```text
specs/009-acc-profile/  spec.md, plan.md, research.md, data-model.md, quickstart.md, contracts/http-routes.md, tasks.md
app/mb360/acc/profile.py   # S-103 data, S-011 validate + save, S-010 switches (BR-003, FR-020, FR-022)
app/mb360/acc/notices.py   # S-009 list, unread count, read marks, where a notification opens (FR-025, FR-026)
app/mb360/acc/routes.py    # routes of contracts/http-routes.md
app/mb360/ui.py            # t_known also reads {field} rows: stored notification titles
app/mb360/templates/       profile.html, edit_profile.html, notif_settings.html, notices.html
tests/unit/test_acc_profile.py, test_acc_notices.py
tests/integration/test_acc_profile_pages.py
```

## Complexity Tracking

| Item | Why it matters | What the plan does until it is answered |
|---|---|---|
| ACC Q13 / S-010 SR-001 — "Report responses" locked on | Team proposal, not a Client requirement | Locked on, as in S-010 and the UI package; a request to change it is refused |
| S-010 #6 — "Appointment reminders" | Could (D-77): hidden if APT is not built | Hidden; the stored value is kept |
| ACC Q16 — unread count follows the filter? | FR-025 | Counts all notifications |
| S-009 §5 #5 — does tapping mark as read? | Stated by FR-026 ("when opened") | Marked read when opened |
| S-103 §9 Q3 — where "Pregnancy information" opens | No target | S-011, as `spec-ACC` FR-024 states |
| S-011 — phone masking, height range | S-011 #6 Q; D-16 | Masked as in the UI package (`0912 ••• 678`); any number accepted, no range invented |
| S-011 — LMP when the due date is edited | LMP and due date would disagree | The stored LMP is cleared when the due date changes |
| U9, U10 of `screens/ui-final/README.md` | The package narrows S-009 and draws a structured notice | All 4 types are listed, the chips of S-009 stay; a notification opens its target (S-026, S-023, S-027, TCI app); the structured detail has no data (D-80) |
| S-103 #12, #13 — Support row, version | Package drops them | Support row kept; version line left out (no version is defined for the sub-app) |
