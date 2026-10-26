# Research: TML timeline (US-1, US-2)

## R1. Week arithmetic (FR-003, FR-006)
- **Decision**: week N runs from (EDD − 280 days) + 7N to + 6 days; current week = (280 − (EDD − today)) // 7 (same rule as ALR FR-015 and the seed). S-048 opens on the current week; `?week=N` (0 – 42) shows another week.

## R2. Week data (FR-003, FR-005, FR-012, BR-001, BR-003, BR-008, D-04, D-75)
- **Decision**: for the week's date range — daily indicators: HEALTH_METRIC_RECORD rows with `measured_at` in the range, grouped by day (newest first), each "metric — value unit · source"; no label added (BR-008); visit cards: VISIT rows with `visit_date` in the range — "Visit dd/mm/yyyy", "From visit", ultrasound image, fetal length (cm), estimated weight (g), "Measurements per ultrasound report dated dd/mm/yyyy", doctor's note; "No visit this week." otherwise, never system-generated measurements (BR-003); diary entries with `gestational_week` = N (text, mood, first photo); Family Messages with `week` = N.

## R3. Prefetch (FR-004)
- **Decision**: `load_week` stores weeks N − 1, N, N + 1 in a module-level cache keyed by (mother, week); a later request for an adjacent week is served from the cache; `diary.save` clears the mother's entries.

## R4. Diary entry (FR-008 – FR-010, BR-002, BR-005, BR-006)
- **Decision**: content required; mood optional (one of Happy / Calm / Nervous / Tired / Worried); 0 – 5 photos, each JPG or PNG (checked by file signature, not only the name) and ≤ 10 MB (D-46). `entry_date` = today and `gestational_week` = current week, whatever week was being viewed (BR-002, BR-005). One transaction writes DIARY_ENTRY + DIARY_IMAGE rows (`sort_order` 1 – 5); files are written to `media/diary/` only after validation; nothing is written on error. No route edits or deletes an entry (BR-006). After saving: S-048 of the current week with "Diary entry saved" (S-053).
