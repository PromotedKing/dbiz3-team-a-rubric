# DBIZ3 Session 8 Workshop Guide: Build the Core Module from the Spec Document

> Markdown copy of `Session8_Workshop-Guide.docx` (course material, version 4 October 2026), kept word for word except line breaks restored inside the command blocks. **This repository** keeps the Spec Documents in `specs/spec-<MODULE-ID>.md` (not `docs/spec/`), the data model in `data/data-model-MB360.md` and the schema in `data/schema/schema-MB360.sql`. Where the guide says `docs/spec/`, read `specs/spec-<MODULE-ID>.md`; the agent arguments adapted to this layout are in [`agent-prompts.md`](agent-prompts.md).

SESSION 8 · SDD STEPS ⑤⑥ TASKS / IMPLEMENT · WORKSHOP GUIDE

Course: DBIZ3 AI-native Product Development
Instructor: Dr. Phạm Văn Chiến, VJCBI College, Foreign Trade University
Version: 4 October 2026. Spec Kit commands were run with Spec Kit v1.0.1 (the version installed in Session 6) on this date. Tool versions change often; Part F lists the sources.

## How this session works

Session 8 is the first build session. Your team turns the Spec Document into running code, one thin slice at a time, with an AI coding agent doing the typing and humans doing the deciding.

| Item | Detail |
|---|---|
| Course step | ⑤ Tasks and ⑥ Implement (Engineer role) |
| Input | Your repository from Sessions 6 and 7: docs/spec/, data/, AGENTS.md, Spec Kit in .specify/ |
| Output today | The first user story (P1) of one core module: planned, broken into tasks, tested and running, in a reviewed pull request |
| Output by the start of Session 9 | MVP Alpha: every core module's P1 story running, tagged mvp-alpha (Part D) |
| Length | 135 minutes |

What is new today, in one sentence: you stop writing documents about the product and start running the Spec Kit chain /speckit-plan, /speckit-tasks, /speckit-analyze, /speckit-implement against your own spec.

## Part 0. Before class (homework, about 60 minutes as a team)

Do these steps before class. In class there is no time to choose a stack or to argue about scope.

**0.1 Close the Session 7 items.** Conditional Go teams: fix the items listed in your Session 7 review for the module you will build first. Every team: make sure the spec and the data model of that module agree. The most common Session 7 problem was a data model changed in Session 5 while the spec still described the old fields. The agent reads the spec, so it will build the old version.

**0.2 Choose the core modules.** Open your MVP Scope v3 (Session 1). The core modules are the ones on the main path of the product: without them the product cannot be demonstrated at all. Choose one or two. Write them in your work allocation table with an owner each.

**0.3 Close blocking open questions.** Open the Spec Document of the first core module. Any open question marked "Blocking: Yes" must be answered (ask the instructor in the Client role) and written into the spec, in a section called `## Clarifications`, before class. /speckit-plan stops when a blocking unknown is left.

**0.4 Draft the stack decision.** Your team chooses its own stack. It will be written into plan.md in class, so agree on it now. The course has four constraints:

1. It runs on every member's laptop, macOS and Windows, with free tools.
2. It can load the Session 5 seed data, or the plan explains how the seed is loaded.
3. It has a test runner that the agent can call from the terminal (for example pytest, npm test).
4. No member needs to buy a new paid account to run it.

If your team already used a platform in Sessions 5 to 7 (for example Firebase or Supabase), keep it unless it breaks a constraint.

**0.5 Add the Session 8 build kit to the repository.** Download Session8_Build-Kit.zip and copy into the repository root:

| File | Purpose |
|---|---|
| tools/start_feature.py | Connects a module spec in docs/spec/ to Spec Kit (Step 1) |
| docs/build/constitution-starter.md | Text for /speckit-constitution |
| docs/build/build-log.md | Build log template |
| docs/build/mvp-alpha-checklist.md | MVP Alpha checklist template |
| .github/pull_request_template.md | Review checklist that GitHub shows on every pull request |

**0.6 Write the constitution.** One member runs /speckit-constitution in the agent chat, with the text inside docs/build/constitution-starter.md as the argument (replace the `<...>`). Read the result in .specify/memory/constitution.md: five principles, no technology names. Commit and push through a pull request.

**0.7 Everyone pulls and checks.** Every member: `git switch main`, `git pull`, then `uv run tools/check_env.py --repo`. No FAIL line.

