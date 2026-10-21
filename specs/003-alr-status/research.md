# Research: ALR status (US-2, FR-018)

## R1. Stack and structure
- **Decision**: same project and stack as `specs/001-alr-core`; new modules in `app/mb360/alr/`.
- **Rationale**: Workshop Guide — later features reuse the plan of the first.

## R2. Rows of S-029 (FR-002, FR-003)
- **Decision**: one row per METRIC_REPORT of the mother plus one row per Chatbot CARE_CASE of the mother. Report row: metric (or "Symptom"), threshold label (THRESHOLD_RULE, "Not assessed" for a symptom report), value with unit, symptoms, `submitted_at`, case status or "No action needed" when there is no case (BR-009). Chatbot row: "Chatbot", first line of the question, case `created_at`, status, no label (S-029 SR-002). Newest first (§10 Q17 — S-029 §4).
- **Filters**: status = the 4 statuses or All (a "No action needed" report appears only under All); type = Blood pressure / Blood glucose / Urine protein / Symptom / Chatbot / All.

## R3. Progress of S-026 (BR-012, D-43)
- **Decision**: 4 steps in order Not viewed, Viewed, Escalated to doctor, Resolved. A step is "done" when CASE_STATUS_HISTORY has the row (time + actor "Nurse name" / "Dr. name"; the first row shows "Report submitted"). "Escalated to doctor" is "skipped — No doctor escalation needed" when the case reached Resolved without it; any step not reached yet is "pending" (empty circle).

## R4. Response or Safety note (BR-011, FR-007)
- **Decision**: STAFF_RESPONSE rows of the case, newest last, each "Response from {Nurse|Dr.} {name}" with the template content and / or custom text. When there is none, the "Safety note" box is shown instead (content placeholder — Complexity Tracking).

## R5. Notifications (FR-018)
- **Decision**: `notify(conn, case_id, event, now, staff_id=None)` writes one NOTIFICATION (`type` = Report, `case_id`) when the mother's NOTIFICATION_PREFERENCE.`report_response` = 1. Events and wording:
  - case created (ALR FR-021): S-009 #11 — title "Your {metric} report has been sent to clinical staff", subtitle "{value} · {label}" (symptom report: "Your Symptom report …", subtitle the symptoms; chatbot case: "Your question has been sent to a nurse").
  - staff response (CLI FR-024): S-009 #8 — title "{Nurse|Doctor} {name} responded to your {metric} report", subtitle "Report {code} · {status}".
  - status change to Viewed / Escalated to doctor / Resolved (CLI FR-004, FR-019, FR-016): title "Your {metric} report is {status}", subtitle "Report {code}" — *interpretation*, copied to spec §10 Q23.
  - A "Viewed" step recorded automatically on escalate / close (D-43) gives no separate notification: one notification per action.
- **Rationale**: FR-018 "when her case changes status or receives a staff response"; S-009 SR-001 Report type → S-026.
- Titles are cut to 100 characters, subtitles to 200 (schema).

## R6. Chatbot cases on S-029 / S-026
- **Decision**: built from CARE_CASE (`case_source` = Chatbot) → CHAT_MESSAGE (question, `sent_at`); no code (§10 Q16), no value, no symptoms (S-026 SR-008).
