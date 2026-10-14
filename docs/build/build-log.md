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
| `specs/002-cli-core` | CLI | US-1 (P1) nurse queue + US-2 (P1) doctor handles escalated case | Sang | `sang/002-cli-core` | Building — tests written (T001 – T013) |

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

## 3. Spec issues found while building

Every gap the build uncovers goes back to `specs/spec-<MODULE>.md` (§10) as an open question or a spec change. It
is never fixed silently in code.

| # | Found at (step, entry) | Issue | Where it went in the spec | Status |
|---|---|---|---|---|
| 1 | Step 1, entry 1 | Seed RPT-006 contradicts ALR BR-006 and §5.1 (`source` = Doctor-assigned). Same defect as D4 of the main repository. Blocks the test "RPT-006 (140/90) opens C6" | No spec change needed (the spec is clear); fix in `data/seed/generate_seed.py`: give U09 an active blood-pressure Watch-Flag, set RPT-006 `watch_flag_id`, H14 `source` = Doctor-assigned, add a generator check for BR-006 — owner Hải Anh | Open |
| 2 | Part 0.3 | ALR §10 Q9 (valid input ranges, D-16) is blocking FR-014 | Ask the Client role; answer in a `## Clarifications` section of `specs/spec-ALR.md`, then `start_feature.py --refresh` | Open |
| 3 | Step 6, entry 6 | The schema rejects a Health Metric Record measured after it is recorded (`ck_hmr_measured_before_created`, HLT §6), so a future "Measured at" on S-025A would make the save fail. The code shows a field error instead; ALR §5.1 does not state this rule and no test covers it (the rule was removed from T010 in entry 3 because it was not in ALR) | Proposal for the ALR owner (Tâm): add to ALR §5.1 FR-014 "measured time not later than the submission time (HLT §6)", then add a test | Open |

## 4. Agent mistakes worth remembering

Short notes for the team and for Session 10 (debugging and code review): what the agent got
wrong, how you noticed, and what you changed in the prompt, `AGENTS.md` or the constitution so it
does not happen again.

| Entry | What went wrong | How it was caught | Prevention |
|---|---|---|---|
| 10 | A test assumed the order of rows that share the same timestamp | The test failed on correct seed data | Compare sets, or order by a column that is defined to be unique |
| 3 | The agent added a validation rule (measured time not in the future) that the spec does not state | Read of T010 against spec §5.1 | Every validation in a test task must cite the FR / BR / screen rule it comes from |
