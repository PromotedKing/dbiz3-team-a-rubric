# MVP Alpha Checklist

Course: DBIZ3 AI-native Product Development, Session 8 output (input to Session 9)
Team: `Group A`    Product: `Mother & Baby 360°`    Date: `20/10/2026`
Commit checked: `7938d71`    Tag: `mvp-alpha` — **not tagged yet**: G1, G2, G3 and G6 are still open (section 2)

Save as `docs/build/mvp-alpha-checklist.md`. "MVP Alpha" in DBIZ3 means: the core modules of
the product run end to end on the Session 5 seed data, for their highest-priority user story,
from a clean clone, with the business rules covered by passing tests. It is a course definition.
It is not a market release, and it does not need login, deployment or a polished interface.

## 1. Core modules in this Alpha

The core modules are the ones on the main path of your MVP Scope v3 (Session 1): without them the
product cannot be demonstrated at all. Usually one or two modules.

Main path (PRD M3 "Risk Feedback & Health Alerts", completed by S1 / S2): the mother reports a flagged metric or a symptom → the system checks the threshold and opens a case → the nurse triages → the doctor closes escalated cases. Core modules: **ALR** and **CLI** (`docs/build/agent-prompts.md` §0).

| Module | P1 user story (from the spec) | Feature folder | Owner | Demo path (URLs or screens, in order) |
|---|---|---|---|---|
| ALR | US-1 Submit a metric or symptom report (`specs/spec-ALR.md` §3). *US-2 "View the status of my reports" is also P1 and is not built yet — see G2 and limitation 1* | `specs/001-alr-core` | Sang (build); Tâm (spec owner) | `http://127.0.0.1:8000/` → choose **Ngô Thị Thảo** → S-027 "Doctor's instructions" → "+ Report metric" (S-025A) → 150/95, "No symptoms" → **S-028 Metric alert** → Close → report 120/80 with "Palpitations" → **S-026** "Not viewed" → report 120/80 "No symptoms" → back to S-027 "Report submitted" |
| CLI | US-1 Nurse works through the case queue; US-2 Doctor handles an escalated case (both P1, `specs/spec-CLI.md` §3) | `specs/002-cli-core` | Sang (build); Trung (spec owner) | `http://127.0.0.1:8000/staff` → nurse **Trần Thị B** → S-061 "Cases to handle" (All, Newest) → "Not viewed" → Ngô Thị Thảo's case → S-064 → Mark as viewed → Escalate to doctor → `/staff` → **Dr. Phạm Quốc Dũng** → S-061 (default "Escalated to doctor") → S-064 → Send guidance → Close case (Resolved) |

Start the app: `uv run python -m uvicorn mb360.main:app --app-dir app --reload` (`AGENTS.md` §4).

## 2. Gates

Tick only after checking it at the commit above. Every line must be ticked for `mvp-alpha`.

