# HTTP routes: CLI core (US-1, US-2)

`{staff_id}` = the staff member chosen on `/staff` (no sign-in until Session 11, §10 Q11).

| Method | Path | Screen | Behaviour | Spec |
|---|---|---|---|---|
| GET | `/staff` | demo page | lists seed staff (role + name) | Complexity Tracking |
| GET | `/staff/{staff_id}/cases?status=` | S-061 | header "Nurse: name" / "Dr. name"; filter chips Not viewed (count) / Viewed / Escalated to doctor / Resolved / All; default All for a nurse, Escalated to doctor for a doctor; table sorted Newest; "Notifications (n)" for a doctor; empty "No cases to handle." | FR-001, FR-002, FR-020, BR-005, CLI-02, R4 |
| GET | `/staff/{staff_id}/cases/{case_id}` | S-064 | profile, medical history, Doctor's instructions (view only), Report block (or chatbot question + conversation), metric history (From visit / Doctor-assigned only) with threshold, latest visit, visit history; action buttons per the permission table | FR-003, FR-006 – FR-008, FR-010, FR-014, FR-015, BR-004, BR-009, CLI-01 |
| POST | `/staff/{staff_id}/cases/{case_id}/view` | S-064 | Mark as viewed (nurse) | FR-004 |
| POST | `/staff/{staff_id}/cases/{case_id}/escalate` | S-064 | Escalate to doctor (nurse) | FR-019, BR-003 |
| POST | `/staff/{staff_id}/cases/{case_id}/guidance` | S-064 | fields `template_id`, `custom_text` (≤ 1000, at least one) | FR-024, BR-008 |
| POST | `/staff/{staff_id}/cases/{case_id}/close` | S-064 | Close case | FR-016, FR-021, BR-001 |

Every POST: success → 303 back to S-064; role not allowed → 403; status does not allow the action → 409; invalid guidance → 422. Nothing is written when the answer is not 303.
