# MVP Alpha Checklist

Course: DBIZ3 AI-native Product Development, Session 8 output (input to Session 9)
Team: `Group A`    Product: `Mother & Baby 360°`    Date: `27/10/2026`
Commit checked: `5263a75` (`main` after PR #14) + this pull request (snapshot refresh of `specs/001-alr-core`, `env.example` rename)    Tag: `mvp-alpha` — **not tagged yet**: G1 and G6 are still open (section 2)

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
| ALR | US-1 Submit a metric or symptom report; US-2 View the status of my reports (both P1, `specs/spec-ALR.md` §3) | `specs/001-alr-core`, `specs/003-alr-status` | Sang (build); Tâm (spec owner) | `http://127.0.0.1:8000/` → choose **Ngô Thị Thảo** → S-027 "Doctor's instructions" → "+ Report metric" (S-025A) → 150/95, "No symptoms" → **S-028 Metric alert** → Close → report 120/80 with "Palpitations" → **S-026** "Not viewed" → report 120/80 "No symptoms" → back to S-027 "Report submitted" → "My reports" (**S-029**) → open a report → **S-026** progress, response or Safety note |
| CLI | US-1 Nurse works through the case queue; US-2 Doctor handles an escalated case (both P1, `specs/spec-CLI.md` §3); also US-3 (P2) Doctor's instructions | `specs/002-cli-core`, `specs/004-cli-instructions` | Sang (build); Trung (spec owner) | `http://127.0.0.1:8000/staff` → nurse **Trần Thị B** → S-061 "Cases to handle" (All, Newest) → "Not viewed" → Ngô Thị Thảo's case → S-064 → Mark as viewed → Escalate to doctor → `/staff` → **Dr. Phạm Quốc Dũng** → S-061 (default "Escalated to doctor") → S-064 → Send guidance → Close case (Resolved) |

Start the app: `uv run python -m uvicorn mb360.main:app --app-dir app --reload` (`AGENTS.md` §4).

## 2. Gates

Tick only after checking it at the commit above. Every line must be ticked for `mvp-alpha`.

- [ ] G1. A fresh clone runs with the commands in each `quickstart.md`, on the laptops of at least two members (one macOS and one Windows, if the team has both). Names: `Sang (Windows 11 — fresh clones of 7938d71 (20/10), 2a880f1 (26/10) and 5263a75 (27/10/2026): uv sync, start_feature --use, generate_seed --check, python -m pytest, app started)`. **Open:** a second member, on macOS if the team has one, must run both quickstart.md files.
- [x] G2. The P1 user story of every core module works end to end on the seed data, following the demo path in section 1. ALR US-1 + US-2 and CLI US-1 + US-2 walked in the browser on Sang's laptop (20 – 21/10/2026: report → Metric alert → nurse escalates → doctor closes; My reports → S-026 with progress, Safety note, then the nurse's response); covered by `tests/integration/test_cli_loop.py`, `test_alr_notifications_flow.py` and the page tests. Recommended: a member other than the builder walks the path before the tag.
- [x] G3. Every business rule (BR) of the core modules, and every acceptance scenario of their P1 stories, has an automated test. All tests pass. Last line of the test run: `277 passed, 2 xfailed, 1 warning in 8.08s` (xfail = ALR §10 Q9 and HLT D-16, valid input ranges pending Client / SME — requirements not yet defined, not business rules). ALR BR-001 – BR-017 and CLI BR-001 – BR-009 each have a test (ALR BR-015 / BR-016 through the CLI tests; ALR BR-001 is a guard test); acceptance scenarios ALR US-1 #1 – #7, US-2 #1 – #3, CLI US-1 #1 – #9, US-2 #1 – #5 (and US-3 #1 – #2) are covered.
- [x] G4. `uv run tools/start_feature.py --check` prints OK for every feature folder (the spec snapshot matches `specs/spec-<MODULE>.md`). Checked 26/10/2026 after refreshing `specs/001-alr-core` (it had drifted when ALR §10 Q23 was added by `specs/003-alr-status`; the only change is that open question, which does not affect US-1): `001-alr-core` … `008-bot-chat` (8 feature folders) all OK on 27/10/2026, after refreshing `001-alr-core` again in this pull request.
- [x] G5. `/speckit-analyze` was run after `/speckit-tasks`, and every CRITICAL and HIGH finding is resolved or recorded in section 3. All eight features: 0 CRITICAL, 0 HIGH (build log entries 4, 9, 13, 16, 20, 23, 26, 29); the MEDIUM findings are in each plan.md Complexity Tracking and in section 3.
- [ ] G6. Every change reached `main` through a pull request reviewed by a member who did not write it. **Not met:** pull requests #4 – #7 and #9 – #14 reached `main` through a pull request, but each was merged by its author (PromotedKing) with **0 reviews** on GitHub. **To do:** Tâm (ALR: #6, #9, ALR part of #10; TML: #13), Trung (CLI: #7, #10), Hải Anh (seed: #5), Chi (PRD alignment: #4; ACC: #11; BOT: #14) and Ánh (HLT: #12) review the merged changes and leave an approving review or comments; this pull request (#8) is approved by a member other than Sang before merge.
- [x] G7. No real personal data and no secret (key, password, token) in any committed file. Checked 20/10, 26/10 and 27/10/2026 (25 PASS, 1 WARN W1 — the `.env.example` file added by #14 made T1 fail; renamed `env.example` in this pull request; it holds only setting names): `uv run tools/check_env.py --repo` → "no .env / key file committed: none tracked"; `git grep` for key / secret / password / token assignments → nothing; every person in the seed is invented (`data/data-model-MB360.md` §11). The Alpha needs no API key.
- [x] G8. `docs/build/build-log.md` has an entry for every agent run that changed code or tests. Entries 1 – 32 (ALR US-1: 1 – 6; CLI US-1/2: 7 – 11; start command: 12; ALR US-2: 13 – 15; CLI US-3: 16 – 18; snapshot refresh: 19; ACC: 20 – 22; HLT: 23 – 25; TML: 26 – 28; BOT: 29 – 31; checklist / rename: 32).

## 3. Known limitations

List what the Alpha does not do yet, honestly. A limitation written here is not a penalty; a
limitation discovered by the instructor that is not written here is.

| # | Limitation | Spec reference | Planned for |
|---|---|---|---|
| 1 | "My reports" and the full S-026 are **done** (`specs/003-alr-status`, PR #9). Remaining: the Safety note text and the hotline number are placeholders | S-026 #18, #19; BOT §10 Q8 | When the hospital supplies them |
| 2 | Notifications are created (ALR FR-018, FR-019) but the mother cannot see them: no notification list S-009, no settings page S-010; no visit-insert path calls FR-019 (D-59) | ACC FR-025 – FR-027; ALR §10 Q23 (wording) | Session 9 (with ACC) |
| 3 | No real sign-in: the mother opens the sub-app from a simulated TCI app (`/tci`, ACC slice) or a demo page (`/`); staff are chosen on `/staff` | ACC FR-015 (TCI identity, §10 Q9); CLI §10 Q11 | Session 11 |
| 4 | No valid-range check on reported values (only format and type are checked) | ALR §10 Q9, D-16 (Pending SME) | When the Client / SME answers |
| 5 | Report code follows a provisional pattern (`BC-MMDD-NNN`) | ALR §10 Q16 | When the team decides |
| 6 | Blood-glucose and urine-protein thresholds are provisional values | ALR BR-004, D-15 (Pending SME) | When the SME confirms |
| 7 | Escalation is refused when the mother has no active responsible doctor; an assignment counts as active on its `valid_to` day | CLI §10 Q10, Q15 | When the team / Client decides |
| 8 | Metric history on S-064 is a table with the threshold, not a chart | CLI FR-008 | Session 10 (polish) |
| 9 | Doctor's instructions form is **done** (`specs/004-cli-instructions`, PR #10). Remaining: no "Remove instruction"; a new instruction is not attached to a visit | CLI FR-025; HLT §10 Q19 | When the team decides |
| 10 | The transcript of a chatbot case is ordered by the stored time (minute precision); a question and its reply in the same minute keep the storage order | BOT §6, D-78; build log issue #4 | When the BOT owner decides |
| 11 | A future "Measured at" is refused with a field error that ALR §5.1 does not state yet (it follows the HLT §6 constraint) | build log issue #3 | When Tâm updates ALR FR-014 |
| 12 | The other Must modules now have their P1 stories (ACC #11, HLT #12, TML #13, BOT #14). Not built yet: ACC US-3 profile, HLT US-3 / US-4, TML US-3 (pending Client D-03) and US-4 (journey review, PDF album), APT (Could) | PRD M1, M2, M4, M5, C1 | Sessions 9 – 11 |
| 14 | Chatbot: the real Gemini call is not tested (no key; fake LLM by default); danger phrases, personal-health markers and topic words are provisional; on an LLM failure the question is not kept (differs from the DM-29 default) | BOT §10 Q2, Q12, Q14; D-47; DM-29 | When a member adds a key; when the SME answers |
| 13 | Data is rebuilt from the seed every time the app starts; reports made in the demo are lost on restart | `specs/001-alr-core/research.md` R2 | Session 11 (deployment) |
| 15 | Screens are in Vietnamese (D-79) but free text from the seed (doctor's notes, guidance templates, diary, chat) is English, and 213 added labels are proposed, not yet reviewed | D-79; `docs/ui-label-reference.md` | When Chi and Ánh review the labels; seed text when the hospital supplies content (D-25) |
| 16 | Profile tab shows only the name, record number and week (S-103 menu, S-010, S-011 are ACC US-3); Appointments tab opens a stand-in page for the TCI booking flow; no notification list (S-009) | D-79; spec-ACC US-3; spec-APT BR-003 | Sessions 9 – 10 |

## 4. Sign-off

| Member | Role in this Alpha | Agrees the gates are met (yes / no, and why) |
|---|---|---|
| Sang | Builder of the eight slices (agent runs, build log); BOT spec owner | No — G1 and G6 are open (section 2) |
| Tâm | ALR spec owner; reviewer of ALR changes (#6, #9) | *pending* |
| Trung | CLI spec owner; reviewer of CLI changes (#7, #10) | *pending* |
| Hải Anh | Seed owner; reviewer of the seed fix (#5); second laptop for G1 | *pending* |
| Chi | ACC spec owner; reviewer of the PRD alignment (#4) | *pending* |
| Ánh | Screens owner; walks the demo path against the screen specs (G2) | *pending* |
