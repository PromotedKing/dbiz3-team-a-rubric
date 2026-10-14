# Data model: ALR core (US-1)

The data model is **`data/data-model-MB360.md`** (logical model §6, physical draft `data/schema/schema-MB360.sql`). This slice defines no field, table or type of its own; it only lists what it reads and writes.

## Tables read

| Table | Why | Through |
|---|---|---|
| USER_ACCOUNT | the mother chosen on the demo page | Complexity Tracking (login: Session 11) |
| PREGNANCY_PROFILE | `edd` → gestational week | FR-015 |
| WATCH_FLAG | active instructions → metrics the mother may report; instruction box on S-025A; `template_id` / `custom_text` for S-028 | FR-011, BR-006, FR-007, BR-013 |
| GUIDANCE_TEMPLATE | default template (`is_default = 1`) when the instruction has no guidance | BR-013 |
| THRESHOLD_RULE | rows with `purpose = 'Report check'` | BR-004 |

## Tables written

| Table | Rows written | Through |
|---|---|---|
| HEALTH_METRIC_RECORD | 1 per metric report (none for a symptom report): `metric`, `metric_group` = Group 2, `value`, `unit`, `glucose_context`, `measured_at`, `source` = Doctor-assigned, `gestational_week`, `created_at` | FR-020, FR-015 |
| METRIC_REPORT | 1 per report: `report_code` (provisional, ALR Q16), `metric`, `health_metric_record_id`, `other_symptom_text`, `note`, `submitted_at`, `watch_flag_id` | FR-020, BR-006 |
| REPORT_SYMPTOM | ≥ 1 per report; "No symptoms" alone or real symptoms (D-73 list) | FR-020, BR-017 |
| CARE_CASE | 0 or 1 per report: `case_source` = Metric report (above threshold) or Symptom (not above threshold, ≥ 1 symptom); `status` = Not viewed | FR-021, BR-007, BR-008 |
| CASE_STATUS_HISTORY | 1 first row per case: `status` = Not viewed, `role` = System, `changed_by` NULL | FR-021 |

## Not stored

- The threshold label (Normal / Above threshold / Not assessed) is computed from THRESHOLD_RULE each time (DM-14 default).
- The guidance shown on S-028 is not copied with the report (DM-15 default).

## Invariants the tests check (all already true in the seed)

- A metric report has exactly one Health Metric Record with the same mother, metric and `created_at` = `submitted_at`; a symptom report has none (D-41).
- `watch_flag_id` = the mother's active instruction for that metric; a symptom report has none (BR-006).
- A case exists ⇔ above threshold or ≥ 1 real symptom (BR-008); its first history row is written by the System (FR-021).
- "No symptoms" never appears with another symptom (BR-017).
