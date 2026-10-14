# Screen Spec: S-064 Mother quick profile

| Field | Value |
|---|---|
| Screen ID | `S-064` |
| Screen name | Mother quick profile + case handling, web (DBIZ2 name: Patient Snapshot Screen) |
| Actor | Nurse / Doctor (web) |
| Priority | Should |
| Belongs to module | `spec-CLI.md` |
| Mockup image | `img/S-064.png` (drawn for the Nurse role) — snapshot at 26/09/2026 · 20:18, before the nurse handled Lan's case, so the case shows "Not viewed"; after handling it shows "Resolved" (`S-026`, `S-061`). The "Chatbot case" Report block is not drawn |
| Status | Draft (revised 29/09/2026 — screen-spec fix #3, #4, #10) |

## 1. Purpose

Quick profile of one mother together with the handling block for the open case: enough context for the nurse to decide whether to handle the case herself or escalate it to a doctor, and for the doctor to handle a case escalated to him (send guidance, close it) and assign metrics to monitor.

**Shown when:** the user clicks "View report ›" on `S-061`; or a doctor opens the case from the high-priority notification shown inside the clinical web (no push / SMS — ALR-03) `[NEEDS CLARIFICATION: S-059]`.

**The user leaves this screen when:** they click "←" (back to `S-061`) or a sidebar item.

## 2. Mockup

![S-064](img/S-064.png)

## 3. Element inventory

| # | Element | Type | Content / data source | Required | Validation |
|---|---|---|---|---|---|
| 1 | Sidebar: "Home", "Patients" (selected), "Settings" | Navigation | navigation | Yes | — |
| 2 | "← Mother quick profile" | Header + Button | back to `S-061` | Yes | — |
| 3 | Role label "Nurse: Trần Thị B ▾" | Dropdown | Staff — role + full name (D-28) | Yes | — |
| 4 | Profile card: photo, "Nguyễn Thị Lan", "Medical record number TC-00123", "Week 28 · Due date 20/12/2026", "Last visit 15/09/2026" | Card | User Account (full name, medical record number); Profile (EDD, gestational week); latest Visit (`spec-CLI.md` FR-007) | No | — |
| 5 | "Medical history": Obstetric history (PARA) 1001; Blood type O+; Allergies None | Card | Patient Clinical Profile (`spec-HLT.md` §6, D-42) | No | — |
| 6 | "Doctor's instructions" + the sentence "Nurses can only view; the "Edit" button and the form below are shown only when a doctor is signed in." | Card | Watch-Flag (`spec-HLT.md` §6) | No | — |
| 7 | Instruction rows "Blood pressure — Assigned 15/09/2026 · Dr. Nguyễn Văn A" + "Edit"; "Blood glucose — …" + "Edit" | List item + Link | Watch-Flag — metric, flagged_at, flagged_by | No | "Edit" shown only to doctors (D-29) |
| 8 | "Add / edit instruction" form (label "Doctor only"): "Metric to monitor" (Blood pressure ▾) | Dropdown | Watch-Flag — metric (group 2 only) (`spec-CLI.md` FR-025) | Yes (on save) | select 1 group-2 metric |
| 9 | "Note for the mother (how to measure, frequency)" — "Enter a note…" | Textarea | Watch-Flag — note | No | maximum length `[NEEDS CLARIFICATION]` |
| 10 | "Above-threshold guidance (shown on S-028 Metric alert)": "Choose a guidance template ▾" + "Add custom text for this mother (optional)…" | Dropdown + Textarea | Watch-Flag — over_threshold_guidance {template_id, custom_text} (D-24) | No | custom text ≤ **1000 characters** (D-46) |
| 11 | "Cancel" / "Save instruction" + the sentence "You can choose only a template, only custom text, or both. If there is nothing → S-028 uses the hospital's default template." | Button pair + Text | FR-025; D-24 | — | — |
| 12 | "Report BC-0926-015" block + status label "Not viewed" | Card header + Label | Metric Report — report_code; Case — status. Chatbot case: code per `spec-ALR.md` Q16 | No | — |
| 13 | "Blood pressure — 150/95 mmHg — Above threshold"; "Measured at 26/09/2026 · 20:15"; "Source — Doctor-assigned" | Text + Label | Health Metric Record — value, unit, measured_at, source; threshold_label (D-17). **Chatbot case:** replaced by "Question: [the mother's question]" + "Sent `dd/mm/yyyy · HH:mm`" + source "Chatbot" (Chat Message — text, sent_at; not drawn) | No | — |
| 14 | "Symptoms: Severe headache / dizziness / blurred vision, Other (Back ache worse in the afternoon) · Mother's note: [content]" (the image shows the D-23 example) | Text | Metric Report — symptoms[], other_symptom_text, note. Hidden for a chatbot case | No | — |
| 15 | "Mark as viewed" button | Button | Case → "Viewed" (`spec-ALR.md` FR-004; `spec-CLI.md` FR-004) | No | **nurse only** — not shown to doctors (D-43 as revised); hidden once the case is past "Viewed" `[NEEDS CLARIFICATION]` |
| 16 | "Escalate to doctor" button | Button | Case → "Escalated to doctor" + high-priority notification (`spec-CLI.md` FR-019; `spec-ALR.md` FR-009) | No | nurse only; not shown to doctors |
| 17 | "Close case" button | Button | Case → "Resolved" (FR-016) | No | nurse: only cases **not** escalated — hidden / disabled when the case is "Escalated to doctor" (D-37); doctor: **only cases "Escalated to doctor"** — hidden / disabled on other cases (CLI-02) |
| 18 | "Send guidance to the mother": "Choose a guidance template ▾" + "Or write / edit the text…" + "Send guidance" button + the sentence "The mother sees the guidance on S-026. "Close case" moves the status to "Resolved"." | Dropdown + Textarea + Button | Staff Response {template_id, custom_text} (`spec-CLI.md` FR-024; `spec-ALR.md` §6) | — | at least one of template / custom text; custom text ≤ **1000 characters** (D-46) |
| 19 | "Metric history" + "Blood pressure ▾" + chart with a "Threshold 140/90 mmHg" line (on-screen text; means systolic ≥ 140 or diastolic ≥ 90 mmHg — D-14), axis 01/09/2026 – 26/09/2026 + the sentence "Includes From visit and Doctor-assigned data, distinguished by source label." | Chart | Health Metric Record per metric — **only "From visit" and "Doctor-assigned" data** (no Self-entered data, CLI-01); Threshold Rule (FR-008, D-52) | No | — |
| 20 | "Visit 15/09/2026" + label "From visit": Blood pressure 132/84 mmHg; Fetal heart rate 145 bpm; Weight 56.5 kg; Blood glucose — | Card | Visit + Health Metric Record with source "From visit" (FR-010) | No | — |
| 21 | *(Removed — screen-spec fix #10, CLI-01)* "Self-tracked metrics" card — not drawn and not built: the mother's self-tracked metrics are for her own reference and are not shown to clinical staff | — | — | — | — |
| 22 | "Visit history": "15/09/2026 · Routine antenatal check-up — Conclusion: [content]"; "18/08/2026 · Anomaly scan — Conclusion: [content]" | List | Visit — visit_date, visit_type, conclusion (FR-010) | No | — |

Note: the "Escalate to doctor: … Close case: …" box below the 3 buttons and the "[Role label] … [Permissions] …" box in the mockup are annotations, described in §6.

## 4. States

| State | What the user sees | Trigger |
|---|---|---|
| Default — Nurse role (shown in mockup) | all blocks; no "Edit" and no instruction form; "Escalate to doctor" present | a nurse opens a case |
| Doctor role | header "Dr. [name]"; "Edit" + "Add / edit instruction" form present; no "Escalate to doctor", **no "Mark as viewed"**; on a case "Escalated to doctor": "Send guidance" and "Close case" available; on any other case: view only (handling buttons hidden / disabled) (CLI-02, D-43 as revised) | a doctor opens a case |
| Case "Escalated to doctor", Nurse role | "Close case" hidden / disabled (D-37); the case shows a red flag (D-44) `[NEEDS CLARIFICATION: how the red flag is displayed is not drawn]` | the case has been escalated |
| Case "Resolved" | handling buttons hidden / disabled `[NEEDS CLARIFICATION: not drawn]` | the case is closed |
| Chatbot case (not drawn) | the Report block shows the mother's question + sent time + source "Chatbot" in place of the value / threshold / symptoms (#13, #14), followed by the **conversation transcript** — every question and answer of the same conversation in time order, the escalated question highlighted, read-only (`spec-CLI.md` FR-003, BR-009, D-78); status label, handling buttons and "Send guidance" are the same as for a report; the metric history (#19) shows the default metric | `case_source` = Chatbot (screen-spec fix #3) |
| Empty (no data) | each empty block uses the shared empty template (D-27) | the mother has no visits / metrics yet |
| Loading | shared skeleton (D-27) | screen opens |
| Error | shared error component + "Retry" (D-27) | loading / saving fails |
| Success / confirmation | the new status appears immediately on the Report block label; toast `[NEEDS CLARIFICATION: wording]` | action succeeds |

## 5. Interactions and navigation

| # | Element | User action | System response | Goes to screen |
|---|---|---|---|---|
| 1 | "Mark as viewed" | click | Case → Viewed; recorded in status_history (D-43) | stays |
| 2 | "Escalate to doctor" (nurse) | click | Case → Escalated to doctor ("Viewed" recorded automatically if missing — D-43); high-priority notification to the responsible doctor inside the clinical web (`spec-ALR.md` FR-009; the doctor = the mother's active responsible doctor, D-68; the notification is not stored, DM-32); the mother receives a notification (`spec-ALR.md` FR-018) | stays |
| 3 | "Close case" | click | Case → Resolved (permissions D-37: nurse — not escalated; doctor — escalated only, CLI-02); the mother receives a notification | stays |
| 4 | "Send guidance" | click | saves the Staff Response; the mother sees it on `S-026`; **no status change** (D-37) | stays |
| 5 | "Edit" / "Save instruction" (doctor) | click | saves the Watch-Flag (FR-025); the mother sees it on `S-027` | stays |
| 6 | "Blood pressure ▾" (Metric history) | select | changes the metric on the chart | stays |
| 7 | "←" | click | — | `S-061` |

## 6. Screen-level rules

| Rule ID | Rule | Source |
|---|---|---|
| SR-001 | Role-based permissions: Nurse — view, Mark as viewed, Escalate to doctor, Send guidance, Close case for cases not escalated to a doctor. Doctor — view; on cases **"Escalated to doctor"** only: Send guidance, Close case (clears the red flag); add / edit Doctor's instructions. The doctor does not "Mark as viewed" (an escalated case already has its "Viewed" step) and cannot act on cases that are not escalated. | D-29, D-37, D-43 as revised, D-44; `spec-CLI.md` CLI-02, permission table |
| SR-002 | "Send guidance" does not change the status; only "Close case" moves it to "Resolved". | D-37 |
| SR-003 | Every value is shown with a source label. | D-10 |
| SR-004 | If there is no above-threshold guidance, S-028 uses the hospital's default template. | D-24 |
| SR-005 | No Call / Message / SpO2 / "via Bluetooth" / document links / "Risk Level" on this screen. | `spec-CLI.md` §1 Out of scope |
| SR-006 | For a chatbot case the whole conversation of the escalated question is shown, so the mother does not have to repeat herself; other conversations of the mother are not shown. | `spec-CLI.md` BR-009; D-78 |

## 7. Linked requirements

| FR ID (from the module spec) | What this screen does for it |
|---|---|
| FR-003, FR-014, FR-015 (`spec-CLI.md`) | The case's Report block |
| FR-004 | Mark as viewed |
| FR-005, FR-016, FR-021 | Status change, Close case |
| FR-007 | Profile card + Medical history |
| FR-008 | Metric history ("From visit" and "Doctor-assigned" data only — the self-tracked card is removed, CLI-01) |
| FR-010 | Visit, Visit history |
| FR-019 | Escalate to doctor |
| FR-024 | Send guidance to the mother |
| FR-025 | Add / edit Doctor's instructions |
| FR-004, FR-009 (`spec-ALR.md`) | Status change and doctor notification |

## 8. Responsive and accessibility notes

- Web screen; minimum width `[NEEDS CLARIFICATION: not specified]`. On narrow screens, the left column (profile, medical history, instructions) stacks above the Report block.
- A button disabled by permissions must have a readable reason (e.g. tooltip "Only a doctor can close an escalated case") `[NEEDS CLARIFICATION]`.

## 9. Open questions

| # | Question | Blocking? | Status |
|---|---|---|---|
| 1 | How the red flag (D-44) and the button states are displayed when the case is escalated / closed — not drawn. | No | Open |
| 2 | How a Chatbot case is displayed in the Report block. | No | Resolved (screen-spec fix #3) — the mother's question + sent time + source "Chatbot" replace value / threshold / symptoms (§4 "Chatbot case"); still to be drawn |
| 3 | Contacting the mother to verify (FR-023) — no call button. | No | Resolved — FR-023 is Won't (`spec-CLI.md` CLI-05, Q8) |
| 4 | Is a list of all the mother's cases needed on this screen (FR-009, FR-013). | No | Open (`spec-CLI.md` Q13) |
| 5 | The "Guidance template" list. | No | Open (`spec-CLI.md` Q15) |
| 6 | Where the Medical history and Visit data come from in the MVP. | No | Resolved (D-59): demo seed data (`spec-HLT.md` Q14) |
| 7 | [NEEDS CLARIFICATION: the "Notifications (n)" button is drawn in the header of `S-061` but not on this screen. Is it also available on `S-064` (so that a doctor can see a new escalation without going back to `S-061`), or only on `S-061`? The mockup is not changed until this is answered.] | No | Open |

---

## Completion checklist

- [x] The mockup is a separate cropped image file, named with the Screen ID (the chatbot-case Report block is not drawn — §4).
- [x] Every visible element in the mockup appears in the element inventory.
- [x] Every input element has a validation rule or an explicit `[NEEDS CLARIFICATION]`.
- [x] All states are filled in (including the Doctor role, escalated case, Chatbot case), or marked `[NEEDS CLARIFICATION]`.
- [x] Every navigation target is a Screen ID that exists in the Screen List.
- [x] Every element that displays data names the field it displays, matching the module spec.
