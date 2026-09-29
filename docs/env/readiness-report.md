# Environment Readiness Report: dbiz3-team-a (Mother & Baby 360°)

One row per member (Setup Guide Part D). Each member runs T1, T2 and T3 on their own laptop, in a fresh clone, and fills **only their own row**. Status values: PASS / WARN (explained in §4) / FAIL / Not run.

## 1. Members

| Member | GitHub username | OS | Path (0.2) | Agent(s) used for T3 | Models seen in the picker | T1 toolchain | T2 seed | T3 read-back | Date | Notes |
|---|---|---|---|---|---|---|---|---|---|---|
| Setup machine — *member name to add* | PromotedKing | Windows 11 Home 10.0.26200 | A | Claude Code 2.1.281 (claude-opus-5-5) | — | WARN (§2, W1) | PASS (§2) | Answer key §3.2; fresh-session run to record | 30/09/2026 | Repository set up from this machine |
| Trung | | | | | | Not run | Not run | Not run | | |
| Tâm | | | | | | Not run | Not run | Not run | | |
| Ánh | | | | | | Not run | Not run | Not run | | |
| Chi | | | | | | Not run | Not run | Not run | | |
| Hải Anh | | | | | | Not run | Not run | Not run | | |
| Sang | | | | | | Not run | Not run | Not run | | |

When the member who owns the setup machine fills their own row, delete the "Setup machine" row and keep its results in theirs.

## 2. T1 and T2 on the setup machine (30/09/2026)

T1 — `uv run tools/check_env.py --repo --path A`: no FAIL.

| Check | Result |
|---|---|
| Python (via uv) | PASS 3.13.14 |
| git, identity | PASS 2.55.0.windows.3 |
| GitHub CLI, login | PASS 2.101.0, logged in |
| uv | PASS 0.12.18 |
| Node.js 24 LTS | PASS v24.19.0 |
| Spec Kit 1.0.1 | **WARN** 1.0.1 found with `uv tool list`; `specify.exe` itself is blocked by Windows (W1) |
| Claude Code (Path A) | PASS 2.1.281 |
| Repository checks (AGENTS.md, .specify/, .agents/rules/, constitution, PRD, 7 Spec Documents, data model + ERD, 28 Screen Specs, schema, seed, this report, AI use log, no secrets, .gitattributes, seed `--check`) | PASS |

T2 — `uv run data/seed/generate_seed.py`, then `git status`: prints `OK — 26 tables, 272 rows; all checks passed; wrote 26 CSV files + seed-report.md`; `git status` shows no changed file. `uv run tools/check_data_model.py`: `OK — 26 tables, 172 columns, 40 relationships = 40 foreign keys; … 26 seed files, 272 rows load in filename order`.

## 3. T3 agent read-back

### 3.1 Prompt used (adapted to this repository's layout)

The Setup Guide prompt points to `docs/spec/spec-document.md` §5.1 and §6. This repository uses the Session 4 layout (one spec per module in `specs/`, entities catalogued in the data model), so every member uses this prompt, identically, in every agent:

```text
Read-only task. Do not create, edit or delete any file, and do not run any
command that changes the repository.
1. From data/data-model-MB360.md section 2, list the stored entity names
   (the 26 entities, not the ones marked "not stored").
2. For each seed data file under data/seed/, report the number of data records
   (exclude header rows).
3. State ALR BR-002 from specs/spec-ALR.md section 5.2 in one sentence.
4. Quote the first hard rule in AGENTS.md.
Answer as one table.
```

### 3.2 Answer key (computed from the files, not by an agent)

