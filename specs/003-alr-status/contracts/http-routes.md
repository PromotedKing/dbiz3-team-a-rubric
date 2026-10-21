# HTTP routes: ALR status (US-2)

| Method | Path | Screen | Behaviour | Spec |
|---|---|---|---|---|
| GET | `/m/{user_id}/my-reports?status=&type=` | S-029 | the mother's reports and chatbot cases, newest first; status chips All / Not viewed / Viewed / Escalated to doctor / Resolved (default All); type All / Blood pressure / Blood glucose / Urine protein / Symptom / Chatbot (default All); a row with a status links to S-026, a "No action needed" row has no link; empty "You have not submitted any reports." | FR-001 – FR-003, FR-006, BR-009 |
| GET | `/m/{user_id}/reports/{report_id}` | S-026 (report) | replaces the minimal page of `specs/001-alr-core`: code, status, metric + label, value, measured / submitted times, symptoms, note, progress, responses or Safety note, emergency call text; "Report submitted" when `?submitted=1`; ← to S-029 | FR-005, FR-007, BR-011, BR-012 |
| GET | `/m/{user_id}/cases/{case_id}` | S-026 (chatbot case) | "Chatbot" + "Your question: …" + sent time; same progress / responses / Safety note | FR-005, S-026 SR-008 |

Links to S-029 ("My reports") are added on S-027, S-028 and S-026 (the S-008 / S-023 cards are not built).
