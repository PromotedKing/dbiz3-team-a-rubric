# Implementation Plan: HLT history — Doctor's instructions and metric history

**Branch**: `sang/010-hlt-history` (based on `sang/009-acc-profile`) | **Date**: 2026-11-02 | **Spec**: [spec.md](spec.md) (snapshot of `specs/spec-HLT.md`)

**Input**: Feature specification from `specs/010-hlt-history/spec.md`; look from `screens/ui-final` (Màn 18, 23) as D-80 limits it.

## Summary

Build HLT **US-3 (P2)** "View Doctor's instructions" (S-027 cards: latest report, threshold label, doctor, date, history link) and **US-4 (P2)** "View a metric's history over time" (S-025: metric, From – To, chart, Average / Lowest / Highest, measurements; FR-009 – FR-012). Read-only; no new table or column. Thresholds and the fetal heart rate range come only from THRESHOLD_RULE.

## Technical Context

**Language/Version**: Python 3.11+ (uv) — unchanged · **Primary Dependencies**: unchanged; the chart is inline SVG computed on the server · **Storage**: SQLite from schema + seed (unchanged) · **Testing**: pytest · **Target**: FastAPI + Jinja2 pages, phone width

## Constitution Check

| Principle | How this plan complies | Status |
|---|---|---|
| I. The spec is the source of truth | HLT US-3 #1 – #3, US-4 #1 – #4, FR-009 – FR-012, BR-001, BR-003 – BR-005; S-025, S-027. Open points stay open (table below) | PASS |
| II. Business rules are test-first | Tests for BR-003, BR-004, BR-005, FR-010 – FR-012 and the threshold lines written and seen failing first | PASS |
| III. Thin vertical slices | Two read-only stories on existing records | PASS |
| IV. Synthetic data and no secrets | Seed data only | PASS |
| V. Humans approve every change | Branch + pull request reviewed by a member who did not write it (Hải Anh reviews HLT) | PASS |

## Project Structure

```text
specs/010-hlt-history/  spec.md, plan.md, research.md, data-model.md, quickstart.md, contracts/http-routes.md, tasks.md
app/mb360/hlt/history.py   # FR-009 – FR-012: rows, statistics, chart geometry; S-027 cards
app/mb360/hlt/routes.py    # GET /m/{id}/history
app/mb360/main.py          # S-027 route passes the cards
app/mb360/templates/       history.html, instructions.html; links on health.html, home.html
tests/unit/test_hlt_history.py
tests/integration/test_hlt_history_page.py
```

## Complexity Tracking

| Item | Why it matters | What the plan does until it is answered |
|---|---|---|
| HLT Q12 — statistics for urine protein and sleep | FR-011 | No Average / Lowest / Highest for these two; the list and chart still show (nothing invented). Chart: urine protein by its dipstick scale, sleep in hours |
| HLT Q12, FR-010 — default time range | No rule in the spec | Last 30 days up to today |
| S-025 SR-006 — blood pressure statistics | Separately or per measurement | Systolic and diastolic separately (`spec-HLT` §5.1 FR-011), all sources combined |
| S-025 — invalid range wording | §4 Error | "From" after "To": field error, no data shown |
| Blood glucose threshold line | FR-012 follows the selected context | A context selector (All by default); the line appears only for one context; each row is labelled by its own context |
| S-025 §5 #3 — tapping a measurement | Not drawn | Rows are not links |
| S-025 ✕ and tab bar | D-80 | ← only, as the UI package |
| U15 of `screens/ui-final/README.md` | Package makes S-027 read-only | The report buttons stay (HLT US-3 #1) |
