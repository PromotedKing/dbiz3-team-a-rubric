# Data model: ALR status (US-2, FR-018)

The data model is **`data/data-model-MB360.md`** (§6; schema `data/schema/schema-MB360.sql`). No field of its own.

## Tables read

| Table | Why | Through |
|---|---|---|
| METRIC_REPORT, REPORT_SYMPTOM, HEALTH_METRIC_RECORD, THRESHOLD_RULE | report rows, value, threshold label | FR-002, FR-005, BR-005, BR-009 |
| CARE_CASE, CASE_STATUS_HISTORY, STAFF | status and progress with time and actor | FR-005, BR-012 |
| CHAT_MESSAGE | question of a chatbot case | FR-002, FR-005 (S-026 #6a) |
| STAFF_RESPONSE, GUIDANCE_TEMPLATE | "Response from …" and guidance | FR-007, BR-011 |
| NOTIFICATION_PREFERENCE | "Report responses" switch | FR-018 |

## Tables written

| Table | Rows | Through |
|---|---|---|
| NOTIFICATION | `type` = Report, `case_id`, title (≤ 100), subtitle (≤ 200), `created_at`; `read_at` empty | FR-018 |
