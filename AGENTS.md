# AGENTS.md — dbiz3-team-a (Mother & Baby 360°, Group A)

Every coding agent in this repository (Claude Code, the Antigravity agent, or any other) reads this file first and follows it. If a request conflicts with this file, stop and ask the human which one wins.

## 1. Project

Mother & Baby 360° is a maternity remote-monitoring sub-app for Thu Cuc Hospital, embedded in the hospital's patient app (TCI app). The expectant mother reviews the data captured at her hospital visits, reports a doctor-flagged metric or a symptom, keeps a pregnancy timeline and diary, and asks an AI chatbot for level-1 support; nurses and doctors triage and follow up her reports on a clinical web. The product scope is `docs/prd.md` (MVP Scope v8, Must items M1 – M5); the behaviour is specified module by module in `specs/`.

## 2. Stack

- Specification and data (Sessions 1 – 7): Markdown, Mermaid, SQLite 3 schema (`data/schema/schema-MB360.sql`), CSV seed files written by a Python 3 generator (standard library only).
- Tooling: Git + GitHub CLI, uv (Python 3.11 or later), Node.js 24 LTS, Spec Kit v1.0.1 (`.specify/`, integrations `agy` and `claude`, helper scripts in Python).
- Application stack (decided 14/10/2026, `specs/001-alr-core/plan.md`): **Python 3.11+, FastAPI + Jinja2 (server-rendered pages), SQLite 3 (`sqlite3`, built from `data/schema/schema-MB360.sql` + `data/seed/*.csv` at start-up), pytest + httpx**, managed with uv (`pyproject.toml`). Code in `app/mb360/`, tests in `tests/`. Do not add another framework, service or package that a `plan.md` does not list.

## 3. Hard rules

1. The repository is the source of truth: build only what `docs/prd.md`, `specs/`, `screens/` and `data/` state; if they disagree or a value is missing, stop and ask — never guess, and never resolve a `[NEEDS CLARIFICATION: …]` or `[PENDING CLIENT: D-xx]` marker yourself.
2. Never edit the seed CSV files or `data/seed/seed-report.md` by hand: change `data/seed/generate_seed.py`, run the seed command, and check that `git status` shows only the changes you intended.
3. Never commit real personal data or secrets: no real patient, mother or staff value, no `.env` file, API key, password or token (gate G5). Test values only, invented as in `data/data-model-MB360.md` §11.
4. Keep the chain consistent in dependency order: PRD → spec (FR, §5.1 fields, business rules) → data model → schema → seed → screens. A change to one file names the downstream files it affects in the same pull request.
5. Work on a branch named `member-name/short-topic` (for example `tam/alr-report-form`), show the diff to a human before committing, and never push to `main`, move a tag, or rewrite Git history.
6. Never edit generated files (`.specify/`, `.agents/skills/`, `.claude/skills/`) and never upgrade Spec Kit: the team stays on v1.0.1. Do not create a `CLAUDE.md`.
7. Clinical safety: the word "Alert" is used only for an above-threshold report (ALR BR-010); the chatbot never diagnoses and never sends the medical record (BOT §5.2); thresholds come only from THRESHOLD_RULE, never hard-coded.
8. Build with Spec Kit from a snapshot of the spec: for example `uv run tools/start_feature.py ALR --name core` makes `specs/001-alr-core/spec.md` (module ID and slice name chosen by the team); never edit that copy by hand, and run `uv run tools/start_feature.py --check` before `/speckit-plan`, `/speckit-tasks` and `/speckit-implement`. After every agent run that creates or changes a file in `specs/`, the code or `tests/`, add an entry to `docs/build/build-log.md`.

## 4. How to run

From the repository root (Windows, macOS, Linux):

```bash
uv run tools/check_env.py --repo              # T1: toolchain and repository (Path A: add --path A)
uv run data/seed/generate_seed.py             # T2: seed command (see below), then: git status
uv run data/seed/generate_seed.py --check     # same checks, writes nothing
uv run tools/check_data_model.py              # data model §5 diagram check + seed load in filename order (gate G3)
uv run tools/start_feature.py ALR --name core   # Session 8: snapshot specs/spec-ALR.md into specs/001-alr-core/ and make it the active feature
uv run tools/start_feature.py --check     # the snapshot still matches its source spec
uv run tools/start_feature.py --use specs/001-alr-core   # choose the active feature after a fresh clone
```

Application (from Session 8, `specs/001-alr-core/quickstart.md`):

