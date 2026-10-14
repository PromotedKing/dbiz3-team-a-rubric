# Mother & Baby 360° — Group A (DBIZ3)

Maternity remote-monitoring sub-app for Thu Cuc Hospital, embedded in the hospital's patient app (TCI app). The mother reviews visit data, reports doctor-flagged metrics or symptoms, keeps a pregnancy timeline and diary, and asks an AI chatbot; nurses and doctors triage and follow up her reports on a clinical web.

Agents: read [`AGENTS.md`](AGENTS.md) first.

## The chain, in order of dependency (Session 7 rubric §3.1)

| # | Artefact | Where | Notes |
|---|---|---|---|
| 1 | PRD | `docs/prd.md` | MVP Scope v8 refined on 14/10/2026, with item IDs (M1 – M5, S1 – S2, C1, W1 – W4), the Must → module map (§7) and the scope changes with reasons (§8) |
| 2 | Spec Documents | `specs/spec-ACC.md`, `spec-HLT.md`, `spec-ALR.md`, `spec-CLI.md`, `spec-TML.md`, `spec-BOT.md`, `spec-APT.md` | Session 4 layout; Won't rows kept for traceability. `docs/spec/README.md` points here |
| 3 | Screen Specs and mockups | `screens/screen-spec-S-xxx.md`, `screens/img/S-xxx.png` | 30 specs, 27 images. S-104 and S-105 (new, D-74, D-75) have no image yet; 7 images are older than their spec and must be redrawn: S-001, S-007 / S-046, S-008, S-025A, S-034, S-048, S-064 (see `docs/decisions.md`, Open items) |
| 4 | Data model with Mermaid ERD | `data/data-model-MB360.md` | One model for the 7 modules (MODULE-ID MB360); §5 diagram check, §11 privacy declaration |
| 5 | Schema | `data/schema/schema-MB360.sql` | SQLite 3 |
| 6 | Seed files, generator, README | `data/seed/` | 26 CSV files named `NN_TABLE.csv`, loaded in filename order; `seed-report.md` holds the edge-case register |
| 7 | Agent contract | `AGENTS.md` | Hard rules, seed command, file owners (§7) |
| 8 | Spec Kit and Antigravity rule | `.specify/` (v1.0.1, constitution in `.specify/memory/constitution.md`), `.agents/rules/project-context.md`, `.agents/skills/`, `.claude/skills/` | Generated files: do not edit |
| 9 | Environment Readiness Report | `docs/env/readiness-report.md` | One row per member; T3 prompt and answer key |
| 10 | AI use log | `docs/ai-use-log.md` | One row per AI-drafted artefact |

Supporting documents: `docs/decisions.md` (decision log D-01 – D-78, open items, module scope), `docs/ui-label-reference.md` (UI conventions, English ↔ on-screen text), `docs/function-list.md`, `docs/screen-list.md`, `docs/architecture/`, `docs/data-model-freeze-worksheet.md` (7 structural questions for the team). Tools: `tools/check_env.py` (T1), `tools/check_data_model.py` (data model §5 and gate G3).

## Commands (from the repository root)

```bash
uv run tools/check_env.py --repo              # T1 (Path A: add --path A)
uv run data/seed/generate_seed.py             # seed command: checks the rules, loads schema + seed in memory, writes the CSV files (T2: git status stays clean)
uv run data/seed/generate_seed.py --check     # same checks, writes nothing
uv run tools/check_data_model.py              # diagram check (data model §5) and seed load in filename order
```

Python 3.8 or later for the data scripts, 3.11 or later for `check_env.py`; standard library only. Without uv: `python3 …` (Windows: `python …`).

## Markers used in the documents

`[NEEDS CLARIFICATION: …]` = information missing, with its owner in §10 of the spec; `[PENDING CLIENT: D-xx]` = designed, waiting for the Client; `DM-xx` = open question from the data model (§10 of the owning spec and §12.3 of the data model).
