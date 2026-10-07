# DBIZ3 Session 8 build kit

> **This repository:** the Spec Documents live in `specs/spec-<MODULE-ID>.md` (Session 4 layout), not in `docs/spec/`; `tools/start_feature.py` finds them there automatically, and feature folders go next to them (`specs/001-<module>-core/`). The data model is `data/data-model-MB360.md`, the schema `data/schema/schema-MB360.sql`, the seed `data/seed/NN_TABLE.csv` (written by `data/seed/generate_seed.py`). `constitution-starter.md` is kept word for word as the course text; the adopted constitution is `.specify/memory/constitution.md`. This file is the kit's README, moved here so it does not replace the repository README.

Copy these files into the root of your team repository (Workshop Guide, Part 0.5).

- `tools/start_feature.py`: connects a module Spec Document in `docs/spec/` to Spec Kit. Run `uv run tools/start_feature.py <MODULE-ID> --name core`. Also `--check`, `--refresh`, `--use <folder>`.
- `docs/build/constitution-starter.md`: the text to give `/speckit-constitution`.
- `docs/build/build-log.md`: build log template. One entry per agent run.
- `docs/build/mvp-alpha-checklist.md`: the eight MVP Alpha gates. Fill it in before tagging `mvp-alpha`.
- `.github/pull_request_template.md`: the review checklist GitHub shows on every pull request.

Files starting with a dot (`.github`) are hidden in Finder and File Explorer. Copy the folder itself, or use `cp -r` / `Copy-Item -Recurse`.
