# Implementation Plan: TML journey — review by stage and keepsake album

**Branch**: `sang/011-tml-journey` (based on `sang/010-hlt-history`) | **Date**: 2026-11-02 | **Spec**: [spec.md](spec.md) (snapshot of `specs/spec-TML.md`)

**Input**: Feature specification from `specs/011-tml-journey/spec.md`; look from `screens/ui-final` (Màn 20) as D-80 limits it.

## Summary

Build TML **US-4 (P2)** "Review my journey and export a keepsake album": S-105 with the stages of D-75, week by week the visits with ultrasound images, the diary entries with photos and the Messages to Baby (FR-013), and a print-ready album page (FR-014, BR-007). Read-only; nothing is stored.

## Technical Context

**Language/Version**: Python 3.11+ (uv) — unchanged · **Primary Dependencies**: unchanged · **Storage**: SQLite from schema + seed (unchanged) · **Testing**: pytest · **Target**: FastAPI + Jinja2 pages, phone width

## Constitution Check

| Principle | How this plan complies | Status |
|---|---|---|
| I. The spec is the source of truth | TML US-4 #1 – #4, FR-013, FR-014, BR-001, BR-003, BR-006, BR-007; S-105. Open points stay open (table below); the one deviation on FR-014 is stated | PASS with a stated limit |
| II. Business rules are test-first | Tests for BR-001, BR-007, FR-013 and the stage rules written and seen failing first | PASS |
| III. Thin vertical slices | One story on existing records | PASS |
| IV. Synthetic data and no secrets | Seed data only | PASS |
| V. Humans approve every change | Branch + pull request reviewed by a member who did not write it (Ánh reviews TML) | PASS |

## Project Structure

```text
specs/011-tml-journey/  spec.md, plan.md, research.md, data-model.md, quickstart.md, contracts/http-routes.md, tasks.md
app/mb360/tml/journey.py   # FR-013: stages and week blocks
app/mb360/tml/routes.py    # GET /m/{id}/journey, /m/{id}/journey/album
app/mb360/templates/       journey.html, album.html; links on timeline.html, profile.html
tests/unit/test_tml_journey.py
tests/integration/test_tml_journey_pages.py
```

## Complexity Tracking

| Item | Why it matters | What the plan does until it is answered |
|---|---|---|
| **FR-014 — a PDF file** | Vietnamese text in a generated PDF needs a new library and an embedded font; `AGENTS.md` adds no dependency without the team | **Limit:** "Export PDF album" opens a print-ready page and the browser's print sheet, where the mother saves it as PDF. Nothing is generated or stored on the server (BR-007). A real `application/pdf` response is left for the team to decide |
| TML Q16 — trimester boundaries | FR-013 | Weeks 0 – 13 / 14 – 27 / 28 – 42 (D-75), not the 1 – 13 / 28 – 40 of the UI package (U12) |
| TML Q18 — album content | FR-014 | Visit date, ultrasound image, measurements with their report date (BR-003), doctor's note; diary with mood and photos; Messages to Baby. Wording when empty: "Nothing to export yet." |
| Messages to Baby `[PENDING CLIENT: D-03]` | FR-013 includes them | Shown when the seed has them; none can be written (US-3) |
| Photos not on disk | Seed rows name files that are not in the repository | A captioned placeholder, as on S-048 |
| S-105 entry | Spec: S-048; package: Profile | Both |
