# Implementation Plan: ACC onboarding — open the sub-app, consent, guide, pregnancy setup

**Branch**: `sang/005-acc-onboarding` | **Date**: 2026-10-26 | **Spec**: [spec.md](spec.md) (snapshot of `specs/spec-ACC.md` v1.8.0)

**Input**: Feature specification from `specs/005-acc-onboarding/spec.md`

## Summary

Build ACC **US-1 (P1)** "Open the sub-app from the TCI app for the first time and agree to the use of information" and **US-2 (P1)** "Set up the pregnancy and reach the personalised home screen": a simulated TCI app home (S-001 state 1) opens the sub-app with a TCI identity; a non-female account gets the notice (BR-007); a first opening shows the consent sheet (S-001 state 2) — "Agree & continue" creates the User Account copy, Consent Record and Notification Preference (FR-011) and the session (FR-015); the onboarding guide S-104 follows once (FR-028); pregnancy setup S-007 / S-046 takes the due date or the LMP, optional height, weight and first visit date (FR-004, FR-005, D-72); then Home S-008 (FR-016, FR-017). A returning mother goes straight to S-008 (or to setup if she has no due date — BR-006). Same stack and project as `specs/001-alr-core/plan.md`.

## Technical Context

**Language/Version**: Python 3.11+ (uv) — unchanged · **Primary Dependencies**: unchanged · **Storage**: SQLite from schema + seed (unchanged) · **Testing**: pytest · **Target Platform**: local laptop · **Project Type**: web application (same project) · **Constraints**: data/ read-only; no password, OTP or registration (D-01); synthetic identities only · **Scale/Scope**: S-001 (2 states + notice), S-104, S-007 / S-046, S-008 (minimal)

## Constitution Check

| Principle | How this plan complies | Status |
|---|---|---|
| I. The spec is the source of truth | ACC US-1 #1 – #6, US-2 #1 – #6, FR-003 – FR-005, FR-011, FR-015 – FR-017, FR-028, BR-002 – BR-007; screen specs S-001, S-104, S-007, S-046, S-008. Open points are not invented: TCI identity mechanism (Q9), LMP → EDD rule (Q10), valid ranges (Q11), unticked-checkbox behaviour (Q14), guide pages (Q20), notice wording (Q21), terms versions (Q17) — see Complexity Tracking | PASS |
| II. Business rules are test-first | Tests for BR-004, BR-006, BR-007, FR-004 rules, FR-011 rows, FR-028 and every scenario of US-1 and US-2, written and seen failing first | PASS (enforced in tasks.md) |
| III. Thin vertical slices | Two P1 stories that form one entry flow | PASS |
| IV. Synthetic data and no secrets | The simulated TCI identities are typed by the tester or taken from the seed; no password, no token secret | PASS |
| V. Humans approve every change | Branch + pull request reviewed by a member who did not write it (Chi, ACC owner) | PASS |

## Project Structure

```text
specs/005-acc-onboarding/  spec.md, plan.md, research.md, data-model.md, quickstart.md, contracts/http-routes.md, tasks.md
app/mb360/acc/
├── __init__.py
├── entry.py       # FR-015 open the sub-app (BR-007 female only, BR-004 consent, BR-006 routing), FR-011 consent, session
├── setup.py       # FR-004, FR-005: validate and save the pregnancy setup (D-72)
└── routes.py      # contracts/http-routes.md
app/mb360/templates/  tci_home.html, consent.html, not_female.html, guide.html, setup.html, home.html
tests/unit/test_acc_entry.py, test_acc_setup.py
tests/integration/test_acc_onboarding_flow.py, test_acc_setup_page.py, test_acc_home_page.py
```

**Structure Decision**: new `acc` package; `/` (demo mother selector) stays for the other slices; the simulated TCI app lives at `/tci`.

## Complexity Tracking

| Item | Why it matters | What the plan does until it is answered |
|---|---|---|
| ACC §10 Q9 — how the TCI app passes the identity (token, format, lifetime) | FR-015 needs an identity and the session lifetime | `/tci` simulates the TCI app: the tester opens the sub-app as a seed TCI account or as a typed (invented) one; the identity is posted as plain form fields — a demo stand-in, not a security design. SESSION rows are written with a 12-hour lifetime, the lifetime of the ordinary seed sessions (7 of 10; the other 3 are edge cases) — provisional, Q9. Later pages keep the mother in the URL as in the other slices (sign-in: Session 11) |
| ACC §10 Q10 — LMP → EDD rule (Pending SME) | US-2 #2 | Team proposal used provisionally: EDD = LMP + 280 days (Naegele), the same 280-day rule as the seed; one function, flagged provisional |
| ACC §10 Q11 — valid ranges for height and weight (D-16) | FR-004 | Only "is a number" is checked; no range |
| ACC §10 Q14 — "Agree & continue" with the box unticked | US-1 #2 | The sheet comes back with an error at the checkbox; nothing is stored (the scenario states only "does not record consent and does not let her continue") |
| ACC §10 Q17 — terms versions | CONSENT_RECORD.`terms_version` | Left empty |
| ACC §10 Q20 — guide pages and text | S-104 | The 4 pages proposed in the S-104 screen spec (Health dashboard, Report a metric or symptom, Pregnancy timeline & diary, Health chatbot), placeholder text; the guide is shown only right after the first agreement, so nothing needs to be stored to "not show it again" |
| ACC §10 Q21 — notice wording for a non-female account | BR-007 | "Mother & Baby 360 is for expectant mothers." + "Back to TCI app"; wording to confirm |
| DM-41 default values of NOTIFICATION_PREFERENCE | FR-011 | The values the seed marks as "defaults written with the account (DM-41)": report responses on, new visit results on, appointment reminders on, Doctor's-instruction reminders off |
| DM-18 default — refresh of the TCI copy | FR-015 | Full name, phone, date of birth and medical record number are refreshed from the TCI identity at every opening |
| S-008 content of other modules | FR-016 | Home shows the greeting, the gestational week card and links to Doctor's instructions and My reports; self-tracked metrics (HLT), appointments (APT), notifications (S-009) and the timeline (S-048) are later slices |
| BR-003 (hospital due date has priority) and S-011 edit | US-3 (P2) | Out of scope; setup is only shown when there is no due date |
