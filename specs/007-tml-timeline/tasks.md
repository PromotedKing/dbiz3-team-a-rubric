# Tasks: TML timeline — pregnancy week view and diary

**Input**: `specs/007-tml-timeline/` — plan.md, spec.md (US-1, US-2), research.md, data-model.md, contracts/http-routes.md, quickstart.md

**Tests**: required by the constitution; each test task comes before the code it checks.

**Out of scope**: US-3 writing Messages to Baby (`[PENDING CLIENT: D-03]`), US-4 journey review and PDF album, editing / deleting diary entries (D-60).

## Phase 1: Setup

- [X] T001 Create `app/mb360/tml/__init__.py`; add `media/` to `.gitignore`; no new dependency

## Phase 2: Foundational

- [X] T002 [P] Seed test in `tests/seed/test_seed_tml.py` (facts checked with queries): Lan's EDD 2026-12-20; her visits 18/08/2026 (week 22, ultrasound `us/VIS-002.jpg`, 27 cm, 480 g, report 18/08/2026) and 15/09/2026 (week 26, no ultrasound); 3 diary entries (week 22 Nervous; week 28 Happy and Calm), each with 1 photo; 2 Family Messages in week 28 (Mother, Father)

## Phase 3: US-1 + US-2 (P1) 🎯

### Tests (write first, see them fail)

- [X] T003 [P] [US1] `tests/unit/test_tml_weeks.py` — **FR-003, FR-004, FR-005, FR-006, FR-012, BR-003, BR-008**: Lan's current week = 28, range 27/09 – 03/10/2026; week 26 = 13/09 – 19/09 with one visit card (15/09/2026, no ultrasound fields) and indicators of 15/09/2026 grouped by day with source From visit and no label; week 22 visit card has image path, 27 cm, 480 g, report date 18/08/2026; week 28: no visit, indicators of 27/09/2026 (Weight 57.0 kg Self-entered …), 2 diary entries, 2 messages (Mother then Father); week 27 lists the reported blood pressure values of 25/09 and 26/09 (Doctor-assigned); after loading week 28 the cache holds weeks 27 and 29 (prefetch), and weeks 0 / 42 have no previous / next
- [X] T004 [P] [US2] `tests/unit/test_tml_diary.py` — **FR-008 – FR-010, BR-002, BR-005, BR-006**: save text + mood Calm + 1 PNG → DIARY_ENTRY (`entry_date` 2026-09-27, `gestational_week` 28 even if week 22 was being viewed) + 1 DIARY_IMAGE (`sort_order` 1, file under `diary/`) and the file exists in the media folder; errors: empty text, mood "Angry", 6 photos, a GIF / a text file renamed `.png`, a photo over 10 MB → nothing written and no file left; the mother's cached weeks are cleared after a save; the module has no update / delete function (BR-006)
- [X] T005 [P] [US1] `tests/integration/test_tml_pages.py` — **US-1 #1 – #6, US-2 #1 – #6**: Home week card links to S-048; S-048 for Lan shows "Week 28", "27/09/2026 – 03/10/2026", "‹ Week 27", "Week 29 ›", "Indicators this week", "No visit this week.", "Messages to Baby · Week 28", "From Mom", "From Dad", "Diary · Week 28", "+ Add diary entry"; `?week=26` shows "Visit 15/09/2026" and "From visit"; `?week=22` shows "Fetal length — 27 cm", "Estimated weight — 480 g", "Measurements per ultrasound report dated 18/08/2026" and the image alt text; no "Size of" / tips text (D-02); `?week=0` has no previous arrow; S-051 shows "Week 28 – current week", "Date 27/09/2026 (automatic)", the 5 moods, a file input, Cancel / "Save diary entry"; POST with text + PNG → 303 to S-048 with "Diary entry saved" and the new text; POST empty → 422 with `data-error-for="text"`; Cancel goes back to S-048; there is no edit / delete control on an entry; the word "alert" is absent

### Implementation

- [X] T006 [US1] `app/mb360/tml/weeks.py` (R1 – R3) — makes T003 pass
- [X] T007 [P] [US2] `app/mb360/tml/diary.py` (R4) — makes T004 pass
- [X] T008 [US1] `app/mb360/tml/routes.py` + register in `main.py`; templates `timeline.html`, `diary_form.html`; Home week card → S-048 — makes T005 pass

## Phase 4: Polish

- [X] T009 Walk quickstart.md scenarios 1 – 6
- [ ] T010 [P] Build log entries

## Dependencies

Phase 1 → 2 → 3 → 4. T003 → T006; T004 → T007; T005 → T008.
