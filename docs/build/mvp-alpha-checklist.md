# MVP Alpha Checklist

Course: DBIZ3 AI-native Product Development, Session 8 output (input to Session 9)
Team: `Group A`    Product: `Mother & Baby 360°`    Date: `27/10/2026`, updated `07/11/2026`
Commit checked: `5263a75` (`main` after PR #14) + this pull request (snapshot refresh of `specs/001-alr-core`, `env.example` rename); re-checked 07/11/2026 on `sang/mother-app-v1` (PR #20, v1.0.0 app, on top of the open PRs #15 – #19)    Tag: `mvp-alpha` — **not tagged yet**: G6 is still open, and #15 – #20 are not on `main` yet (section 2)

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

**v1.0.0 app (07/11/2026, PR #20, D-81 – D-85):** the same path runs as one mobile flow: `uv run python -m uvicorn mb360.server:app --app-dir app` (`docs/build/mother-app-v1.md`), or on the internet at `https://mother-baby-360.onrender.com` (D-82; the clinical web asks for the team password). Mother: TCI home → "Mẹ & Bé 360" → Terms → guide → setup → Home → "Báo cáo chỉ số" → 150/95 → S-028 → "Xem trạng thái". Staff: `/staff` → Phạm Thị Lan → **Overview** → "Above threshold, not viewed" → the case → S-064 → escalate; Trần Thu Hà → Case board → the case → Send guidance → Close case.

## 2. Gates

Tick only after checking it at the commit above. Every line must be ticked for `mvp-alpha`.

- [ ] G1. A fresh clone runs with the commands in each `quickstart.md`, on the laptops of at least two members (one macOS and one Windows, if the team has both). Names: `Sang (Windows 11 — fresh clones of 7938d71 (20/10), 2a880f1 (26/10) and 5263a75 (27/10/2026): uv sync, start_feature --use, generate_seed --check, python -m pytest, app started)`; `Tâm (macOS — fresh clone of sang/mother-app-v1, review of the v1.0.0 app, 06/11/2026: 416 passed; recorded in the team's review document, not on GitHub)`. **Still to do before the tag:** tick this box again on the merged `main` (one Windows and one macOS run), since #15 – #20 are not merged yet.
- [x] G2. The P1 user story of every core module works end to end on the seed data, following the demo path in section 1. ALR US-1 + US-2 and CLI US-1 + US-2 walked in the browser on Sang's laptop (20 – 21/10/2026: report → Metric alert → nurse escalates → doctor closes; My reports → S-026 with progress, Safety note, then the nurse's response); covered by `tests/integration/test_cli_loop.py`, `test_alr_notifications_flow.py` and the page tests. Recommended: a member other than the builder walks the path before the tag.
- [x] G3. Every business rule (BR) of the core modules, and every acceptance scenario of their P1 stories, has an automated test. All tests pass. Last line of the test run: `277 passed, 2 xfailed, 1 warning in 8.08s` (27/10/2026); `465 passed, 2 xfailed, 1 warning in 12.29s` on 07/11/2026 (v1.0.0 app, PR #20) (xfail = ALR §10 Q9 and HLT D-16, valid input ranges pending Client / SME — requirements not yet defined, not business rules). ALR BR-001 – BR-017 and CLI BR-001 – BR-009 each have a test (ALR BR-015 / BR-016 through the CLI tests; ALR BR-001 is a guard test); acceptance scenarios ALR US-1 #1 – #7, US-2 #1 – #3, CLI US-1 #1 – #9, US-2 #1 – #5 (and US-3 #1 – #2) are covered.
- [x] G4. `uv run tools/start_feature.py --check` prints OK for every feature folder (the spec snapshot matches `specs/spec-<MODULE>.md`). Checked 26/10/2026 after refreshing `specs/001-alr-core` (it had drifted when ALR §10 Q23 was added by `specs/003-alr-status`; the only change is that open question, which does not affect US-1): `001-alr-core` … `008-bot-chat` (8 feature folders) all OK on 27/10/2026, after refreshing `001-alr-core` again in this pull request. 07/11/2026: the 7 module specs were updated (Session 11 EARS lines, v1.0.0 differences); all 11 feature folders `001` … `011` refreshed and checked OK. Their plan.md and tasks.md were written for the older spec text; the changes are notes and answered questions, not new FRs.
- [x] G5. `/speckit-analyze` was run after `/speckit-tasks`, and every CRITICAL and HIGH finding is resolved or recorded in section 3. All eight features: 0 CRITICAL, 0 HIGH (build log entries 4, 9, 13, 16, 20, 23, 26, 29); the MEDIUM findings are in each plan.md Complexity Tracking and in section 3.
- [ ] G6. Every change reached `main` through a pull request reviewed by a member who did not write it. **Not met:** pull requests #4 – #7 and #9 – #14 reached `main` through a pull request, but each was merged by its author (PromotedKing) with **0 reviews** on GitHub. **To do:** Tâm (ALR: #6, #9, ALR part of #10; TML: #13), Trung (CLI: #7, #10), Hải Anh (seed: #5), Chi (PRD alignment: #4; ACC: #11; BOT: #14) and Ánh (HLT: #12) review the merged changes and leave an approving review or comments; this pull request (#8) is approved by a member other than Sang before merge. **07/11/2026:** #14 now has an approving review on GitHub. The review of the v1.0.0 app by Tâm, Ánh and Chi (06/11/2026) was written in a shared document, not on GitHub, so it does not count yet. **To do:** a member other than Sang approves #15 – #20 on GitHub (they are stacked: #15 → #16 → #17 → #18 → #19 → #20), then they are merged in that order.
- [x] G7. No real personal data and no secret (key, password, token) in any committed file. Checked 20/10, 26/10 and 27/10/2026 (25 PASS, 1 WARN W1 — the `.env.example` file added by #14 made T1 fail; renamed `env.example` in this pull request; it holds only setting names): `uv run tools/check_env.py --repo` → "no .env / key file committed: none tracked"; `git grep` for key / secret / password / token assignments → nothing; every person in the seed is invented (`data/data-model-MB360.md` §11). The Alpha needs no API key. 07/11/2026: the hosted app reads `GROQ_API_KEY`, `GEMINI_API_KEY` and `MB360_STAFF_PASSWORD` only from the platform's environment (`render.yaml` lists the names with `sync: false` or `generateValue`, never a value); BOT §5.3 E-3.
- [x] G8. `docs/build/build-log.md` has an entry for every agent run that changed code or tests. Entries 1 – 32 (ALR US-1: 1 – 6; CLI US-1/2: 7 – 11; start command: 12; ALR US-2: 13 – 15; CLI US-3: 16 – 18; snapshot refresh: 19; ACC: 20 – 22; HLT: 23 – 25; TML: 26 – 28; BOT: 29 – 31; checklist / rename: 32), then the dated entries of PRs #15 – #20 (v1.0.0 app, hosting, chatbot, Overview, this spec update).

## 3. Known limitations

List what the Alpha does not do yet, honestly. A limitation written here is not a penalty; a
limitation discovered by the instructor that is not written here is.

| # | Limitation | Spec reference | Planned for |
|---|---|---|---|
| 1 | "My reports" and the full S-026 are **done** (`specs/003-alr-status`, PR #9). Remaining: the Safety note text and the hotline number are placeholders | S-026 #18, #19; BOT §10 Q8 | When the hospital supplies them |
| 2 | **Done** (#17, v1.0.0 app): notification list S-009 with type filter and "Mark all as read", answer detail (Màn 10), settings S-010. Remaining: no visit-insert path calls FR-019 in the demo (visits come from the seed) | ACC FR-025 – FR-027; ALR §10 Q23 | — |
| 3 | No real sign-in. The mother opens the sub-app from a simulated TCI app; the sub-app now checks its session and "Close app" ends it (ACC §5.3). Staff are chosen on `/staff`; on the internet the clinical web is behind one shared team password (D-82, CLI §5.3) | ACC FR-015 (§10 Q9); CLI §10 Q11 | When the hospital answers Q9 / Q11 |
| 4 | No valid-range check on reported values (only format and type are checked) | ALR §10 Q9, D-16 (Pending SME) | When the Client / SME answers |
| 5 | Report code follows a provisional pattern (`BC-MMDD-NNN`) | ALR §10 Q16 | When the team decides |
| 6 | Blood-glucose and urine-protein thresholds are provisional values | ALR BR-004, D-15 (Pending SME) | When the SME confirms |
| 7 | Escalation is refused when the mother has no active responsible doctor; an assignment counts as active on its `valid_to` day | CLI §10 Q10, Q15 | When the team / Client decides |
| 8 | Metric history on S-064 is a table with the threshold, not a chart | CLI FR-008 | Session 10 (polish) |
| 9 | Doctor's instructions form is **done** (`specs/004-cli-instructions`, PR #10). Remaining: no "Remove instruction"; a new instruction is not attached to a visit | CLI FR-025; HLT §10 Q19 | When the team decides |
| 10 | The transcript of a chatbot case is ordered by the stored time (minute precision); a question and its reply in the same minute keep the storage order | BOT §6, D-78; build log issue #4 | When the BOT owner decides |
| 11 | A future "Measured at" is refused with a field error that ALR §5.1 does not state yet (it follows the HLT §6 constraint) | build log issue #3 | When Tâm updates ALR FR-014 |
| 12 | Built since the Alpha (#17 – #20): ACC US-3 profile, HLT US-3 / US-4, TML US-4, the v1.0.0 mobile flow and the clinical Overview / Case board (D-85). Not built: TML US-3 family messages (pending Client D-03); APT booking (Could — the next-appointment card reads a simulated TCI host table) | PRD M1, M2, M4, M5, C1; D-81, D-85 | When the Client answers D-03 |
| 14 | Chatbot: answers come from Groq's free plan on the hosted app (D-84), Gemini second (D-83), local sample answers without a key. Word lists are provisional (Pending SME). On an LLM failure the question stays in the field and nothing is stored (BOT §5.3 E-1), which differs from the DM-29 default. Free plans have daily limits | BOT §10 Q2, Q12, DM-29; D-83, D-84 | When the SME answers; before a real launch |
| 13 | `mb360.main:app` rebuilds the data from the seed at every start. The v1.0.0 app keeps a file database, but the free hosting plan has no lasting disk: the data goes back to the seed after a redeploy or a restart, and the app sleeps after 15 minutes without visits (the first page then takes about a minute) | `specs/001-alr-core/research.md` R2; `docs/build/adr-hosting.md` | When the team moves to a paid plan or a managed database |
| 15 | Screens are in Vietnamese (D-79); the sample mother of the v1.0.0 app has Vietnamese content, the rest of the seed (other mothers' notes, guidance templates, diary) is still English. Labels checked by Chi and Ánh on 06/11/2026; the labels added after that are proposed | D-79; `docs/ui-label-reference.md` | Seed text when the hospital supplies content (D-25) |
| 17 | "Export PDF album" opens a print-ready page and the browser saves it as PDF; the server generates no PDF file | TML FR-014; build log spec issue #7 | When the team decides |
| 18 | Chatbot answers are cut at 500 characters (last whole sentence), because the schema limits every CHAT_MESSAGE.text to 500 although DM-36 says answers have no limit | BOT §5.3 E-2, §7.3; DM-36 | When Tâm settles DM-36 |
| 19 | The Overview and the Case board have no Screen ID and no screen spec yet; they only count and group existing cases (no new threshold, no time limit) | CLI §7.3; D-85 | When Chi adds the screens and Trung accepts D-85 |
| 16 | No booking in the sub-app (D-80). The next-appointment card and the due-date prefill read a simulated TCI host table; the real TCI interface is not known. APT navigation documentation is aligned by D-86 (11/11/2026): no Appointments tab or Home booking CTA; the real TCI integration remains unconfirmed | D-80; spec-APT §7.3; `screens/ui-final/README.md` U2 | When the APT owner and the hospital decide |

## 4. Sign-off

| Member | Role in this Alpha | Agrees the gates are met (yes / no, and why) |
|---|---|---|
| Sang | Builder of the eleven slices and the v1.0.0 app (agent runs, build log); BOT spec owner | No — G6 is open and #15 – #20 are not merged (section 2) |
| Tâm | ALR spec owner; reviewer of ALR changes (#6, #9) | *pending* |
| Trung | CLI spec owner; reviewer of CLI changes (#7, #10) | *pending* |
| Hải Anh | Seed owner; reviewer of the seed fix (#5); second laptop for G1 | *pending* |
| Chi | ACC spec owner; reviewer of the PRD alignment (#4) | *pending* |
| Ánh | Screens owner; walks the demo path against the screen specs (G2) | *pending* |