1. **26 entities:** USER_ACCOUNT, SESSION, PREGNANCY_PROFILE, CONSENT_RECORD, EMR_LINKAGE_REQUEST, NOTIFICATION, NOTIFICATION_PREFERENCE, HEALTH_METRIC_RECORD, VISIT, PATIENT_CLINICAL_PROFILE, WATCH_FLAG, METRIC_REPORT, REPORT_SYMPTOM, CARE_CASE, CASE_STATUS_HISTORY, STAFF_RESPONSE, GUIDANCE_TEMPLATE, THRESHOLD_RULE, STAFF, PATIENT_ASSIGNMENT, DIARY_ENTRY, DIARY_IMAGE, FAMILY_MESSAGE, CONVERSATION, CHAT_MESSAGE, AI_RESPONSE_LOG.
2. **Records per seed file (272 in total):**

| File | Rows | File | Rows | File | Rows |
|---|---|---|---|---|---|
| 01_STAFF | 7 | 10_NOTIFICATION_PREFERENCE | 10 | 19_HEALTH_METRIC_RECORD | 19 |
| 02_THRESHOLD_RULE | 7 | 11_PATIENT_ASSIGNMENT | 9 | 20_WATCH_FLAG | 8 |
| 03_USER_ACCOUNT | 10 | 12_PATIENT_CLINICAL_PROFILE | 10 | 21_METRIC_REPORT | 11 |
| 04_CONSENT_RECORD | 11 | 13_PREGNANCY_PROFILE | 9 | 22_CARE_CASE | 10 |
| 05_CONVERSATION | 9 | 14_SESSION | 10 | 23_REPORT_SYMPTOM | 16 |
| 06_DIARY_ENTRY | 8 | 15_VISIT | 8 | 24_CASE_STATUS_HISTORY | 22 |
| 07_EMR_LINKAGE_REQUEST | 10 | 16_AI_RESPONSE_LOG | 8 | 25_NOTIFICATION | 9 |
| 08_FAMILY_MESSAGE | 7 | 17_CHAT_MESSAGE | 16 | 26_STAFF_RESPONSE | 8 |
| 09_GUIDANCE_TEMPLATE | 8 | 18_DIARY_IMAGE | 12 | | |

3. **ALR BR-002:** only a report whose value is above threshold creates an "Alert" (S-028); a report with symptoms but no above-threshold value still goes to the nurse queue without being called an Alert, and a Normal report with no symptoms does not notify clinical staff.
4. **First hard rule:** "The repository is the source of truth: build only what `docs/prd.md`, `specs/`, `screens/` and `data/` state; if they disagree or a value is missing, stop and ask — never guess, and never resolve a `[NEEDS CLARIFICATION: …]` or `[PENDING CLIENT: D-xx]` marker yourself."

Pass condition: each member's answer matches this key, and `git status` is still clean afterwards. A difference is recorded in §4 with which agent gave it and what the file says.

## 4. Warnings and disagreements

| # | Found by, date | What | Explanation / action |
|---|---|---|---|
| W1 | Setup machine, 30/09/2026 | T1 WARN: `specify version` cannot start — "An Application Control policy has blocked this file" (Windows Smart App Control blocks the unsigned `specify.exe` shim that uv creates). | Spec Kit v1.0.1 is installed (`uv tool list` → `specify-cli v1.0.1`) and `.specify/` was initialised with it on 24/09/2026. Only the Windows shim is blocked; no Spec Kit command is needed for the Session 7 demo. Before Session 8 (`/speckit-plan`), the owner of this machine allows the file in Windows Security or runs Spec Kit from a teammate's laptop. |
| D1 | Setup machine, 30/09/2026 | T2 would have failed on other laptops: the seed generator wrote the local SQLite version into `data/seed/seed-report.md` ("SQLite 3.45.1" in the package, "3.50.4" on this machine), so `git status` showed a changed file. | Fixed in `generate_seed.py`: the version is no longer written. `--check` now passes on this machine; every member confirms T2 on their own laptop. |
| D2 | Setup machine, 30/09/2026 | The Setup Guide T3 prompt names `docs/spec/spec-document.md`, which does not exist in the Session 4 layout. | Adapted prompt in §3.1; `docs/spec/README.md` points to `specs/`. |
| — | *each member* | *T3 differences between agents / members* | *to fill after each run* |
