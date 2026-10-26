# Research: HLT dashboard (US-1, US-2)

## R1. Latest visit results (FR-001, FR-005, BR-001, BR-004, BR-005)
- **Decision**: the mother's latest VISIT (by `visit_date`); its HEALTH_METRIC_RECORD rows (`visit_id`, source From visit) shown in the order of S-023: Blood pressure, Fetal heart rate, Weight, Blood glucose, Urine protein; a metric the visit did not record shows "—". Group 2 values carry the label from `alr.thresholds.evaluate` (THRESHOLD_RULE); fetal heart rate shows "(reference range 110–160 bpm)" built from the THRESHOLD_RULE row with `purpose` = Display only, and no label; group 1 has no label. Header "Visit date dd/mm/yyyy · not editable".

## R2. Cards (FR-005, FR-008)
- **Decision**: "Doctor's instructions": "{n} metrics: {names}" of the active WATCH_FLAG rows → S-027; "My reports": number of the mother's cases not Resolved + latest case status → S-029.

## R3. Self-tracked metrics section (FR-005)
- **Decision**: latest Self-entered Group 1 record per metric (Weight, Temperature, Heart rate, Sleep) with `measured_at`; sleep shown as a duration ("7 h 30 min") computed from the stored "HH:MM-HH:MM".

## R4. Storing S-024 values (FR-007, BR-003)
- **Decision**: one HEALTH_METRIC_RECORD per entered metric — `metric_group` Group 1, `source` Self-entered, units kg / °C / bpm, sleep value "HH:MM-HH:MM" (no unit) with `measured_at` = wake-up time; `gestational_week` from the EDD; `created_at` = now. Nothing else is written (no METRIC_REPORT, no case, no notification). One transaction.

## R5. Refresh (FR-003, FR-004)
- **Decision**: "⟳ Refresh" reloads the page from the database with `?refreshed=1` and shows "Data updated." (wording not drawn).