## Part A. Why the repository needs one bridge

Spec Kit v1.0.1 looks for the active feature in the file `.specify/feature.json`, and it expects the specification of that feature at `specs/<feature>/spec.md`. Your Spec Document lives in docs/spec/ (Sessions 4 and 6). The script `tools/start_feature.py` connects the two without moving anything:

- it copies `docs/spec/spec-<MODULE>.md` to `specs/<NNN>-<module>-<slice>/spec.md` as a read-only snapshot, and records the source file and its fingerprint (SHA-256) in the first line;
- it writes `.specify/feature.json`, so every Spec Kit command works on that feature;
- `--check` tells you when docs/spec/ changed after the snapshot, so the plan may be out of date.

The rule does not change: `docs/spec/` is the single source of truth. Never edit `specs/<feature>/spec.md` by hand. If the build shows that the spec is wrong, fix docs/spec/, then run `--refresh`.

Spec Kit keeps `.specify/feature.json` out of Git on purpose: each laptop chooses its own active feature. After every fresh clone, or when you switch to a teammate's feature, run `uv run tools/start_feature.py --use specs/<folder>`.

## Part B. The build loop

Every slice goes through the same eight steps. Steps 2 to 5 are done once per slice; steps 6 and 7 repeat for each phase of tasks.md.

| # | Step | Command | Who decides |
|---|---|---|---|
| 1 | Prepare | `uv run tools/start_feature.py <MODULE> --name <slice>`, then a branch with the folder name it prints | Driver |
| 2 | Plan | /speckit-plan with the argument in 2.1 | Whole team approves the stack and the plan |
| 3 | Tasks | /speckit-tasks with the argument in 3.1 | Spec keeper checks coverage |
| 4 | Analyze | /speckit-analyze (read-only) | Team triages every CRITICAL and HIGH finding |
| 5 | Tests first | /speckit-implement limited to the test tasks of one phase | Test reviewer sees them fail |
| 6 | Code | /speckit-implement limited to the code tasks of the same phase | Driver, then test reviewer sees them pass |
| 7 | Verify | Run the tests, follow quickstart.md, click the demo path | Everyone on their own laptop |
| 8 | Log and review | Build log entry, commit, pull request, review, merge | A member who did not write the code approves |

### Roles in the team (rotate for every slice)

| Role | Job during the loop |
|---|---|
| Driver | Types into the agent, shares the screen, never accepts a change the team has not seen |
| Spec keeper | Has docs/spec/ open; checks every plan decision and task against an FR or BR |
| Data keeper | Has data/ open; stops any change to the Session 5 data model that was not agreed |
| Test reviewer | Reads every test before the code exists; checks that each test can actually fail |
| Logger | Writes the build log entry right after each run |

A team of 5 or 6 can run a second core module in parallel only after the first slice's Setup and Foundational phases are merged into main. Two branches that each create the project scaffold will conflict in almost every file.

### Step 1. Prepare (5 minutes)

```text
git switch main
git pull
uv run tools/start_feature.py <MODULE> --name core
git switch -c <the folder name it printed, for example 001-acc-core>
```

If your team keeps every module in one file: `uv run tools/start_feature.py --spec docs/spec/spec-document.md <MODULE> --name core`.

Then run one read-only consistency check, the same check as criterion T3 in Session 7. Paste into the agent:

```text
Read-only task. Do not create, edit or delete any file.
For module <MODULE>, list every field in the Input/Output table (section 5.1) of
docs/spec/spec-<MODULE>.md that is stored by the system. For each field, give the entity and
attribute in data/ where it is stored, or write NOT FOUND. Answer as one table.
```

Every NOT FOUND is fixed in docs/spec/ or data/ before Step 2, not during the build.

### Step 2. Plan (20 minutes)

#### 2.1 Argument for /speckit-plan

Copy, replace every `<...>`, and paste after /speckit-plan in the agent chat.

```text
Stack (decided by the team): <language and version>, <framework>, <storage>, <test runner>.
It must run on macOS and Windows with free tools.
Scope of this feature: user story <US-1> (P1) only<, and US-2 (P2) if time allows>.
List every other user story of the spec as out of scope.
Data: the data model, schema and seed in data/ are the source of truth and must not change.
data-model.md must point to data/data-model-<MODULE>.md and list only which tables or
collections this slice reads and writes, and through which FR or BR. Do not redefine any field.
Login and deployment are out of scope until Session 11; if an FR needs them, record it in
Complexity Tracking.
quickstart.md must give the exact commands to install, load the seed, run the tests and start
the app, from a fresh clone, on macOS and Windows.
<For the second feature onward: use the stack and project structure in specs/001-.../plan.md.>
```

