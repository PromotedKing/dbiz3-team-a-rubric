# HTTP routes: ALR core (US-1)

Server-rendered pages (HTML). Paths are for the demo; `{user_id}` is the mother chosen on `/` (no login until Session 11).

| Method | Path | Screen | Behaviour | Spec |
|---|---|---|---|---|
| GET | `/` | demo page | lists seed mothers; choosing one opens her S-027 | Complexity Tracking |
| GET | `/m/{user_id}/instructions` | S-027 | active Doctor's instructions (metric cards with "+ Report metric") and "+ Report symptoms" | FR-010, BR-006 |
| GET | `/m/{user_id}/report?metric={metric}` | S-025A | form for the chosen metric, or symptom mode (`metric=Symptom`); "Change metric ▾" lists only active instructions + symptom mode; instruction box shown for a metric, hidden in symptom mode; threshold card text from THRESHOLD_RULE | FR-011 – FR-013, US-1 #1 – #3 |
| POST | `/m/{user_id}/report` | S-025A → result | fields: `metric`, `systolic`, `diastolic` (blood pressure), `value` (glucose), `level` (urine protein), `glucose_context`, `measured_at`, `symptoms` (multi), `other_symptom_text`, `note`. Invalid → S-025A again with field errors (HTTP 422). Valid → store (FR-020), threshold check (BR-004), case (FR-021), then redirect (303) per BR-008 | FR-014, FR-020, FR-021, BR-008, BR-017 |
| GET | `/m/{user_id}/reports/{report_id}/alert` | S-028 | "Metric alert": value, measured time, threshold, "Your report has been sent to clinical staff", "Doctor's guidance" (instruction guidance or the default template), buttons View status / Call hotline / nurse / Close; Close returns to S-027 and does not cancel the report | FR-007, BR-002, BR-010, BR-013, BR-014 |
| GET | `/m/{user_id}/reports/{report_id}` | S-026 (minimal) | report details + status "Not viewed" ("Report submitted" message after a branch-2 submit) | FR-005, US-1 #5 |

Redirect targets after POST (BR-008):

| Result | Redirect |
|---|---|
| Above threshold (with or without symptoms) | `/m/{user_id}/reports/{report_id}/alert` |
| Not above threshold, ≥ 1 symptom | `/m/{user_id}/reports/{report_id}?submitted=1` |
| Not above threshold, "No symptoms" | `/m/{user_id}/instructions?submitted=1` |

Rules for every page: the word "Alert" appears only on S-028 (BR-010); dates are shown `dd/mm/yyyy · HH:mm` (D-27).
