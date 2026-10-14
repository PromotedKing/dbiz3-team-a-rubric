# Data model: CLI core (US-1, US-2)

The data model is **`data/data-model-MB360.md`** (§6; schema `data/schema/schema-MB360.sql`). This slice defines no field of its own.

## Tables read

| Table | Why | Through |
|---|---|---|
| STAFF | role + name in the header; permissions | FR-001, BR-004, BR-005 |
| CARE_CASE, METRIC_REPORT, REPORT_SYMPTOM, HEALTH_METRIC_RECORD | queue rows and the Report block | FR-002, FR-003, FR-014, FR-015 |
| CHAT_MESSAGE | question of a chatbot case and its whole conversation | FR-003, BR-009, D-78 |
| THRESHOLD_RULE | threshold label and threshold of the metric history | BR-007 (= ALR BR-004) |
| USER_ACCOUNT, PREGNANCY_PROFILE, PATIENT_CLINICAL_PROFILE, VISIT | profile card, medical history, latest visit, visit history | FR-007, FR-010 |
| WATCH_FLAG, GUIDANCE_TEMPLATE | Doctor's instructions block (view only); templates for "Send guidance" | FR-024 |
| PATIENT_ASSIGNMENT | responsible doctor on escalation; doctor badge | FR-019, D-68 |

## Tables written

| Table | Rows | Through |
|---|---|---|
| CARE_CASE | `status`; `assigned_doctor_id` on escalation; `closed_at`, `closed_by` on close | FR-004, FR-016/021, FR-019 |
| CASE_STATUS_HISTORY | one row per status reached (status, changed_at, changed_by = staff, role = Nurse / Doctor); "Viewed" added automatically when skipped | BR-002, D-43 |
| STAFF_RESPONSE | template and/or custom text (≤ 1000), responder, role, sent_at | FR-024 |

## Not shown / not stored

- Self-entered metrics are never read for S-064 (CLI-01).
- The doctor notification is not stored (DM-32); the badge is derived.
