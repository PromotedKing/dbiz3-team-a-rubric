# Screen Spec: S-105 Journey review & album

| Field | Value |
|---|---|
| Screen ID | `S-105` (new ID, not in the DBIZ2 Screen List — D-75) |
| Screen name | My journey (journey review by stage + PDF keepsake album) |
| Actor | Mother |
| Priority | Must (PRD M4 — D-75) |
| Belongs to module | `spec-TML.md` |
| Mockup image | not drawn yet (`img/S-105.png` to be added) |
| Status | Draft (14/10/2026 — PRD alignment) |

> **S-105 layout (D-87, proposed):** The stage selector and statistics precede the visible week cards, newest first. The current week's card carries "Hiện tại" when present in the selected stage. The Highlights grid, its timeline link and the week disclosure are removed. The bottom PDF control stays available according to the selected stage's content. The album presents weeks oldest first.

## 1. Purpose

Let the mother look back over one stage of her pregnancy, or the whole journey, and export it as a PDF keepsake album to her device (PRD M4: "review her entire journey and compile it into a commemorative keepsake album exported directly to her device (PDF format)").

**Shown when:** the mother taps "My journey ›" on `S-048` (Home tab, D-30).

**The user leaves this screen when:** she taps ← (`S-048`), ✕ (`S-083`) or a tab.

## 2. Mockup

Not drawn yet. Until the image exists, this element inventory is the reference.

## 3. Element inventory

| # | Element | Type | Content / data source | Required | Validation |
|---|---|---|---|---|---|
| 1 | ← button | Button | navigation | Yes | — |
| 2 | Title "My journey" | Header | static | No | — |
| 3 | ✕ button | Button | closes the sub-app (D-01) | Yes | — |
| 4 | Stage selector: "First trimester (weeks 0 – 13)", "Second trimester (14 – 27)", "Third trimester (28 – 42)", "Full journey" | Toggle (segmented) | stage (`spec-TML.md` FR-013); boundaries Pending SME (`spec-TML.md` Q16); a stage after the current week is shown as "Not reached yet" | Yes | exactly 1 selected; default = the current stage |
| 5 | Week block header "Week N · dd/mm/yyyy – dd/mm/yyyy", with "Hiện tại" on the current week's card | Header (list group) | derived from the EDD (`spec-ACC.md` Profile) | No | visible without expanding a control, newest first. Weeks without content are not listed |
| 6 | Visit card "Visit dd/mm/yyyy" + label "From visit" + ultrasound image | Card | Visit — visit_date, ultrasound_image (`spec-HLT.md` §6) | No | — |
| 7 | Diary entry "dd/mm/yyyy · text" + mood + photos | List item | Diary Entry, Diary Image (`spec-TML.md` §6) | No | read-only (D-60) |
| 8 | Messages to Baby "From Mom / From Dad · dd/mm/yyyy — text" | Text | Family Message (`spec-TML.md` §6) `[PENDING CLIENT: D-03]` | No | — |
| 9 | Empty state "Nothing to show for this stage yet." | Empty state | the stage has no Visit, Diary Entry or Family Message `[NEEDS CLARIFICATION: wording — spec-TML.md Q18]` | — | — |
| 10 | "Export PDF album" button (primary) | Button | builds the PDF of the selected stage or full journey (`spec-TML.md` FR-014) | Yes | disabled when the stage has no content |
| 11 | 5-tab bar, "Home" selected | Toggle (tab) | navigation (D-30) | Yes | — |

## 4. States

| State | What the user sees | Trigger |
|---|---|---|
| Default | current stage selected; its weeks with visits, diary entries and messages | screen opened from `S-048` |
| Week without diary or unavailable image | visit and message content stays visible. Missing ultrasound images use the existing labeled placeholder and unavailable diary photos are omitted. If a displayed image fails to load, its alternative text remains visible | week with partial content |
| Stage not reached | "Not reached yet" in place of the week list; "Export PDF album" disabled | a stage after the current week is selected |
| Empty (no data) | #9; "Export PDF album" disabled | the selected stage has no content |
| Loading | shared skeleton (D-27) while the stage loads; progress indicator while the PDF is built `[NEEDS CLARIFICATION: not drawn]` | stage selected / export tapped |
| Error | shared error component + "Retry" (D-27) | loading the stage or building the PDF failed |
| Success / confirmation | the device's save / share sheet opens with the PDF file | PDF built |

## 5. Interactions and navigation

| # | Element | User action | System response | Goes to screen |
|---|---|---|---|---|
| 1 | Stage selector | tap | loads the stage content (FR-013) | stays |
| 2 | "Export PDF album" | tap | builds the PDF on request and hands it to the device; nothing is stored by the system (FR-014, BR-007) | device save / share sheet |
| 3 | ← | tap | — | `S-048` |
| 4 | ✕ | tap | asks for confirmation to close the sub-app | `S-083` |
| 5 | Tab | tap | — | `S-008` / `S-023` / TCI app / `S-031` / `S-103` |

## 6. Screen-level rules

| Rule ID | Rule | Source |
|---|---|---|
| SR-001 | The journey shows only the mother's own visits, diary entries and Messages to Baby; visit data is read-only. | `spec-TML.md` BR-001, BR-007 |
| SR-002 | The PDF album is generated on request and not stored or sent anywhere by the system. | `spec-TML.md` BR-007; D-75 |
| SR-003 | Stage boundaries are weeks 0 – 13 / 14 – 27 / 28 – 42 until the SME confirms them. | D-75; `spec-TML.md` Q16 |
| SR-004 | No system-generated weekly content (Tips, "Size of") appears in the journey or the album. | D-02 `[PENDING CLIENT: D-02]`; D-04 |

## 7. Linked requirements

| FR ID (from the module spec) | What this screen does for it |
|---|---|
| FR-013 (`spec-TML.md`, new — D-75) | Journey review by stage |
| FR-014 (`spec-TML.md`, new — D-75) | PDF keepsake album export |
| FR-011 (`spec-TML.md`) | Messages to Baby in the journey `[PENDING CLIENT: D-03]` |

## 8. Responsive and accessibility notes

- Ultrasound and diary images need alternative text (e.g. "Ultrasound image, 15/09/2026").
- The stage selector wraps to two lines on narrow screens.

## 9. Open questions

| # | Question | Blocking? | Status |
|---|---|---|---|
| 1 | Trimester boundaries (`spec-TML.md` Q16). | No | Open (Pending SME) |
| 2 | Which visit fields go into the album (images and dates only, or measurements and the doctor's note); page layout of the PDF (`spec-TML.md` Q18). | No | Open |
| 3 | Wording of the empty and "Not reached yet" states (`spec-TML.md` Q18). | No | Open |

---

## Completion checklist

- [ ] The mockup is a separate cropped image file, named with the Screen ID. — not drawn yet (D-75)
- [x] Every visible element in the mockup appears in the element inventory. — the inventory is the reference until the image exists
- [x] Every input element has a validation rule or an explicit `[NEEDS CLARIFICATION]`.
- [x] All states are filled in, or marked `[NEEDS CLARIFICATION]` with a reason.
- [x] Every navigation target is a Screen ID that exists in the Screen List.
- [x] Every element that displays data names the field it displays, matching the module spec.
