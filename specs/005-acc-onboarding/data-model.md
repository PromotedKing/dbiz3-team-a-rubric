# Data model: ACC onboarding (US-1, US-2)

Data model: **`data/data-model-MB360.md`** (§6), schema `data/schema/schema-MB360.sql`. No field of its own.

| Table | Read / write | Through |
|---|---|---|
| USER_ACCOUNT | write (first agreement): copy of the TCI identity — `tci_account_ref`, `full_name`, `phone`, `date_of_birth`, `sex` = Female, `record_code`, `role` = Mother; update at each opening (DM-18) | FR-011, FR-015, BR-007, D-71 |
| CONSENT_RECORD | write: `accepted` = 1, `accepted_at`, `terms_version` empty (Q17), `tci_data_permission` = 1 | FR-011, BR-004 |
| NOTIFICATION_PREFERENCE | write: defaults (DM-41) | FR-011 |
| SESSION | write: token, `role` = Mother, `created_at`, `expires_at` (12 h, Q9) | FR-015 |
| PREGNANCY_PROFILE | read (BR-006); write: `edd`, `lmp`, `edd_source` = Self-entered, `height_cm`, `first_visit_date` | FR-004, FR-005, D-72 |
| HEALTH_METRIC_RECORD | write: the weight (Group 1, Self-entered) | FR-005, D-42 |
| WATCH_FLAG, METRIC_REPORT, CARE_CASE | read: Home cards | FR-016 |
