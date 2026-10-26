# Build Log

Course: DBIZ3 AI-native Product Development, Sessions 8 to 11
Team: `Group A`    Product: `Mother & Baby 360°`

Save as `docs/build/build-log.md`. Add one entry for every agent run that created or changed a
file in `specs/`, `src/` (or your code folder) or `tests/`. Write it right after the run, not at
the end of the day. The build log is how the instructors, and your teammates, see what the agent
did and what the humans decided.

## 1. Features in progress

| Feature folder | Module | User stories in this slice | Owner | Branch | Status |
|---|---|---|---|---|---|
| `specs/001-alr-core` | ALR | US-1 (P1) — submit a metric or symptom report (US-2 if time allows) | Sang | `sang/001-alr-core` | Merged (PR #6) |
| `specs/002-cli-core` | CLI | US-1 (P1) nurse queue + US-2 (P1) doctor handles escalated case | Sang | `sang/002-cli-core` | Merged (PR #7) |
| `specs/003-alr-status` | ALR | US-2 (P1) My reports + report status; FR-018 notifications | Sang | `sang/003-alr-status` | In review — 143 passed, 1 xfailed |
| `specs/004-cli-instructions` | CLI (+ ALR FR-019) | US-3 (P2) Doctor's instructions form; ALR BR-001, BR-003 / FR-019 | Sang | `sang/004-cli-instructions` | In review — 159 passed, 1 xfailed |
| `specs/005-acc-onboarding` | ACC | US-1 (P1) open the sub-app + consent + guide; US-2 (P1) pregnancy setup + Home | Sang | `sang/005-acc-onboarding` | In review — 198 passed, 1 xfailed |
| `specs/006-hlt-dashboard` | HLT | US-1 (P1) Health metrics S-023; US-2 (P1) self-tracked metrics S-024 | Sang | `sang/006-hlt-dashboard` | In review — 220 passed, 2 xfailed |
| `specs/007-tml-timeline` | TML | US-1 (P1) week view S-048 (+ daily indicators D-75); US-2 (P1) diary S-051 / S-052 | Sang | `sang/007-tml-timeline` | In review — 246 passed, 2 xfailed |
| `specs/008-bot-chat` | BOT | US-1 (P1) ask a question; US-2 (P1) hand-off to a nurse (fake LLM by default, D-76) | Sang | `sang/008-bot-chat` | Building — tests written (T001 – T006) |

## 2. Run entries

Copy this block for each run. Keep the newest entry at the bottom.

### Entry 1: 14/10 Sang

| Field | Value |
|---|---|
| Path and agent | A (Claude Code, claude-opus-5-5) |
| Command and argument | `uv run tools/start_feature.py --spec specs/spec-ALR.md ALR --name core`, then the Step 1 consistency check of `docs/build/agent-prompts.md` §1 (read-only) |
| Feature and tasks | `specs/001-alr-core` (no tasks yet) |
| What the agent produced | `specs/001-alr-core/spec.md` (snapshot of `specs/spec-ALR.md` v1.8.0); `.specify/feature.json` (local, not committed); consistency table: every stored field of ALR §5.1 maps to `data/data-model-MB360.md` §6 (METRIC_REPORT, REPORT_SYMPTOM, HEALTH_METRIC_RECORD, CARE_CASE, CASE_STATUS_HISTORY, STAFF_RESPONSE, WATCH_FLAG, NOTIFICATION) — 0 NOT FOUND |
| Human review | Pending — Sang to confirm the table |
| Tests | none yet |
| Spec issues found | Seed row RPT-006 (`BC-0927-020`, U09) breaks ALR BR-006: blood pressure reported with no `watch_flag_id`, U09 has no Doctor's instruction, and the Health Metric Record source is "Self-entered" instead of "Doctor-assigned" (§5.1). Issue #1 below |
| Commit | (not committed yet) |

### Entry `<n>`: `<dd/mm>` `<member>`

| Field | Value |
|---|---|
| Path and agent | A (Claude Code) / B (Antigravity agent, model `<name>`) |
| Command and argument | `/speckit-plan ...` (paste the argument you typed) |
| Feature and tasks | `specs/001-...`, tasks `T0xx` to `T0yy` |
| What the agent produced | files created or changed, one line each |
| Human review | Accepted / Changed / Rejected. What you changed and why |
| Tests | `<passed> passed, <failed> failed` (paste the last line of the test run) |
| Spec issues found | none / open question `<n>` added to `specs/spec-<MODULE>.md` §10 |
| Commit | `<first 7 characters of the hash>` |

### Entry 2: 14/10 Sang

| Field | Value |
|---|---|
| Path and agent | A (Claude Code, claude-opus-5-5) |
| Command and argument | `/speckit-plan` with the argument of `docs/build/agent-prompts.md` §2: stack Python 3.11 + FastAPI + SQLite + pytest; scope US-1 (P1) only; data/ read-only; thresholds from THRESHOLD_RULE; login and deployment out of scope; ALR Q9 → Complexity Tracking (team decision 14/10) |
| Feature and tasks | `specs/001-alr-core` (no tasks yet) |
| What the agent produced | `plan.md` (technical context, constitution check, structure, complexity tracking); `research.md` (R1 – R8); `data-model.md` (tables read / written, points to `data/data-model-MB360.md`); `contracts/http-routes.md`; `quickstart.md` |
| Human review | Pending — the 8 questions of Workshop Guide 2.2 |
| Tests | none yet |
| Spec issues found | none new: the interpretations in research.md map to existing open questions (ALR Q9, Q14, Q16; ACC Q9, Q10) |
| Commit | (not committed yet) |

### Entry 3: 14/10 Sang

| Field | Value |
|---|---|
| Path and agent | A (Claude Code, claude-opus-5-5) |
| Command and argument | `/speckit-tasks` with the argument of `docs/build/agent-prompts.md` §3 (test task before each code task; seed test: 272 rows, RPT-006 opens C6; out-of-scope stories excluded) |
| Feature and tasks | `specs/001-alr-core`, T001 – T028 |
| What the agent produced | `tasks.md`: Setup T001 – T003; Foundational T004 – T008 (seed and clock tests first); US-1 tests T009 – T018, code T019 – T026; Polish T027 – T028 |
| Human review | Accepted by Sang (14/10). Changed: T010 no longer checks "measured time not in the future" — the agent added a rule the spec does not state |
| Tests | none yet |
| Spec issues found | none |
| Commit | see the commit of this entry |

### Entry 4: 14/10 Sang

| Field | Value |
|---|---|
| Path and agent | A (Claude Code, claude-opus-5-5) |
| Command and argument | `/speckit-analyze` (no argument, read-only) |
| Feature and tasks | `specs/001-alr-core`, T001 – T028 |
| What the agent produced | Analysis report (not a file): 0 CRITICAL, 0 HIGH, 4 MEDIUM, 2 LOW; coverage of the slice's FRs (FR-007, FR-010 – FR-015, FR-020, FR-021) and BRs (BR-002, BR-004 – BR-010, BR-013, BR-014, BR-017) = 100 % |
| Human review | MEDIUM items accepted as recorded in plan.md Complexity Tracking (ALR Q9, Q16) or left for the US-2 slice (seed N09, FR-018) |
| Tests | none yet |
| Spec issues found | none new |
| Commit | see the commit of this entry |

### Entry 5: 14/10 Sang

| Field | Value |
|---|---|
| Path and agent | A (Claude Code, claude-opus-5-5) |
| Command and argument | `/speckit-implement Only the Setup and Foundational phases and the test tasks of the US-1 phase (T001 to T018). Do not write any code that makes those tests pass. Run the tests at the end and show me the output.` |
| Feature and tasks | `specs/001-alr-core`, T001 – T018 |
| What the agent produced | `pyproject.toml` (uv; fastapi, jinja2, python-multipart, uvicorn; dev: pytest, httpx) and `uv.lock`; `.gitignore` + `.pytest_cache/`; `app/mb360/db.py` (schema + seed loader), `app/mb360/clock.py`; `tests/conftest.py`; tests: `tests/seed/test_seed_load.py`, `tests/unit/test_clock.py`, `test_thresholds.py`, `test_validation.py`, `test_routing.py`, `test_gestational_week.py`, `tests/integration/test_report_*.py`, `test_metric_alert.py`, `helpers.py` |
| Human review | Pending — test reviewer checks that the US-1 tests fail because the code is missing |
| Tests | Foundational: `5 passed` (seed 272 rows, foreign keys, RPT-006 → C6, clock). US-1: `5 passed, 26 errors` — every US-1 test errors with `ModuleNotFoundError` / `ImportError` (`mb360.main`, `mb360.alr.thresholds`, `validation`, `routing`, `reports` do not exist yet) |
| Spec issues found | none |
| Commit | see the commit of this entry |

### Entry 6: 14/10 Sang

| Field | Value |
|---|---|
| Path and agent | A (Claude Code, claude-opus-5-5) |
| Command and argument | `/speckit-implement Only the code tasks of the US-1 phase (T019 to T026). Do not change any test. If a test seems wrong, stop and tell me which and why. Do not change specs/, data/, data/seed/generate_seed.py or the constitution. Run all tests at the end and show me the output. Mark finished tasks [X] in tasks.md.` |
| Feature and tasks | `specs/001-alr-core`, T019 – T026 |
| What the agent produced | `app/mb360/alr/thresholds.py` (BR-004 from THRESHOLD_RULE, threshold card text), `validation.py` (FR-013, FR-014, BR-017; no range — ALR Q9), `routing.py` (BR-008), `reports.py` (FR-020, FR-015, provisional report code — ALR Q16), `cases.py` (FR-021); `app/mb360/main.py` (routes of contracts/http-routes.md); templates `base`, `select_mother`, `instructions` (S-027), `report_form` (S-025A), `metric_alert` (S-028), `report_status` (S-026 minimal) |
| Human review | Pending (pull request) |
| Tests | `63 passed, 1 xfailed` (xfail = ALR Q9). No test changed; `data/` unchanged (`generate_seed.py --check` OK) |
| Spec issues found | #3 below |
| Commit | see the commit of this entry |

### Entry 7: 14/10 Sang

| Field | Value |
|---|---|
| Path and agent | A (Claude Code, claude-opus-5-5) |
| Command and argument | `uv run tools/start_feature.py --spec specs/spec-CLI.md CLI --name core`; Step 1 consistency check (read-only) |
| Feature and tasks | `specs/002-cli-core` |
| What the agent produced | snapshot `specs/002-cli-core/spec.md`; consistency table: every stored field of CLI §5.1 maps to the data model (CARE_CASE, CASE_STATUS_HISTORY, STAFF_RESPONSE, WATCH_FLAG, STAFF, PATIENT_ASSIGNMENT) — 0 NOT FOUND |
| Human review | Accepted (Sang) |
| Tests | none |
| Spec issues found | none at this step |
| Commit | see the commit of this entry |

### Entry 8: 14/10 Sang

| Field | Value |
|---|---|
| Path and agent | A (Claude Code, claude-opus-5-5) |
| Command and argument | `/speckit-plan` — argument of agent-prompts §2 with "use the stack and project structure in specs/001-alr-core/plan.md"; scope US-1 + US-2 (both P1, same screens); sign-in out of scope (§10 Q11 → Complexity Tracking) |
| Feature and tasks | `specs/002-cli-core` |
| What the agent produced | `plan.md`, `research.md` (R1 – R7), `data-model.md`, `contracts/http-routes.md`, `quickstart.md`; `specs/spec-CLI.md` §10 Q15 added (interpretation of R3: assignment active on its `valid_to` day), snapshot refreshed |
| Human review | Pending — 8 questions of Workshop Guide 2.2 |
| Tests | none |
| Spec issues found | §10 Q15 (new) |
| Commit | see the commit of this entry |

### Entry 9: 14/10 Sang

| Field | Value |
|---|---|
| Path and agent | A (Claude Code, claude-opus-5-5) |
| Command and argument | `/speckit-tasks` (agent-prompts §3, seed test: 10 cases by status, C7 history) then `/speckit-analyze` |
| Feature and tasks | `specs/002-cli-core`, T001 – T020 |
| What the agent produced | `tasks.md` (tests T002, T003, T006 – T013 before code T004, T014 – T018); analysis: 0 CRITICAL, 0 HIGH, 3 MEDIUM (mother notifications deferred to ALR US-2; FR-008 chart as a table; any doctor may act on an escalated case — the spec does not limit it to the assigned doctor), 1 LOW (nurse default filter All, Q5) |
| Human review | Pending |
| Tests | none |
| Spec issues found | none new |
| Commit | see the commit of this entry |

### Entry 10: 14/10 Sang

| Field | Value |
|---|---|
| Path and agent | A (Claude Code, claude-opus-5-5) |
| Command and argument | `/speckit-implement Only the Setup and Foundational phases and the test tasks of the US-1/US-2 phase (T001 to T013). Do not write any code that makes those tests pass. Run the tests at the end and show me the output.` |
| Feature and tasks | `specs/002-cli-core`, T001 – T013 |
| What the agent produced | `app/mb360/cli/__init__.py`, `cli/actions.py` (`responsible_doctor` only, T004), fixture `staff_id` (T005); tests `tests/seed/test_seed_cli.py`, `tests/unit/test_cli_assignment.py`, `test_cli_actions.py`, `test_cli_permissions.py`, `test_cli_queue.py`, `tests/integration/test_cli_*.py` (5 files), `tests/cli_helpers.py`, `tests/__init__.py` |
| Human review | Changed: the seed test first assumed the order of two history rows of the same minute (C7); the rows keep CSV order, so the test now compares the set of statuses and the shared time / staff. The seed itself was right |
| Tests | Foundational `9 passed`. Whole suite `70 passed, 1 xfailed, 31 failed, 1 error` — every CLI failure is a missing function (`actions.mark_viewed`, `allowed`, `send_guidance`, `ActionError`, `cli.queue`) or a missing route (404) |
| Spec issues found | none |
| Commit | see the commit of this entry |

### Entry 11: 14/10 Sang

| Field | Value |
|---|---|
| Path and agent | A (Claude Code, claude-opus-5-5) |
| Command and argument | `/speckit-implement Only the code tasks of the US-1/US-2 phase (T014 to T018). Do not change any test. If a test seems wrong, stop and tell me which and why. Do not change specs/, data/, data/seed/generate_seed.py or the constitution. Run all tests at the end and show me the output. Mark finished tasks [X] in tasks.md.` |
| Feature and tasks | `specs/002-cli-core`, T014 – T018 |
| What the agent produced | `app/mb360/cli/actions.py` (status machine, permissions, guidance), `cli/queue.py` (S-061 rows, doctor badge), `cli/case_detail.py` (S-064 data, chatbot transcript), `cli/routes.py`; `main.py` registers the clinical routes; templates `staff_base`, `staff_select`, `cases` (S-061), `case` (S-064) |
| Human review | Pending (pull request) |
| Tests | `110 passed, 1 xfailed` (ALR + CLI; xfail = ALR Q9). No test changed; `data/` unchanged |
| Spec issues found | #4 below |
| Commit | see the commit of this entry |

### Entry 12: 20/10 Sang

| Field | Value |
|---|---|
| Path and agent | A (Claude Code, claude-opus-5-5) |
| Command and argument | Fix the start command after the app failed to start on Sang's laptop |
| Feature and tasks | `specs/001-alr-core`, `specs/002-cli-core` (quickstart.md); `AGENTS.md` §4 |
| What the agent produced | start and test commands changed to `uv run python -m uvicorn mb360.main:app --app-dir app --reload` and `uv run python -m pytest` in both quickstart.md files and AGENTS.md §4, with the reason |
| Human review | Requested by Sang (20/10) |
| Tests | `110 passed, 1 xfailed` (unchanged) |
| Spec issues found | none |
| Commit | see the commit of this entry |

### Entry 13: 21/10 Sang

| Field | Value |
|---|---|
| Path and agent | A (Claude Code, claude-opus-5-5) |
| Command and argument | `uv run tools/start_feature.py --spec specs/spec-ALR.md ALR --name status`; Step 1 check; `/speckit-plan` (stack of specs/001-alr-core; scope US-2 + FR-018; S-009 out); `/speckit-tasks`; `/speckit-analyze` |
| Feature and tasks | `specs/003-alr-status`, T001 – T016 |
| What the agent produced | snapshot; consistency: 0 NOT FOUND (NOTIFICATION, NOTIFICATION_PREFERENCE, CASE_STATUS_HISTORY, STAFF_RESPONSE); `plan.md`, `research.md` (R1 – R6), `data-model.md`, `contracts/http-routes.md`, `quickstart.md`, `tasks.md`; `specs/spec-ALR.md` §10 Q23 (wording of status-change notifications) and snapshot refreshed. Analyze: 0 CRITICAL, 0 HIGH, 2 MEDIUM (Safety note and hotline placeholders; Q23 wording interpretation), 1 LOW (entry links on S-027 / S-028 instead of S-008 / S-023) |
| Human review | Pending — 8 questions of Workshop Guide 2.2 |
| Tests | none yet |
| Spec issues found | §10 Q23 (new) |
| Commit | see the commit of this entry |

### Entry 14: 21/10 Sang

| Field | Value |
|---|---|
| Path and agent | A (Claude Code, claude-opus-5-5) |
| Command and argument | `/speckit-implement Only the Setup and Foundational phases and the test tasks of the US-2 phase (T001 to T008). Do not write any code that makes those tests pass. Run the tests at the end and show me the output.` |
| Feature and tasks | `specs/003-alr-status`, T001 – T008 |
| What the agent produced | `tests/seed/test_seed_alr_status.py`, `tests/unit/test_alr_my_reports.py`, `test_alr_status.py`, `test_alr_notifications.py`, `tests/integration/test_alr_my_reports_page.py`, `test_alr_status_page.py`, `test_alr_notifications_flow.py`, `tests/alr_status_helpers.py` |
| Human review | Pending — test reviewer |
| Tests | `112 passed, 1 xfailed, 10 failed, 3 errors` — the 2 new seed tests pass; every US-2 failure is a missing module (`alr.my_reports`, `alr.status`, `alr.notifications`), a missing route (404) or missing page content |
| Spec issues found | none |
| Commit | see the commit of this entry |

### Entry 15: 21/10 Sang

| Field | Value |
|---|---|
| Path and agent | A (Claude Code, claude-opus-5-5) |
| Command and argument | `/speckit-implement Only the code tasks of the US-2 phase (T009 to T014). Do not change any test. If a test seems wrong, stop and tell me which and why. Do not change specs/, data/, data/seed/generate_seed.py or the constitution. Run all tests at the end and show me the output. Mark finished tasks [X] in tasks.md.` |
| Feature and tasks | `specs/003-alr-status`, T009 – T014 |
| What the agent produced | `app/mb360/alr/notifications.py` (FR-018), `alr/my_reports.py` (S-029 rows), `alr/status.py` (progress, responses, Safety note); `alr/cases.py` and `cli/actions.py` call `notifications.notify` in their transactions; `main.py` routes `/m/{user}/my-reports`, S-026 full, `/m/{user}/cases/{case}`; templates `my_reports.html` (S-029), `report_status.html` (S-026 full, report and chatbot variants); "My reports" links on S-027 and S-028 |
| Human review | Pending (pull request) |
| Tests | `143 passed, 1 xfailed` (all features; xfail = ALR Q9). No test changed; `data/` unchanged |
| Spec issues found | none new |
| Commit | see the commit of this entry |

### Entry 16: 26/10 Sang

| Field | Value |
|---|---|
| Path and agent | A (Claude Code, claude-opus-5-5) |
| Command and argument | `uv run tools/start_feature.py --spec specs/spec-CLI.md CLI --name instructions`; Step 1 check; `/speckit-plan` (scope CLI US-3 + ALR FR-019, BR-001, BR-003 to close MVP Alpha G3; stack unchanged); `/speckit-tasks`; `/speckit-analyze` |
| Feature and tasks | `specs/004-cli-instructions`, T001 – T011 |
| What the agent produced | snapshot; consistency: 0 NOT FOUND (WATCH_FLAG, NOTIFICATION, NOTIFICATION_PREFERENCE); `plan.md`, `research.md` (R1 – R3), `data-model.md`, `contracts/http-routes.md`, `quickstart.md`, `tasks.md`. Analyze: 0 CRITICAL, 0 HIGH, 2 MEDIUM (FR-019 has no visit-insert path in the MVP, so it is tested as a function — D-59; new instruction has no visit — HLT §10 Q19), 1 LOW (no "Remove instruction") |
| Human review | Pending — 8 questions of Workshop Guide 2.2 |
| Tests | none yet |
| Spec issues found | none new (HLT Q19 already open) |
| Commit | see the commit of this entry |

### Entry 17: 26/10 Sang

| Field | Value |
|---|---|
| Path and agent | A (Claude Code, claude-opus-5-5) |
| Command and argument | `/speckit-implement Only the Setup and Foundational phases and the test tasks of the US-3 phase (T001 to T006). Do not write any code that makes those tests pass. Run the tests at the end and show me the output.` |
| Feature and tasks | `specs/004-cli-instructions`, T001 – T006 |
| What the agent produced | `tests/seed/test_seed_instructions.py`, `tests/unit/test_cli_instructions.py`, `test_alr_watch_flags_kept.py`, `test_alr_visit_notification.py`, `tests/integration/test_cli_instructions_page.py` |
| Human review | Pending — test reviewer |
| Tests | `146 passed, 1 xfailed, 6 failed, 1 error` — failures: `cli.instructions` and `notify_visit_result` missing, route 404, no form on S-064. `test_alr_watch_flags_kept` (ALR BR-001) passes before any code: it guards a rule no code breaks today, which is expected for a "never" rule |
| Spec issues found | none |
| Commit | see the commit of this entry |

### Entry 18: 26/10 Sang

| Field | Value |
|---|---|
| Path and agent | A (Claude Code, claude-opus-5-5) |
| Command and argument | `/speckit-implement Only the code tasks of the US-3 phase (T007 to T009). Do not change any test. If a test seems wrong, stop and tell me which and why. Do not change specs/, data/, data/seed/generate_seed.py or the constitution. Run all tests at the end and show me the output. Mark finished tasks [X] in tasks.md.` |
| Feature and tasks | `specs/004-cli-instructions`, T007 – T009 |
| What the agent produced | `app/mb360/cli/instructions.py` (FR-025, doctor only, one active instruction per metric); `notify_visit_result()` in `alr/notifications.py` (FR-019, BR-003); route `POST /staff/{staff}/cases/{case}/instructions`; S-064: "Edit" per instruction row and the "Add / edit instruction" form for doctors, "Assigned dd/mm/yyyy · Dr. name"; `cli/case_detail.py` reads the doctor's name |
| Human review | Pending (pull request) |
| Tests | `159 passed, 1 xfailed` (xfail = ALR Q9). No test changed; `data/` unchanged |
| Spec issues found | none |
| Commit | see the commit of this entry |

### Entry 20: 26/10 Sang

| Field | Value |
|---|---|
| Path and agent | A (Claude Code, claude-opus-5-5) |
| Command and argument | `uv run tools/start_feature.py --spec specs/spec-ACC.md ACC --name onboarding`; Step 1 check; `/speckit-plan` (scope ACC US-1 + US-2; simulated TCI app for §10 Q9; stack unchanged); `/speckit-tasks`; `/speckit-analyze`. Sang asked to build the slice first and review later (26/10) |
| Feature and tasks | `specs/005-acc-onboarding`, T001 – T013 |
| What the agent produced | snapshot; consistency: 0 NOT FOUND (USER_ACCOUNT, CONSENT_RECORD, NOTIFICATION_PREFERENCE, SESSION, PREGNANCY_PROFILE, HEALTH_METRIC_RECORD); `plan.md`, `research.md` (R1 – R6), `data-model.md`, `contracts/http-routes.md`, `quickstart.md`, `tasks.md`; `specs/spec-ACC.md` §10 Q22 (Notification Preference defaults, greeting, session lifetime) and snapshot refreshed. Analyze: 0 CRITICAL, 0 HIGH, 3 MEDIUM (simulated TCI identity — Q9; LMP rule provisional — Q10; DM-41 defaults — Q22), 1 LOW (S-008 shows only the ALR / HLT cards that exist) |
| Human review | Deferred by Sang (review after the slice) |
| Tests | none at this step |
| Spec issues found | §10 Q22 (new) |
| Commit | see the commit of this entry |

### Entry 21: 26/10 Sang

| Field | Value |
|---|---|
| Path and agent | A (Claude Code, claude-opus-5-5) |
| Command and argument | `/speckit-implement Only the Setup and Foundational phases and the test tasks of the US-1/US-2 phase (T001 to T007). Do not write any code that makes those tests pass. Run the tests at the end and show me the output.` |
| Feature and tasks | `specs/005-acc-onboarding`, T001 – T007 |
| What the agent produced | `app/mb360/acc/__init__.py`; `tests/seed/test_seed_acc.py`, `tests/unit/test_acc_entry.py`, `test_acc_setup.py`, `tests/integration/test_acc_onboarding_flow.py`, `test_acc_setup_page.py`, `test_acc_home_page.py`, `tests/acc_helpers.py` |
| Human review | Changed: the plan said "every seed session lasts 12 hours" and the seed test failed — only the 7 ordinary sessions do (U06, U07, U08 are edge cases). Test, plan, research and ACC Q22 corrected before any code |
| Tests | seed `12 passed`; whole suite: every ACC failure is a missing module (`acc.entry`, `acc.setup`) or a missing route (404) |
| Spec issues found | none |
| Commit | see the commit of this entry |

### Entry 22: 26/10 Sang

| Field | Value |
|---|---|
| Path and agent | A (Claude Code, claude-opus-5-5) |
| Command and argument | `/speckit-implement Only the code tasks of the US-1/US-2 phase (T008 to T011). Do not change any test. If a test seems wrong, stop and tell me which and why. Do not change specs/, data/, data/seed/generate_seed.py or the constitution. Run all tests at the end and show me the output. Mark finished tasks [X] in tasks.md.`; then T012 (quickstart walked in the browser) |
| Feature and tasks | `specs/005-acc-onboarding`, T008 – T012 |
| What the agent produced | `app/mb360/acc/entry.py` (open the sub-app, BR-007, consent, session), `acc/setup.py` (calculate / validate / save, D-72), `acc/routes.py`; `main.py` registers them; templates `tci_home`, `consent`, `not_female`, `guide`, `setup`, `home` |
| Human review | Deferred by Sang. Browser walk on Sang's laptop (26/10): simulated TCI account → consent → guide → Skip → setup with LMP 01/04/2026 → card "Week 25 · day 4, Due 06/01/2027" → Confirm → Home "Hello, Demo!", Week 25 |
| Tests | `198 passed, 1 xfailed` (xfail = ALR Q9). No test changed; `data/` unchanged |
| Spec issues found | none new |
| Commit | see the commit of this entry |

### Entry 23: 26/10 Sang

| Field | Value |
|---|---|
| Path and agent | A (Claude Code, claude-opus-5-5) |
| Command and argument | `uv run tools/start_feature.py --spec specs/spec-HLT.md HLT --name dashboard`; Step 1 check; `/speckit-plan` (scope HLT US-1 + US-2; based on PR #11 for Home); `/speckit-tasks`; `/speckit-analyze` |
| Feature and tasks | `specs/006-hlt-dashboard`, T001 – T010 |
| What the agent produced | snapshot; consistency: 0 NOT FOUND (HEALTH_METRIC_RECORD, VISIT, THRESHOLD_RULE, WATCH_FLAG, CARE_CASE); `plan.md`, `research.md` (R1 – R5), `data-model.md`, `contracts/http-routes.md`, `quickstart.md`, `tasks.md`. Every seed fact used in the tasks was checked with a query first (entry 21 lesson). Analyze: 0 CRITICAL, 0 HIGH, 2 MEDIUM (D-16 ranges; sleep rules proposed on S-024), 1 LOW (urine protein label shown although the drawing has none — follows FR-001) |
| Human review | Deferred by Sang |
| Tests | none at this step |
| Spec issues found | none new (all open points already marked in S-023 / S-024) |
| Commit | see the commit of this entry |

### Entry 24: 26/10 Sang

| Field | Value |
|---|---|
| Path and agent | A (Claude Code, claude-opus-5-5) |
| Command and argument | `/speckit-implement Only the Setup and Foundational phases and the test tasks of the US-1/US-2 phase (T001 to T005). Do not write any code that makes those tests pass. Run the tests at the end and show me the output.` |
| Feature and tasks | `specs/006-hlt-dashboard`, T001 – T005 |
| What the agent produced | `app/mb360/hlt/__init__.py`; `tests/seed/test_seed_hlt.py`, `tests/unit/test_hlt_dashboard.py`, `test_hlt_self_tracked.py`, `tests/integration/test_hlt_pages.py` |
| Human review | Deferred by Sang |
| Tests | seed tests pass; every HLT failure is a missing module (`hlt.dashboard`, `hlt.self_tracked`) or a missing route (404) |
| Spec issues found | none |
| Commit | see the commit of this entry |

### Entry 25: 26/10 Sang

| Field | Value |
|---|---|
| Path and agent | A (Claude Code, claude-opus-5-5) |
| Command and argument | `/speckit-implement Only the code tasks of the US-1/US-2 phase (T006 to T008). Do not change any test. If a test seems wrong, stop and tell me which and why. Do not change specs/, data/, data/seed/generate_seed.py or the constitution. Run all tests at the end and show me the output. Mark finished tasks [X] in tasks.md.`; then T009 (browser walk) |
| Feature and tasks | `specs/006-hlt-dashboard`, T006 – T009 |
| What the agent produced | `app/mb360/hlt/dashboard.py` (S-023 data, labels from THRESHOLD_RULE, fetal heart rate reference range from the Display only row), `hlt/self_tracked.py` (S-024 validation and Group 1 records), `hlt/routes.py`; `main.py` registers them; templates `health.html` (S-023), `self_tracked.html` (S-024); "Health metrics ›" on Home |
| Human review | Deferred by Sang. Browser walk (26/10): Lan → S-024 weight 57.4 + sleep 22:00 – 06:30 → "Metrics saved", Weight 57.4 kg, Sleep 8 h 30 min; visit section 15/09/2026 with labels and the reference range |
| Tests | `220 passed, 2 xfailed` (xfail = ALR Q9, HLT D-16). No test changed; `data/` unchanged |
| Spec issues found | none new |
| Commit | see the commit of this entry |

### Entry 26: 26/10 Sang

| Field | Value |
|---|---|
| Path and agent | A (Claude Code, claude-opus-5-5) |
| Command and argument | `uv run tools/start_feature.py --spec specs/spec-TML.md TML --name timeline`; Step 1 check; `/speckit-plan` (scope TML US-1 + US-2; based on PR #12); `/speckit-tasks`; `/speckit-analyze` |
| Feature and tasks | `specs/007-tml-timeline`, T001 – T010 |
| What the agent produced | snapshot; consistency: 0 NOT FOUND (DIARY_ENTRY, DIARY_IMAGE, FAMILY_MESSAGE, VISIT, HEALTH_METRIC_RECORD); `plan.md`, `research.md` (R1 – R4), `data-model.md`, `contracts/http-routes.md`, `quickstart.md`, `tasks.md`; seed facts checked with queries. Analyze: 0 CRITICAL, 0 HIGH, 3 MEDIUM (photo storage location not specified → git-ignored `media/`; FR-004 prefetch on server pages → in-memory cache; Messages to Baby shown read-only while D-03 is pending), 1 LOW (ultrasound files absent from the seed → placeholder) |
| Human review | Deferred by Sang |
| Tests | none at this step |
| Spec issues found | none new (Q9, Q10, Q11, Q14, Q15, Q17 already open) |
| Commit | see the commit of this entry |

### Entry 27: 26/10 Sang

| Field | Value |
|---|---|
| Path and agent | A (Claude Code, claude-opus-5-5) |
| Command and argument | `/speckit-implement Only the Setup and Foundational phases and the test tasks of the US-1/US-2 phase (T001 to T005). Do not write any code that makes those tests pass. Run the tests at the end and show me the output.` |
| Feature and tasks | `specs/007-tml-timeline`, T001 – T005 |
| What the agent produced | `app/mb360/tml/__init__.py`; `.gitignore` + `/media/`; `tests/seed/test_seed_tml.py`, `tests/unit/test_tml_weeks.py`, `test_tml_diary.py`, `tests/integration/test_tml_pages.py` |
| Human review | Deferred by Sang |
| Tests | `222 passed, 2 xfailed, 3 errors` — the seed tests pass; the 3 TML test files fail to import `tml.weeks` / `tml.diary` (missing code) |
| Spec issues found | none |
| Commit | see the commit of this entry |

### Entry 28: 26/10 Sang

| Field | Value |
|---|---|
| Path and agent | A (Claude Code, claude-opus-5-5) |
| Command and argument | `/speckit-implement Only the code tasks of the US-1/US-2 phase (T006 to T008). Do not change any test. If a test seems wrong, stop and tell me which and why. Do not change specs/, data/, data/seed/generate_seed.py or the constitution. Run all tests at the end and show me the output. Mark finished tasks [X] in tasks.md.`; then T009 (browser walk) |
| Feature and tasks | `specs/007-tml-timeline`, T006 – T009 |
| What the agent produced | `app/mb360/tml/weeks.py` (week data, prefetch cache), `tml/diary.py` (entry + photos, JPG / PNG by signature, ≤ 5, ≤ 10 MB, no edit / delete), `tml/routes.py` (+ `/media/` file route with a path check); templates `timeline.html` (S-048), `diary_form.html` (S-051 / S-052); Home week card → S-048 |
| Human review | Deferred by Sang. Two problems found by the agent while building and fixed: (1) the first prefetch cache would have shown stale indicators after a report or a self-tracked value saved on another screen — the cache is now reused only while the database is unchanged; **a regression test (`tests/integration/test_tml_cache_freshness.py`) was added after the fix, in Step 6** — a new test, no existing test changed, but it was not seen failing first; (2) the browser walk showed sleep as "22:30-06:00" on S-048 while S-023 shows "7 h 30 min" — S-048 now uses the same duration. Browser walk: Home → S-048 week 28 → diary with a PNG photo → "Diary entry saved", photo shown |
| Tests | `246 passed, 2 xfailed` (xfail = ALR Q9, HLT D-16). No existing test changed; `data/` unchanged |
| Spec issues found | none new |
| Commit | see the commit of this entry |

### Entry 29: 26/10 Sang

| Field | Value |
|---|---|
| Path and agent | A (Claude Code, claude-opus-5-5) |
| Command and argument | `uv run tools/start_feature.py --spec specs/spec-BOT.md BOT --name chat`; Step 1 check; `/speckit-plan` (scope BOT US-1 + US-2; **team decision (Sang, 26/10): LLM interface with a fake client by default, Gemini only when a member puts a key in the local `.env`**); `/speckit-tasks`; `/speckit-analyze` |
| Feature and tasks | `specs/008-bot-chat`, T001 – T012 |
| What the agent produced | snapshot; consistency: 0 NOT FOUND (CONVERSATION, CHAT_MESSAGE, AI_RESPONSE_LOG, CARE_CASE); `plan.md`, `research.md` (R1 – R5), `data-model.md`, `contracts/http-routes.md`, `quickstart.md`, `tasks.md`; `specs/spec-BOT.md` §10 Q14 (new conversation per visit; provisional personal-health and topic word lists) and snapshot refreshed. Analyze: 0 CRITICAL, 0 HIGH, 3 MEDIUM (D-47 danger phrases Pending SME; Q12 personal-health recognition by provisional markers; out-of-scope decided by topic words with the fake LLM), 1 LOW (Gemini client untested without a key) |
| Human review | Deferred by Sang |
| Tests | none at this step |
| Spec issues found | §10 Q14 (new) |
| Commit | see the commit of this entry |

### Entry 30: 26/10 Sang

| Field | Value |
|---|---|
| Path and agent | A (Claude Code, claude-opus-5-5) |
| Command and argument | `/speckit-implement Only the Setup and Foundational phases and the test tasks of the US-1/US-2 phase (T001 to T006). Do not write any code that makes those tests pass. Run the tests at the end and show me the output.` |
| Feature and tasks | `specs/008-bot-chat`, T001 – T006 |
| What the agent produced | `app/mb360/bot/__init__.py`; `.env.example` (setting names only) and `!.env.example` in `.gitignore` (the existing `.env.*` rule hid it; `.env` stays ignored); `tests/seed/test_seed_bot.py`, `tests/unit/test_bot_llm.py`, `test_bot_classify.py`, `test_bot_chat.py`, `tests/integration/test_bot_pages.py` |
| Human review | Changed: the seed test assumed every conversation has `current_session_data`; one edge-case conversation leaves the optional column empty — test and task corrected before any code (same lesson as entry 21: the counts were checked, the empty values were not) |
| Tests | seed `20 passed`; every BOT failure is a missing module (`bot.llm`, `bot.classify`, `bot.chat`) or a missing route (404). No test calls the network |
| Spec issues found | none |
| Commit | see the commit of this entry |

## 3. Spec issues found while building

Every gap the build uncovers goes back to `specs/spec-<MODULE>.md` (§10) as an open question or a spec change. It
is never fixed silently in code.

| # | Found at (step, entry) | Issue | Where it went in the spec | Status |
|---|---|---|---|---|
| 1 | Step 1, entry 1 | Seed RPT-006 contradicts ALR BR-006 and §5.1 (`source` = Doctor-assigned). Same defect as D4 of the main repository. Blocks the test "RPT-006 (140/90) opens C6" | No spec change needed (the spec is clear); fix in `data/seed/generate_seed.py`: give U09 an active blood-pressure Watch-Flag, set RPT-006 `watch_flag_id`, H14 `source` = Doctor-assigned, add a generator check for BR-006 — owner Hải Anh | Open |
| 2 | Part 0.3 | ALR §10 Q9 (valid input ranges, D-16) is blocking FR-014 | Ask the Client role; answer in a `## Clarifications` section of `specs/spec-ALR.md`, then `start_feature.py --refresh` | Open |
| 3 | Step 6, entry 6 | The schema rejects a Health Metric Record measured after it is recorded (`ck_hmr_measured_before_created`, HLT §6), so a future "Measured at" on S-025A would make the save fail. The code shows a field error instead; ALR §5.1 does not state this rule and no test covers it (the rule was removed from T010 in entry 3 because it was not in ALR) | Proposal for the ALR owner (Tâm): add to ALR §5.1 FR-014 "measured time not later than the submission time (HLT §6)", then add a test | Open |
| 4 | Step 6, entry 11 | CHAT_MESSAGE.`sent_at` has minute precision; a question and the chatbot reply are stored in the same minute, so the order of the transcript on S-064 (D-78) follows the storage order, not a rule | Proposal for the BOT owner (Sang): state in BOT §6 that the question is shown before its reply when the times are equal, or store seconds | Open |

## 4. Agent mistakes worth remembering

Short notes for the team and for Session 10 (debugging and code review): what the agent got
wrong, how you noticed, and what you changed in the prompt, `AGENTS.md` or the constitution so it
does not happen again.

| Entry | What went wrong | How it was caught | Prevention |
|---|---|---|---|
| 3 | The agent added a validation rule (measured time not in the future) that the spec does not state | Read of T010 against spec §5.1 | Every validation in a test task must cite the FR / BR / screen rule it comes from |
| 10 | A test assumed the order of rows that share the same timestamp | The test failed on correct seed data | Compare sets, or order by a column that is defined to be unique |
| 12 | quickstart.md used `uv run uvicorn`; on Windows with Smart App Control the `uvicorn.exe` shim is blocked ("An Application Control policy has blocked this file") | The app did not start on Sang's laptop (T019 / G1 check) | Start Python tools with `uv run python -m <tool>`; run quickstart on a real laptop before the pull request |
| 21 | The plan stated a fact about the seed ("every session lasts 12 hours") without checking it | The seed test written from the plan failed | Check every claim about the seed with a query before writing it into plan.md |
| 28 | A cache added for FR-004 was not invalidated by writes from other modules (stale timeline after a report) | Code reading while writing the routes | When a feature adds a cache, write a test that changes the data from another screen before writing the cache |
