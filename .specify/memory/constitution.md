# Mother & Baby 360° Constitution

The principles below govern every Spec Kit step (specify, clarify, plan, tasks, implement) in this repository. `AGENTS.md` holds the day-to-day rules for agents; this constitution is what a plan or a pull request is checked against.

## Core Principles

### I. Spec-first, chain-consistent

Nothing is built that is not traced to the chain PRD (`docs/prd.md`) → FR in `specs/spec-{MODULE-ID}.md` → §5.1 fields → entity in `data/data-model-MB360.md` → schema → seed row → screen in `screens/`. Every task names the FR IDs it delivers. A change to an upstream document updates the downstream documents in the same pull request, in dependency order.

### II. No guessing

An open point stays marked `[NEEDS CLARIFICATION: …]` with its owner, or `[PENDING CLIENT: D-xx]`, until a human decides it and the decision is written in `docs/decisions.md`. Neither a member nor an agent fills a gap with an invented value, threshold, text or rule.

### III. Clinical safety over convenience

Thresholds come only from THRESHOLD_RULE; "Alert" is used only for an above-threshold report; a report with a symptom always reaches a nurse; the chatbot never diagnoses and never sends the medical record; case status only moves forward. Every business rule in §5.2 of the specs has a named place where it is enforced (`data/data-model-MB360.md` §8) and a test.

### IV. Test-first from the acceptance scenarios (NON-NEGOTIABLE)

Each acceptance scenario in §3 of a spec becomes an automated test before the code that satisfies it. The seed data (`data/seed/`) is the shared test fixture: it is generated, never hand-edited, and `uv run data/seed/generate_seed.py` must leave `git status` clean.

### V. Privacy and secrets

Only invented data is committed (data model §11). No `.env` file, key, password or token enters the repository or its history. Patient data shown to staff is limited to what the spec's §5.1 contract lists.

## Constraints

- The MVP is a sub-app of the TCI app: identity comes from the host app (no sign-up, OTP or password in the sub-app, D-01); appointments are a redirect to the host app (APT-01); visit data is seed data, with no HIS/EMR integration (D-59).
- The application stack is chosen at the Plan step and recorded in the plan with its reason; it must run on the members' Windows and macOS laptops.
- Spec Kit stays on v1.0.1 for the whole team; generated files are not edited.

## Development Workflow

- One topic per branch, named `member-name/short-topic`, finished within one or two days; pull request reviewed by the file owner listed in `AGENTS.md` §7.
- Before a commit, the member reads `git diff`. Before a merge: `uv run tools/check_env.py --repo`, `uv run tools/check_data_model.py` and the test suite pass.
- Every artefact an AI tool drafted or changed gets a row in `docs/ai-use-log.md` naming the member who checked it and how.

## Governance

This constitution overrides other practices in the repository. An amendment is a pull request that states the reason, is approved by at least two members including the owner of `AGENTS.md`, and bumps the version below (MAJOR: a principle removed or redefined; MINOR: a principle or section added; PATCH: wording). Plans and pull requests are checked against Principles I – V.

**Version**: 1.0.0 | **Ratified**: 2026-09-30 | **Last Amended**: 2026-09-30