- [ ] G1. A fresh clone runs with the commands in each `quickstart.md`, on the laptops of at least two members (one macOS and one Windows, if the team has both). Names: `Sang (Windows 11, 20/10/2026 — fresh clone of 7938d71: uv sync, start_feature --use, generate_seed --check, pytest, app started; /staff answers 200)`. **Open:** a second member, on macOS if the team has one, must run both quickstart.md files.
- [ ] G2. The P1 user story of every core module works end to end on the seed data, following the demo path in section 1. **Met for ALR US-1 and CLI US-1 + US-2** (app running on Sang's laptop; the whole path is also covered by `tests/integration/test_cli_loop.py` and the ALR integration tests). **Open:** ALR US-2 is also P1 ("My reports" S-029, full S-026) and is not built; a member other than the builder should walk the demo path.
- [ ] G3. Every business rule (BR) of the core modules, and every acceptance scenario of their P1 stories, has an automated test. All tests pass. Last line of the test run: `110 passed, 1 xfailed, 1 warning in 4.18s` (xfail = ALR §10 Q9, valid ranges, pending Client / SME). **Met for the slices built** (ALR US-1: BR-002, BR-004 – BR-010, BR-013, BR-014, BR-017; CLI US-1 / US-2: BR-001 – BR-005, BR-007 – BR-009, with ALR BR-015 / BR-016). **Open:** no test yet for ALR BR-001 (instructions never removed automatically), BR-003 (visit-result notification), BR-011 (Safety note), BR-012 (S-026 progress), the acceptance scenarios of ALR US-2, and CLI BR-006 (above-threshold guidance written with the instruction — US-3, P2).
- [x] G4. `uv run tools/start_feature.py --check` prints OK for every feature folder (the spec snapshot matches `specs/spec-<MODULE>.md`). Checked 20/10/2026: `specs/001-alr-core` OK, `specs/002-cli-core` OK.
- [x] G5. `/speckit-analyze` was run after `/speckit-tasks`, and every CRITICAL and HIGH finding is resolved or recorded in section 3. Both features: 0 CRITICAL, 0 HIGH (build log entries 4 and 9); the MEDIUM findings are in each plan.md Complexity Tracking and in section 3.
- [ ] G6. Every change reached `main` through a pull request reviewed by a member who did not write it. **Not met:** pull requests #4 – #7 reached `main` through a pull request, but each was merged by its author (PromotedKing) with **0 reviews** on GitHub. **To do:** Tâm (ALR, #6), Trung (CLI, #7), Hải Anh (seed, #5) and Chi (PRD alignment, #4) review the merged changes and leave an approving review or comments; from now on a member other than the author approves before merge.
- [x] G7. No real personal data and no secret (key, password, token) in any committed file. Checked 20/10/2026: `uv run tools/check_env.py --repo` → "no .env / key file committed: none tracked"; `git grep` for key / secret / password / token assignments → nothing; every person in the seed is invented (`data/data-model-MB360.md` §11). The Alpha needs no API key.
- [x] G8. `docs/build/build-log.md` has an entry for every agent run that changed code or tests. Entries 1 – 12 (ALR: 1 – 6, CLI: 7 – 11, start command fix: 12).

## 3. Known limitations

List what the Alpha does not do yet, honestly. A limitation written here is not a penalty; a
limitation discovered by the instructor that is not written here is.

| # | Limitation | Spec reference | Planned for |
|---|---|---|---|
| 1 | "My reports" list (S-029) and the full report status page S-026 (progress steps, Safety note, responses) are not built; S-026 shows report details and the status only | ALR US-2 (P1), FR-001 – FR-003, FR-005, BR-009, BR-011, BR-012 | Session 9 |
| 2 | No notification to the mother when her case changes status or receives a response; no notification list S-009 | ALR FR-018, CLI FR-005, ACC FR-025 – FR-027 | Session 9 (with limitation 1) |
| 3 | No sign-in: the mother and the staff member are chosen on demo pages (`/`, `/staff`) | ACC FR-015 (TCI identity, §10 Q9); CLI §10 Q11 | Session 11 |
| 4 | No valid-range check on reported values (only format and type are checked) | ALR §10 Q9, D-16 (Pending SME) | When the Client / SME answers |
| 5 | Report code follows a provisional pattern (`BC-MMDD-NNN`) | ALR §10 Q16 | When the team decides |
| 6 | Blood-glucose and urine-protein thresholds are provisional values | ALR BR-004, D-15 (Pending SME) | When the SME confirms |
| 7 | Escalation is refused when the mother has no active responsible doctor; an assignment counts as active on its `valid_to` day | CLI §10 Q10, Q15 | When the team / Client decides |
| 8 | Metric history on S-064 is a table with the threshold, not a chart | CLI FR-008 | Session 10 (polish) |
| 9 | Doctor's instructions cannot be added or edited (view only) | CLI US-3, FR-025 (P2) | Session 9 or 10 |
| 10 | The transcript of a chatbot case is ordered by the stored time (minute precision); a question and its reply in the same minute keep the storage order | BOT §6, D-78; build log issue #4 | When the BOT owner decides |
| 11 | A future "Measured at" is refused with a field error that ALR §5.1 does not state yet (it follows the HLT §6 constraint) | build log issue #3 | When Tâm updates ALR FR-014 |
| 12 | Other Must modules are not built: ACC onboarding / profile, HLT dashboard, TML timeline and diary, BOT chatbot | PRD M1, M2, M4, M5 | Sessions 9 – 11 |
| 13 | Data is rebuilt from the seed every time the app starts; reports made in the demo are lost on restart | `specs/001-alr-core/research.md` R2 | Session 11 (deployment) |

## 4. Sign-off

| Member | Role in this Alpha | Agrees the gates are met (yes / no, and why) |
|---|---|---|
| Sang | Builder of both slices (agent runs, build log); BOT spec owner | No — G1, G2, G3 and G6 are open (section 2) |
| Tâm | ALR spec owner; reviewer of ALR changes (#6) | *pending* |
| Trung | CLI spec owner; reviewer of CLI changes (#7) | *pending* |
| Hải Anh | Seed owner; reviewer of the seed fix (#5); second laptop for G1 | *pending* |
| Chi | ACC spec owner; reviewer of the PRD alignment (#4) | *pending* |
| Ánh | Screens owner; walks the demo path against the screen specs (G2) | *pending* |
