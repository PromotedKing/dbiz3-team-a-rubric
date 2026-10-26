# Data model: HLT dashboard (US-1, US-2)

Data model: **`data/data-model-MB360.md`** (§6), schema `data/schema/schema-MB360.sql`. No field of its own.

| Table | Read / write | Through |
|---|---|---|
| VISIT | read: latest visit date | FR-005, BR-001 |
| HEALTH_METRIC_RECORD | read: visit values, latest self-tracked values; write: Group 1 Self-entered records from S-024 | FR-005, FR-007, FR-008, BR-003, BR-004 |
| THRESHOLD_RULE | read: labels (Report check) and the fetal heart rate reference range (Display only) | FR-001, BR-005, ALR BR-004 |
| WATCH_FLAG, CARE_CASE | read: the two cards | FR-005, FR-008 |
| PREGNANCY_PROFILE | read: EDD for the gestational week of a new record | FR-007 |
