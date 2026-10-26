# HTTP routes: CLI instructions (US-3)

| Method | Path | Screen | Behaviour | Spec |
|---|---|---|---|---|
| GET | `/staff/{staff_id}/cases/{case_id}` | S-064 | for a doctor: each instruction row has "Edit" (fills the form); form "Add / edit instruction" (Doctor only): metric, note, template, custom text, "Cancel" / "Save instruction"; for a nurse: rows only, no "Edit", no form | FR-025, S-064 #6 – #11 |
| POST | `/staff/{staff_id}/cases/{case_id}/instructions` | S-064 | fields `metric`, `note`, `template_id`, `custom_text`; success → 303 to S-064; nurse → 403; invalid → 422; nothing written unless 303 | FR-025, CLI BR-001, BR-006 |

No route for FR-019: there is no visit-insert path in the MVP (D-59).
