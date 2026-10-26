# Data model: CLI instructions + ALR FR-019

Data model: **`data/data-model-MB360.md`** (§6), schema `data/schema/schema-MB360.sql`. No field of its own.

| Table | Read / write | Through |
|---|---|---|
| WATCH_FLAG | write: insert or update `metric`, `note`, `template_id`, `custom_text`, `flagged_by`, `flagged_at`, `active` = 1 (`visit_id` empty for a new one) | CLI FR-025, BR-006 |
| STAFF | read: role (doctor only) | CLI BR-001, BR-004 |
| GUIDANCE_TEMPLATE | read: template list | FR-025 |
| VISIT, NOTIFICATION_PREFERENCE | read | ALR FR-019 |
| NOTIFICATION | write: `type` = Visit result, `visit_id`, title, subtitle | ALR FR-019, BR-003 |
