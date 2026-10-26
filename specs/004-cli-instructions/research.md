# Research: CLI instructions (US-3) + ALR FR-019

## R1. Saving an instruction (FR-025, CLI BR-006)
- **Decision**: `save_instruction(conn, user_id, doctor_id, now, metric, note, template_id, custom_text)`; refused (403) for a nurse; metric must be Blood pressure / Blood glucose / Urine protein (422); custom text ≤ 1000 (422); template must exist (422). If the mother has an active instruction for that metric it is updated (note, guidance, `flagged_by`, `flagged_at` = today); otherwise a new active WATCH_FLAG is inserted with `visit_id` empty. One transaction.
- **Rationale**: S-064 #8 – #11; DM-21 default (one active instruction per metric, checked by the seed generator); HLT §10 Q19 open.
- **Effect for the mother**: S-027 / S-025A list active instructions and S-028 reads `template_id` / `custom_text` of the instruction (already built in `specs/001-alr-core`), so nothing changes on the mother side.

## R2. ALR BR-001
- **Decision**: no code path sets `active = 0` or deletes a WATCH_FLAG; a test runs a report → case → escalate → close cycle and checks the instructions are unchanged, and checks that a nurse cannot save one.

## R3. Visit-result notification (FR-019, BR-003)
- **Decision**: `notify_visit_result(conn, visit_id, now)` writes one NOTIFICATION `type` = Visit result, `visit_id`, title "New visit results available", subtitle "Visit dd/mm/yyyy" (S-009 #9), when NOTIFICATION_PREFERENCE.`new_visit_result` = 1; no threshold label and no word "Alert".
- **Rationale**: ALR FR-019, BR-003, D-22; S-009 #9. The seed holds its own Visit result notifications, so start-up does not call the function (no duplicates).
