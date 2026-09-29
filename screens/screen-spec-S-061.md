# Screen Spec: S-061 Cases to handle

| Field | Value |
|---|---|
| Screen ID | `S-061` |
| Screen name | Cases to handle — nurse / doctor dashboard, web (DBIZ2 name: Doctor Dashboard Screen) |
| Actor | Nurse / Doctor (web) |
| Priority | Should |
| Belongs to module | `spec-CLI.md` |
| Mockup image | `img/S-061.png` (drawn for the Nurse role) |
| Status | Draft (revised 29/09/2026 — screen-spec fix #4, #9) |

## 1. Purpose

Web home page for nurses and doctors: one table, at full width, combining every case created by mothers (metric reports, symptoms, chatbot), filtered by status. (The former quick-notes panel is removed — screen-spec fix #9, CLI-03.)

**Shown when:** a nurse / doctor signs in on the web (`S-054` / `S-060`, not drawn) or clicks "Home" in the sidebar.

**The user leaves this screen when:** they click "View report ›" on a row (→ `S-064`), "Patients" (`S-062`, not drawn), "Settings" (not drawn), or "Notifications".

## 2. Mockup

![S-061](img/S-061.png)

## 3. Element inventory

| # | Element | Type | Content / data source | Required | Validation |
|---|---|---|---|---|---|
| 1 | Logo | Image | static | No | — |
| 2 | Sidebar: "Home" (selected), "Patients", "Settings" | Navigation | navigation | Yes | — |
| 3 | Title "Cases to handle" | Header | static | No | — |
| 4 | "Notifications (2)" button | Button + badge | **Doctor:** number of cases in status "Escalated to doctor" whose `assigned_doctor_id` is the signed-in doctor — derived from Case, not stored, no read / unread state (`spec-ALR.md` FR-009, DM-32, D-68; no push / SMS — ALR-03). **Nurse:** `[NEEDS CLARIFICATION: what the button shows for a nurse — no notification to clinical staff is stored (DM-32), but the mockup, drawn for the Nurse role, shows "Notifications (2)"; §9 Q5, owner Team]`. The web notification list is not drawn (S-059) | No | — |
| 5 | Role label "Nurse: Trần Thị B ▾" | Dropdown | Staff — role + full name (`spec-CLI.md` §6, D-28) | Yes | matches the signed-in user (BR-005) |
| 6 | Filters "Not viewed (1)", "Viewed", "Escalated to doctor", "Resolved", "All" (the mockup shows "All" selected, so rows of every status are visible) | Toggle (chip, single select) | Case — status (D-18); count on "Not viewed" | Yes | default: **Doctor → "Escalated to doctor"** (CLI-02); Nurse → `[NEEDS CLARIFICATION: spec-CLI.md Q5]` |
| 7 | "Sort: Newest ▾" | Dropdown | order by submission time | No | only "Newest" is shown in the mockup `[NEEDS CLARIFICATION: are there other options]` |
| 8 | Table — "Mother" column (e.g. Nguyễn Thị Lan) | Table column | User Account — full name (`spec-ACC.md` §6) | — | — |
| 9 | "Gestational age" column (e.g. Week 28) | Table column | current gestational week (calculated from the EDD) | — | — |
| 10 | "Case source" column (Metric report / Symptom / Chatbot) | Table column | Case — `case_source` (D-41) | — | one of the 3 values |
| 11 | "Content" column (e.g. Blood pressure; Dizziness, Headache; Question with a risk keyword; Urine protein) | Table column | Metric Report — metric / symptoms[]; Chatbot case: the mother's question (Chat Message — text, `spec-BOT.md` §6) | — | — |
| 12 | "Value" column + threshold label (e.g. "150/95 mmHg — Above threshold"; "— Not assessed"; "2+ — Above threshold") | Table column + Label | Health Metric Record — value, unit; threshold_label from Threshold Rule (D-17, D-52) | — | "Not assessed" only when there is no measured value |
| 13 | "Submitted at" column (`dd/mm/yyyy · HH:mm`) | Table column | Metric Report — submitted_at / Case — created_at (Chatbot case) | — | — |
| 14 | "Status" column | Label | Case — status (D-18) | — | — |
| 15 | "View report ›" link on each row | Link | opens the case | Yes | — |
| 16 | Empty state "No cases to handle." | Empty state | when the filter has no cases | — | — |
| 17 | *(Removed — screen-spec fix #9, CLI-03)* "Quick notes" panel — not drawn and not built (not in MVP v8; `spec-CLI.md` FR-011 Won't) | — | — | — | — |
| 18 | *(Removed — screen-spec fix #9)* "Write a note…" field + "Auto-saved" | — | — | — | — |

Note: the "[Role label] …" and "[Escalate to doctor] …" boxes in the mockup are annotations, described in §6. The mother names in the mockup are sample data.

## 4. States

| State | What the user sees | Trigger |
|---|---|---|
| Default (shown in mockup) | case table per filter, at full width | screen opens |
| Doctor role | header "Dr. Nguyễn Văn A"; same table with the **default filter "Escalated to doctor"**; the doctor may switch filters to view other cases, but can act only on escalated cases (Send guidance, Close case on `S-064`); no "Mark as viewed" (CLI-02, D-43 as revised) | a doctor signs in |
| Empty (no data) | "No cases to handle." | the filter has no cases |
| Loading | shared skeleton (D-27) | table loading |
| Error | shared error component + "Retry" (D-27) | loading fails |
| Success / confirmation | not applicable — the list screen has no save action; case actions are confirmed on `S-064` | — |

## 5. Interactions and navigation

| # | Element | User action | System response | Goes to screen |
|---|---|---|---|---|
| 1 | Status chip | click | filters the table (`spec-CLI.md` FR-002, FR-020) | stays |
| 2 | "Sort" | select | re-sorts the table | stays |
| 3 | "View report ›" | click | opens the quick profile with the case's Report block (FR-006) | `S-064` |
| 4 | *(Removed — Quick notes, screen-spec fix #9)* | — | — | — |
| 5 | *(Removed — Quick notes, screen-spec fix #9)* | — | — | — |
| 6 | "Notifications" | click | `[NEEDS CLARIFICATION: S-059 not drawn]` | `S-059` |
| 7 | Sidebar "Patients" / "Settings" | click | — | `S-062` / `[NEEDS CLARIFICATION: no ID yet]` |
| 8 | Role label ▾ | click | `[NEEDS CLARIFICATION: account menu not drawn]` | — |

## 6. Screen-level rules

| Rule ID | Rule | Source |
|---|---|---|
| SR-001 | The header always shows the correct role + name of the signed-in user. | D-28; `spec-CLI.md` BR-005 |
| SR-002 | One table combines cases from 3 sources; statuses use the same names as on the mother's side. | D-18, D-41 |
| SR-003 | Threshold labels are only Normal / Above threshold / Not assessed; "Not assessed" only for cases without a measured value. | D-15, D-17 |
| SR-004 | When a nurse clicks "Escalate to doctor" (on `S-064`), the case becomes "Escalated to doctor" and the responsible doctor receives a high-priority notification inside the clinical web; only a doctor can close this case. The doctor handles only cases "Escalated to doctor" (Send guidance, Close case); his default filter is "Escalated to doctor"; he does not "Mark as viewed". Which doctor receives the notification: open (`spec-CLI.md` Q10 — team suggestion for the demo: every doctor account, not decided). | D-29, D-37, D-43 as revised; `spec-CLI.md` CLI-02, BR-004; `spec-ALR.md` FR-009 |
| SR-005 | Status only moves forward (D-43); the table always shows the case's current status. | D-43 |

## 7. Linked requirements

| FR ID (from the module spec) | What this screen does for it |
|---|---|
| FR-001 (`spec-CLI.md`) | Loads the dashboard |
| FR-002, FR-020 | Case table, filtering by status |
| FR-006 | "View report ›" opens `S-064` |
| FR-008 (`spec-ALR.md`) | "Not viewed" queue |

## 8. Responsive and accessibility notes

- Web screen; minimum width `[NEEDS CLARIFICATION: not specified]`. The case table uses the full width; on narrow screens columns may scroll horizontally `[NEEDS CLARIFICATION]`.
- Statuses and threshold labels must have text, not rely on background colour alone.

## 9. Open questions

| # | Question | Blocking? | Status |
|---|---|---|---|
| 1 | Default filter when the screen opens. | No | Open (`spec-CLI.md` Q5) |
| 2 | Does the nurse see all cases or only assigned cases; which escalated cases does a given doctor see. | Yes | **Partly resolved** — a doctor sees the escalated cases assigned to him (D-68); which cases the nurse sees is still open in `spec-CLI.md` Q10 (remaining part). `spec-CLI.md` Q16 was closed by the module review (CLI-02: the doctor's default filter is "Escalated to doctor"), but which escalated cases a given doctor sees still depends on Q10. "Every doctor account sees escalated cases" is only the review's suggestion for the demo |
| 3 | Are quick notes per person or shared by the shift. | No | Resolved — not applicable: Quick notes removed (screen-spec fix #9, CLI-03) |
| 4 | The web "Notifications" (S-059), "Patients" (S-062) and "Settings" screens are not drawn. | No | Open |
| 5 | [NEEDS CLARIFICATION: what does the "Notifications (n)" button show for a nurse? No notification to clinical staff is stored (DM-32); options: hide the button for the Nurse role, or count the cases "Not viewed". The mockup (Nurse role) shows "Notifications (2)".] Owner: Team. | No | Open |

---

## Completion checklist

- [x] The mockup is a separate cropped image file, named with the Screen ID.
- [x] Every visible element in the mockup appears in the element inventory.
- [x] Every input element has a validation rule — no input fields remain after removing Quick notes; filters only.
- [x] All states are filled in, or marked `[NEEDS CLARIFICATION]` with a reason.
- [x] Every navigation target is a Screen ID that exists in the Screen List, or flagged `[NEEDS CLARIFICATION]`.
- [x] Every element that displays data names the field it displays, matching the module spec.