```bash
uv sync                                               # install the packages of pyproject.toml into .venv
uv run python -m pytest                                       # run all tests (the database is built from schema + seed in memory)
uv run python -m uvicorn mb360.main:app --app-dir app --reload  # start the app at http://127.0.0.1:8000 (clinical web: /staff)
```

The app is started with `python -m uvicorn` instead of the `uvicorn.exe` shim: Windows Smart App Control blocks the unsigned shim that uv creates (readiness report W1).

## 5. Data model

The Spec Documents are split per module (Session 4 layout), not in one `docs/spec/spec-document.md`:

| Module | Spec | Owns the entities |
|---|---|---|
| ACC | `specs/spec-ACC.md` | USER_ACCOUNT, SESSION, PREGNANCY_PROFILE, CONSENT_RECORD, EMR_LINKAGE_REQUEST, NOTIFICATION, NOTIFICATION_PREFERENCE |
| HLT | `specs/spec-HLT.md` | HEALTH_METRIC_RECORD, VISIT, PATIENT_CLINICAL_PROFILE, WATCH_FLAG |
| ALR | `specs/spec-ALR.md` | METRIC_REPORT, REPORT_SYMPTOM, CARE_CASE, STAFF_RESPONSE, GUIDANCE_TEMPLATE, THRESHOLD_RULE |
| CLI | `specs/spec-CLI.md` | CASE_STATUS_HISTORY, STAFF, PATIENT_ASSIGNMENT |
| TML | `specs/spec-TML.md` | DIARY_ENTRY, DIARY_IMAGE, FAMILY_MESSAGE |
| BOT | `specs/spec-BOT.md` | CONVERSATION, CHAT_MESSAGE, AI_RESPONSE_LOG |
| APT | `specs/spec-APT.md` | none stored (appointments stay in the TCI app) |

In every spec, §5.1 is the Input/Output contract of each FR (field, type, required flag), §5.2 the business rules and §6 the key entities. The one data model for all modules is `data/data-model-MB360.md` (MODULE-ID MB360): 26 stored entities (§2), Mermaid ERD with 40 relationships (§4), logical model (§6), business rules and where they are enforced (§8). Schema: `data/schema/schema-MB360.sql`. Seed: 26 files `data/seed/NN_TABLE.csv`, 141 rows, loaded in filename order.

## 6. Business rules

The rule an agent must never break: **a report creates an "Alert" only when its value is above the threshold in THRESHOLD_RULE (blood pressure: systolic ≥ 140 mmHg or diastolic ≥ 90 mmHg), while a report with at least one symptom always goes to the nurse queue with status "Not viewed", whatever the threshold result** (ALR BR-002, BR-004, BR-007; enforced as listed in `data/data-model-MB360.md` §8). All rules: §5.2 of each spec.

## 7. File owners

Shared files have one owner. Others propose changes through a pull request that the owner reviews and merges.

| Path | Owner | Reviewer |
|---|---|---|
| `AGENTS.md`, `README.md`, `tools/`, `.agents/rules/`, `.specify/memory/constitution.md` | Trung | Tâm |
| `docs/prd.md`, `docs/decisions.md` | Trung | Chi |
| `specs/spec-ACC.md` | Chi | Trung |
| `specs/spec-HLT.md` | Ánh | Hải Anh |
| `specs/spec-ALR.md` | Tâm | Sang |
| `specs/spec-CLI.md` | Trung | Tâm |
| `specs/spec-TML.md` | Tâm | Ánh |
| `specs/spec-BOT.md` | Sang | Chi |
| `specs/spec-APT.md` | Hải Anh | Chi |
| `screens/`, `docs/screen-list.md`, `docs/ui-label-reference.md` | Chi | Ánh |
| `data/data-model-MB360.md`, `data/schema/` | Tâm | Trung |
| `data/seed/` | Hải Anh | Tâm |
| `docs/env/readiness-report.md` | every member edits only their own row | Trung |
| `docs/build/build-log.md` | the member who ran the agent writes the entry | the pull request reviewer |
| `docs/build/` (other files), `tools/start_feature.py`, `.github/` | Trung + Sang | Tâm |
| `docs/ai-use-log.md` | the member who checked the artefact | Trung |

## Seed command

```bash
uv run data/seed/generate_seed.py
```

Equivalent without uv: `python3 data/seed/generate_seed.py` (Windows: `python data/seed/generate_seed.py`). It checks the keys, foreign keys and business rules, loads the schema and every seed file into an in-memory SQLite database, and rewrites the 26 CSV files, `appointment-demo.json` and `seed-report.md` byte for byte. Pass condition (T2): it prints `OK` and `git status` shows no changed file.