#### 2.2 Review the plan before you accept it

The driver reads each line aloud; the team answers yes or no. One "no" means the plan goes back to the agent with the reason.

1. The Technical Context names the stack your team chose, and no extra framework or service.
2. No NEEDS CLARIFICATION is left in plan.md or research.md.
3. The Constitution Check table shows every principle, with a reason, not only "PASS".
4. data-model.md changes nothing in data/.
5. Every route, screen or function in contracts/ traces to an FR in the spec.
6. quickstart.md can be run by a member who was not in the room.
7. Every decision in research.md that is an interpretation of the spec (not stated in it) is copied into the spec's open questions.
8. The plan does not include a user story that the scope excluded.

Then: update section 2 of AGENTS.md with the stack and the real commands (install, seed, test, run), commit, and continue.

### Step 3. Tasks (10 minutes)

#### 3.1 Argument for /speckit-tasks

```text
Tests are required by the constitution (Principle II). For every business rule in this slice
and every acceptance scenario of the user stories in scope, create a test task that comes
before the code task it checks. Include one test that loads the seed data and checks one value
that the Session 5 data package already states (for example a computed total or rate).
Keep the user stories that plan.md marks out of scope out of tasks.md.
```

#### 3.2 Check

- Every BR of the module that this slice touches has its own test task.
- Every test task comes before the code task it checks.
- Every task names an exact file path.
- The first user story phase can be finished and demonstrated on its own.

### Step 4. Analyze (5 minutes)

Run /speckit-analyze with no argument. It is read-only: it reads spec.md, plan.md and tasks.md and reports duplicated, ambiguous, under-specified or inconsistent items, coverage gaps, and conflicts with the constitution, each with a severity.

| Severity | What the team does before Step 5 |
|---|---|
| CRITICAL | Fix. A constitution conflict is always CRITICAL. Do not implement until it is gone |
| HIGH | Fix, or record in the build log why it does not affect this slice |
| MEDIUM, LOW | Record in the build log; fix later |

A fix to the spec goes into docs/spec/, then `uv run tools/start_feature.py --refresh`, then a check that plan.md and tasks.md still hold.

### Step 5. Tests first (15 minutes)

```text
/speckit-implement Only the Setup and Foundational phases and the test tasks of the
<US-1> phase (<T001 to T0nn>). Do not write any code that makes those tests pass.
Run the tests at the end and show me the output.
```

The test reviewer checks two things before anyone continues: the tests fail, and they fail for the right reason (the code is missing, not a typo in the test). A test that passes before the code exists checks nothing.

### Step 6. Code (25 minutes)

```text
/speckit-implement Only the code tasks of the <US-1> phase (<T0xx to T0yy>).
Do not change any test. If a test seems wrong, stop and tell me which and why.
Run all tests at the end and show me the output. Mark finished tasks [X] in tasks.md.
```

Stop rules for the driver:

- The agent wants to change a test, the spec, the constitution or data/: stop. A human decides, and a spec change goes into docs/spec/.
- The same failure survives three fix attempts: stop, write it in the build log, ask the instructor.
- The agent wants to install a package that plan.md does not list: stop and decide as a team.
- The agent asks for permission to run a command you do not understand: refuse, then ask.

### Step 7. Verify (5 minutes per member)

On your own laptop, not only the driver's:

1. git pull the branch, then `uv run tools/start_feature.py --use specs/<folder>`.
2. Follow quickstart.md from the top.
3. All tests pass.
4. Click through the demo path of the user story; compare each screen with the acceptance scenarios.
5. Pick one business rule and find both its test and the line of code that applies it.

### Step 8. Log and review

1. Logger adds the build log entry (template in docs/build/build-log.md).
2. Driver commits with a message such as `feat(<MODULE>): US-1 <short summary>` and pushes the branch.
3. Open a pull request. GitHub fills in the review checklist from .github/pull_request_template.md.
4. A member who did not write the code reviews, runs Step 7, and approves. Then merge.

## Part C. Access paths

