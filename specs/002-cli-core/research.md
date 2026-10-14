# Research: CLI core (US-1, US-2)

## R1. Stack and structure

- **Decision**: reuse the stack and project of `specs/001-alr-core` (FastAPI + Jinja2 + SQLite + pytest); new package `app/mb360/cli/`.
- **Rationale**: Workshop Guide — "for the second feature onward: use the stack and project structure in specs/001-.../plan.md".
- **Alternatives**: a separate web app for clinical staff (two projects for one demo).

## R2. Status machine (BR-002, D-43)

- **Decision**: one function per action, each checking role and current status, writing CARE_CASE and CASE_STATUS_HISTORY in one transaction:
  - Mark as viewed (nurse): Not viewed → Viewed.
  - Escalate to doctor (nurse): from Not viewed (records Viewed first, same staff, same time) or Viewed → Escalated to doctor; `assigned_doctor_id` = active PATIENT_ASSIGNMENT doctor.
  - Close case: nurse — from Not viewed (records Viewed first) or Viewed → Resolved; doctor — from Escalated to doctor → Resolved; `closed_at`, `closed_by` set.
  - Send guidance (nurse; doctor only on Escalated to doctor): STAFF_RESPONSE row, status unchanged (BR-008).
  - Any other combination → refused (HTTP 403 for a role not allowed, 409 for a status that does not allow it); nothing written.
- **Rationale**: the permission table of spec §5.2 and the forward-only rule; the seed already holds exactly these histories (C7: Viewed and Escalated at the same minute by the same nurse).
- **Alternatives**: a generic "set status" endpoint (would allow backwards moves).

## R3. Responsible doctor (D-68)

- **Decision**: the active assignment is the PATIENT_ASSIGNMENT row of the mother with `valid_from` ≤ today and (`valid_to` empty or `valid_to` ≥ today).
- **Rationale**: spec §6 "valid_to empty = still active"; a `valid_to` equal to today is still the last day of the assignment. *Interpretation* — the inclusive end day is not stated; copied to the spec as part of §10 Q10.
- **Alternatives**: `valid_to` > today (exclusive).

## R4. Doctor notification (ALR FR-009, DM-32)

- **Decision**: no row is written; the "Notifications (n)" badge on S-061 for a doctor = number of cases "Escalated to doctor" with `assigned_doctor_id` = that doctor.
- **Rationale**: S-061 screen spec #4 and DM-32 (resolved): derived, not stored.

## R5. Threshold label and content columns of S-061

- **Decision**: label from `mb360.alr.thresholds.evaluate` (THRESHOLD_RULE); "Not assessed" for Symptom and Chatbot cases (BR-007); content = metric for a metric report, symptoms (UI wording) for a symptom report, the question text for a chatbot case; "Submitted at" = METRIC_REPORT.`submitted_at`, or CARE_CASE.`created_at` for a chatbot case (screen spec #13).

## R6. Chatbot transcript (FR-003, D-78)

- **Decision**: Case → `chat_message_id` → CHAT_MESSAGE → all CHAT_MESSAGE rows with the same `conversation_id`, ordered by `sent_at`; the escalated question is marked.

## R7. Staff identity (§10 Q11 open)

- **Decision**: `/staff` lists seed STAFF; every clinical route carries `{staff_id}`; the header shows "Nurse: name" or "Dr. name" from STAFF.`role` (BR-005).
- **Rationale**: login is out of scope until Session 11 (Workshop Guide; agent-prompts §2).
