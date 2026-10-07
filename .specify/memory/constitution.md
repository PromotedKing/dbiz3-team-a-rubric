# Mother & Baby 360° Constitution

Project: Mother & Baby 360°, team Group A, DBIZ3 VJCBI College - FTU.

The five principles below are the DBIZ3 course convention (`docs/build/constitution-starter.md`), kept word for word except one adaptation to this repository's layout, marked *(layout)*: the Spec Documents live in `specs/spec-<MODULE-ID>.md`, not in `docs/spec/`. Technology choices are not part of the constitution; they belong in `plan.md`.

## Core Principles

### I. The spec is the source of truth

Requirements come only from `specs/spec-<MODULE-ID>.md` *(layout)*. Data structures come only from `data/` (Session 5 data model, schema and seed). If code and spec disagree, the code is wrong until the spec is changed by a human in `specs/spec-<MODULE-ID>.md` *(layout)*. Never invent a requirement; mark it [NEEDS CLARIFICATION] and stop.

### II. Business rules are test-first (non-negotiable)

Every business rule (BR-xxx) and every acceptance scenario of the slice being built gets an automated test that is written and seen failing before the code that makes it pass.

### III. Thin vertical slices

Build one user story at a time, end to end (screen, logic, data), in priority order P1, P2, P3. A slice is done only when its tests pass and it runs from a clean clone with the commands in quickstart.md.

### IV. Synthetic data and no secrets

Only the seed data generated in `data/` is used. No real personal data, no API keys or passwords in any committed file; secrets live in `.env`.

### V. Humans approve every change

The agent works on a branch, shows the changed files with a reason for each, and never pushes or merges. A teammate reviews every pull request before merge.

## Governance

Amend only by pull request reviewed by two members; bump the version (MAJOR when a principle is removed or redefined, MINOR when one is added, PATCH for wording). Technology choices are NOT part of the constitution; they belong in plan.md.

**Version**: 2.0.0 | **Ratified**: 2026-09-30 | **Last Amended**: 2026-10-07 (replaced by the five DBIZ3 Session 8 principles)