| Path | Who | How you take part |
|---|---|---|
| A | Paid Claude plan | Run the Spec Kit commands in Claude Code (claude in the Antigravity terminal). The skills are in .claude/skills/ |
| B | No paid Claude plan | Run the same commands in the Antigravity agent panel. The skills are in .agents/skills/. Keep the permission setting from Session 6 (Request Review, never Turbo or Always Proceed) |
| C | Browser only | You do not run the agent. Take a review role: paste plan.md or tasks.md into claude.ai and ask it to check them against the spec, then bring its findings to the team. You still do Step 7 on your laptop |

The commands are typed in the agent chat, not in the terminal, in the hyphen form shown in this guide (/speckit-plan). Some documentation writes them with a dot (/speckit.plan); it is the same step.

Path B note: the free quota of the Antigravity agent refreshes weekly. Plan, tasks and analyze use a lot of it. Let one member with quota drive the planning steps, and save your own quota for implementing.

## Part D. MVP Alpha

In DBIZ3, MVP Alpha means: the core modules of the product run end to end on the Session 5 seed data, for their highest-priority user story, from a clean clone, with the business rules covered by passing tests. It is a course definition, not a market release. It does not need login, deployment or a polished interface; those come in Sessions 10 and 11.

Deadline: tag `mvp-alpha` on main before Session 9, with docs/build/mvp-alpha-checklist.md filled in at that commit. The eight gates of the checklist:

| Gate | Evidence |
|---|---|
| G1 Clean clone runs on two members' laptops | Names in the checklist |
| G2 P1 story of every core module works on the seed data | Demo path in the checklist |
| G3 Every BR and P1 acceptance scenario has a passing test | Last line of the test run |
| G4 Spec snapshot is current | start_feature.py --check prints OK |
| G5 Analyze findings handled | Build log |
| G6 Every change reviewed in a pull request | GitHub history |
| G7 No real personal data, no secrets | Checked by a member |
| G8 Every agent run logged | Build log |

Write the limitations honestly in section 3 of the checklist. A limitation you wrote down is part of the plan; one the instructor discovers is not.

## Part E. Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| ERROR: no active feature on this laptop | Fresh clone; .specify/feature.json is not in Git | `uv run tools/start_feature.py --use specs/<folder>` |
| /speckit-plan reports "Feature directory not found" | start_feature.py not run on this laptop | Same as above |
| DRIFT from --check | Someone changed docs/spec/ after the snapshot | --refresh, then re-read plan.md and tasks.md against the change |
| The agent edits specs/<feature>/spec.md | It treats the snapshot as editable | Reject the change; make it in docs/spec/; --refresh |
| plan.md keeps NEEDS CLARIFICATION | A blocking open question is still open | Ask the Client, write the answer in docs/spec/ under Clarifications, --refresh, re-run plan |
| data-model.md redefines your entities | The plan template asks the agent to "extract entities" | Re-run with the data sentence of 2.1; reject any change to data/ |
| tasks.md has no test tasks | Spec Kit only adds tests when asked | Re-run /speckit-tasks with the argument in 3.1 |
| The agent says the work is done but tests were not run | It reported instead of verifying | Run the tests yourself; paste the output back to the agent |
| Two branches both created the scaffold | Parallel work started before Foundational was merged | Keep one; rebase the other branch onto main after merging |
| Quota exhausted (Path B) | Weekly free quota used | Switch model, or let a teammate drive; do not create extra accounts |

## Part F. References

Accessed 4 October 2026 unless stated.

- GitHub, Spec Kit, release v1.0.1 (21 August 2026): repository README, command skills speckit-plan, speckit-tasks, speckit-analyze, speckit-implement, and the helper scripts in .specify/scripts/python/ (read in a repository initialised with --integration agy --script py). https://github.com/github/spec-kit
- GitHub, Spec Kit documentation, "Adopting Spec Kit in an Existing Project". https://github.github.io/spec-kit/guides/existing-projects.html
- Anthropic, "Best practices for Claude Code" (sections "Explore first, then plan, then code" and "Give Claude a way to verify its work"). https://code.claude.com/docs/en/best-practices
- Beck, K. (2002). Test-Driven Development: By Example. Addison-Wesley.
- Wake, B. (2003, 17 August). INVEST in Good Stories, and SMART Tasks. XP123. https://xp123.com/invest-in-good-stories-and-smart-tasks/
- DBIZ3 course materials: Session 4 Spec Document template, Session 5 data package rules, Session 6 Setup Guide, Session 7 Midterm Rubric.
