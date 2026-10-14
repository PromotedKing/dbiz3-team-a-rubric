# Session 8 agent prompts — adapted to this repository

The arguments of the [Workshop Guide](workshop-guide.md), rewritten for this repository's layout: Spec Documents in `specs/spec-<MODULE-ID>.md`, data model with ERD in `data/data-model-MB360.md`, schema in `data/schema/schema-MB360.sql` (SQLite 3), seed in `data/seed/NN_TABLE.csv` written by `data/seed/generate_seed.py`. Copy a block, replace every `<...>`, paste it in the agent chat (Claude Code or the Antigravity agent). Log every run in `docs/build/build-log.md`.

## 0. Before the first run (team decisions, Workshop Guide Part 0)

| Item | Status on 07/10/2026 | What to do |
|---|---|---|
| Core modules (0.2) | Not chosen | Proposal: **ALR** (report → threshold → case) and **CLI** (nurse / doctor handling) — README "Remaining differences" #1: the Must item "Risk Feedback & Health Alerts" completes its loop only with CLI. Write the choice and an owner each in `docs/team-work-report.md` |
| Blocking open questions (0.3) | ALR §10 Q9 (valid input ranges, D-16, Pending SME); CLI §10 Q11 (web sign-in) | Q9: ask the instructor (Client role), write the answer in a `## Clarifications` section of `specs/spec-ALR.md`. Q11: sign-in is out of scope until Session 11 — record it in Complexity Tracking of `plan.md` |
| Spec ↔ data agreement (0.1) | Readiness report §4: seed row RPT-006 (`BC-0927-020`) reports blood pressure with no `watch_flag_id` and source Self-entered, which breaks ALR BR-006 (the same defect as D4 in the main repository) | Fix before any test is written for BR-006 (owner of `data/seed/`: Hải Anh; data model: Sang) |
| Stack (0.4) | Not chosen | Must run on macOS + Windows with free tools, load the seed CSV files, have a terminal test runner, need no paid account. The chatbot backend is fixed to Python (BOT BR-003), so a Python stack with pytest keeps one language |

## 1. Prepare — consistency check (Step 1)

Run after `uv run tools/start_feature.py <MODULE-ID> --name core` and `git switch -c <folder it printed>`.

```text
Read-only task. Do not create, edit or delete any file.
For module <MODULE-ID>, list every field in the Input/Output table (section 5.1) of
specs/spec-<MODULE-ID>.md that is stored by the system. For each field, give the entity and
attribute in data/data-model-MB360.md (section 6) where it is stored (section 3, the CRUD matrix,
shows which FR writes which entity), or write NOT FOUND. Answer as one table.
```

Every NOT FOUND is fixed in `specs/spec-<MODULE-ID>.md` or `data/` before Step 2.

## 2. Plan — argument for /speckit-plan (Step 2)

```text
Stack (decided by the team): <language and version>, <framework>, <storage>, <test runner>.
It must run on macOS and Windows with free tools.
Scope of this feature: user story <US-1> (P1) of specs/spec-<MODULE-ID>.md only<, and US-2 (P2) if time allows>.
List every other user story of the spec as out of scope.
Data: the data model in data/data-model-MB360.md, the schema in data/schema/schema-MB360.sql and the
seed in data/seed/ (NN_TABLE.csv, loaded in filename order, written by data/seed/generate_seed.py)
are the source of truth and must not change. data-model.md must point to data/data-model-MB360.md
and list only which tables this slice reads and writes, and through which FR or BR. Do not redefine
any field. Thresholds are read from THRESHOLD_RULE, never hard-coded (AGENTS.md hard rule 7).
Login and deployment are out of scope until Session 11; if an FR needs them (for example
spec-CLI.md §10 Q11, staff sign-in), record it in Complexity Tracking.
quickstart.md must give the exact commands to install, load the seed, run the tests and start
the app, from a fresh clone, on macOS and Windows.
<For the second feature onward: use the stack and project structure in specs/001-.../plan.md.>
```

Review the plan with the 8 questions of Workshop Guide 2.2, then update `AGENTS.md` §2 (stack) and §4 (install, seed, test, run commands).

## 3. Tasks — argument for /speckit-tasks (Step 3)

```text
Tests are required by the constitution (Principle II). For every business rule in this slice
and every acceptance scenario of the user stories in scope, create a test task that comes
before the code task it checks. Include one test that loads the seed data and checks one value
that the Session 5 data package already states: data/seed/seed-report.md gives 271 rows in total, and
its scenario "ALR BR-008 branch 1" says report RPT-006 (exactly 140/90 mmHg) opens case C6.
Keep the user stories that plan.md marks out of scope out of tasks.md.
```

## 4. Analyze (Step 4)

`/speckit-analyze` with no argument. CRITICAL: fix before Step 5. HIGH: fix, or record in the build log why it does not affect this slice. A spec fix goes into `specs/spec-<MODULE-ID>.md`, then `uv run tools/start_feature.py --refresh`.

## 5. Tests first (Step 5)

```text
/speckit-implement Only the Setup and Foundational phases and the test tasks of the
<US-1> phase (<T001 to T0nn>). Do not write any code that makes those tests pass.
Run the tests at the end and show me the output.
```

The test reviewer checks that the tests fail, and fail because the code is missing.

## 6. Code (Step 6)

```text
/speckit-implement Only the code tasks of the <US-1> phase (<T0xx to T0yy>).
Do not change any test. If a test seems wrong, stop and tell me which and why.
Do not change specs/, data/ (including data/seed/generate_seed.py) or the constitution.
Run all tests at the end and show me the output. Mark finished tasks [X] in tasks.md.
```

Stop rules (Workshop Guide Step 6): the agent wants to change a test, the spec, the constitution or `data/`; the same failure survives three attempts; it wants a package `plan.md` does not list; it asks to run a command you do not understand.
