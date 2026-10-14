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
| `specs/001-alr-core` | ALR | US-1 (P1) — submit a metric or symptom report (US-2 if time allows) | Sang | `sang/001-alr-core` | Tasks — analyzed, ready for Step 5 (tests first) |

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

## 3. Spec issues found while building

Every gap the build uncovers goes back to `specs/spec-<MODULE>.md` (§10) as an open question or a spec change. It
is never fixed silently in code.

| # | Found at (step, entry) | Issue | Where it went in the spec | Status |
|---|---|---|---|---|
| 1 | Step 1, entry 1 | Seed RPT-006 contradicts ALR BR-006 and §5.1 (`source` = Doctor-assigned). Same defect as D4 of the main repository. Blocks the test "RPT-006 (140/90) opens C6" | No spec change needed (the spec is clear); fix in `data/seed/generate_seed.py`: give U09 an active blood-pressure Watch-Flag, set RPT-006 `watch_flag_id`, H14 `source` = Doctor-assigned, add a generator check for BR-006 — owner Hải Anh | Open |
| 2 | Part 0.3 | ALR §10 Q9 (valid input ranges, D-16) is blocking FR-014 | Ask the Client role; answer in a `## Clarifications` section of `specs/spec-ALR.md`, then `start_feature.py --refresh` | Open |

## 4. Agent mistakes worth remembering

Short notes for the team and for Session 10 (debugging and code review): what the agent got
wrong, how you noticed, and what you changed in the prompt, `AGENTS.md` or the constitution so it
does not happen again.

| Entry | What went wrong | How it was caught | Prevention |
|---|---|---|---|
| 3 | The agent added a validation rule (measured time not in the future) that the spec does not state | Read of T010 against spec §5.1 | Every validation in a test task must cite the FR / BR / screen rule it comes from |
