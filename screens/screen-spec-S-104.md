# Screen Spec: S-104 Onboarding guide

| Field | Value |
|---|---|
| Screen ID | `S-104` (new ID, not in the DBIZ2 Screen List — D-74) |
| Screen name | Onboarding guide |
| Actor | Mother |
| Priority | Must (PRD M1 — D-74) |
| Belongs to module | `spec-ACC.md` |
| Mockup image | not drawn yet (`img/S-104.png` to be added) |
| Status | Draft (14/10/2026 — PRD alignment) |

> **v1.0.0 app (07/11/2026, D-80 – D-85):** 3 pages (ACC Q20).

## 1. Purpose

Introduce the main features of Mother & Baby 360 once, right after the mother's first agreement on `S-001` and before pregnancy setup, so that she knows where to find her health data, reports, timeline and chatbot (PRD §2: "An intuitive onboarding guide introduces key features before landing on the dashboard").

**Shown when:** the mother taps "Agree & continue" on `S-001` state 2 for the first time (`spec-ACC.md` FR-028).

**The user leaves this screen when:** she finishes the last page or taps "Skip" (→ `S-007`/`S-046` when there is no due date, otherwise `S-008`), or taps ✕ (`S-083`).

## 2. Mockup

Not drawn yet. Until the image exists, this element inventory is the reference.

## 3. Element inventory

| # | Element | Type | Content / data source | Required | Validation |
|---|---|---|---|---|---|
| 1 | Sub-app header: logo + "Mother & Baby 360" | Header | static | No | — |
| 2 | ✕ button | Button | closes the sub-app (D-01) | Yes | — |
| 3 | Guide page: illustration + title + one sentence | Card (carousel page) | static content; proposed pages: Health dashboard (visit results, Doctor's instructions), Report a metric or symptom, Pregnancy timeline & diary, Health chatbot `[NEEDS CLARIFICATION: number of pages and text — spec-ACC.md §10 Q20]` | No | — |
| 4 | Page indicator (dots) | Indicator | current page / number of pages | No | — |
| 5 | "Skip" button (secondary) | Button | ends the guide (FR-028) | Yes | — |
| 6 | "Next" button (primary); on the last page "Get started" | Button | next page; on the last page ends the guide | Yes | — |

## 4. States

| State | What the user sees | Trigger |
|---|---|---|
| Default | first guide page, "Skip" and "Next" | first agreement on `S-001` |
| Last page | "Next" becomes "Get started" | the mother reaches the last page |
| Empty (no data) | not applicable — static content | — |
| Loading | not applicable — static content | — |
| Error | not applicable — no data is loaded or saved `[NEEDS CLARIFICATION: if "guide seen" is stored, a save error is possible — spec-ACC.md §10 Q20]` | — |
| Success / confirmation | none; goes straight to the next screen | "Skip" or "Get started" |

## 5. Interactions and navigation

| # | Element | User action | System response | Goes to screen |
|---|---|---|---|---|
| 1 | "Next" | tap | shows the next page | stays |
| 2 | Guide page | swipe left / right | previous / next page | stays |
| 3 | "Skip" / "Get started" | tap | marks the guide as seen (FR-028) | `S-007`/`S-046` (no due date) or `S-008` |
| 4 | ✕ | tap | asks for confirmation to close the sub-app | `S-083` |

## 6. Screen-level rules

| Rule ID | Rule | Source |
|---|---|---|
| SR-001 | The guide is shown once, after the first agreement and before pregnancy setup; later openings skip it. | `spec-ACC.md` FR-028; D-74 |
| SR-002 | The guide can be skipped at any page. | D-74 |
| SR-003 | The guide contains no medical advice and uses the word "Alert" only for an above-threshold report. | D-22; `spec-ALR.md` BR-010 |

## 7. Linked requirements

| FR ID (from the module spec) | What this screen does for it |
|---|---|
| FR-028 (`spec-ACC.md`, new — D-74) | Shows the guide once, lets the mother skip it |
| FR-003 (`spec-ACC.md`) | Continues to the next screen after the guide |

## 8. Responsive and accessibility notes

- Illustrations need alternative text.
- "Skip" and "Next" stay visible without scrolling on the smallest supported width `[NEEDS CLARIFICATION: width not specified]`.

## 9. Open questions

| # | Question | Blocking? | Status |
|---|---|---|---|
| 1 | Number of pages, their text and images (`spec-ACC.md` §10 Q20). | No | Open |
| 2 | Is "guide seen" kept only on the device, or stored for the mother? (`spec-ACC.md` §10 Q20) | No | Open |
| 3 | Can the mother open the guide again later (for example from `S-103`)? | No | Open |

---

## Completion checklist

- [ ] The mockup is a separate cropped image file, named with the Screen ID. — not drawn yet (D-74)
- [x] Every visible element in the mockup appears in the element inventory. — the inventory is the reference until the image exists
- [x] Every input element has a validation rule or an explicit `[NEEDS CLARIFICATION]` (no input fields).
- [x] All states are filled in, or marked `[NEEDS CLARIFICATION]` with a reason.
- [x] Every navigation target is a Screen ID that exists in the Screen List.
- [x] Every element that displays data names the field it displays, matching the module spec.
