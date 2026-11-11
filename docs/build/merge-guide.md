# Approving and merging PRs #15 – #20

Written 07/11/2026 for the merge of the v1.0.0 app into `main` (gate G6 of `docs/build/mvp-alpha-checklist.md`).
Checked on that day at commit `7b31274`: every PR below is mergeable, and merging them in the order below gives no conflict.

## 1. The six pull requests

Four of them are **stacked**: each one is built on the branch of the one before it, so they must be merged in order.

| Order | PR | Branch → base today | What it holds | Suggested reviewer (AGENTS.md §7) |
|---|---|---|---|---|
| 1 | #15 | `sang/tci-ui-shell` → `main` | Mother screens rebuilt from the UI package, Vietnamese labels (D-79, D-80) | Chi (screens), Ánh |
| 2 | #16 | `sang/ui-final-package` → `main` | The 25-screen UI package as a design input (docs only, not stacked) | Ánh |
| 3 | #17 | `sang/009-acc-profile` → `sang/tci-ui-shell` | ACC US-3: profile, notification settings and list | Chi (spec-ACC) |
| 4 | #18 | `sang/010-hlt-history` → `sang/009-acc-profile` | HLT US-3 + US-4: doctor's instructions, metric history | Ánh (spec-HLT) |
| 5 | #19 | `sang/011-tml-journey` → `sang/010-hlt-history` | TML US-4: journey by stage, keepsake album | Tâm (spec-TML) |
| 6 | #20 | `sang/mother-app-v1` → `sang/011-tml-journey` | v1.0.0 app, hosting, chatbot, clinical Overview, Session 11 specs | Tâm, plus each spec owner for their §5.3 / §7.3 |

Rules:
- Sang wrote all six, so **Sang cannot approve them**. GitHub does not count an author's own approval. Any other collaborator can (Tâm, Ánh, Hải Anh, Chi). Trung is not a collaborator on this repository yet; Sang adds Trung under *Settings → Collaborators* if Trung is to review.
- The review written in the shared document on 06/11/2026 does not count for G6. The approval must be on GitHub.
- Never push to `main` directly (AGENTS.md rule 5).

### Who approves which part of #20

#20 is large (about 6,400 lines in 140 files). It is not split, because its parts depend on each other (the hosted app
needs the v1.0.0 screens, the chatbot change needs the hosting settings), but each part has its owner (AGENTS.md §7).
GitHub counts one approval; the others confirm their part in a comment on #20.

| Part of #20 | Files | Owner who confirms |
|---|---|---|
| Mother app screens and flow (D-81) | `app/mb360/templates/`, `app/mb360/static/`, `app/mb360/acc/`, `hlt/`, `tml/`, `alr/` | Chi (screens), Ánh |
| Hosting and team password (D-82) | `render.yaml`, `app/mb360/server.py`, `gate.py`, `serial.py`, `docs/build/adr-hosting.md` | Trung |
| Chatbot on Groq / Gemini (D-83, D-84) | `app/mb360/bot/`, `spec-BOT.md` | Sang owns spec-BOT, so Chi (its reviewer) confirms |
| Clinical Overview and Case board (D-85) | `app/mb360/cli/dashboard.py`, `staff_*.html`, `spec-CLI.md` | Trung |
| Schema: three `json_valid` checks allow NULL | `data/schema/schema-MB360.sql`, `data/data-model-MB360.md` | Tâm (reviewer: Trung) |
| Decisions D-81 – D-85 | `docs/decisions.md` | Trung (reviewer: Chi) |
| Spec updates (§5.3 EARS, §7.3, answered questions) and 18 screen specs | `specs/spec-*.md`, `specs/0*/spec.md` (copies), `screens/screen-spec-*.md` | each spec owner for their file; the copies follow the spec |
| Labels | `docs/ui-label-reference.md` | Chi (reviewer: Ánh) |

## 2. Approving (reviewer)

1. Open the PR on GitHub, tab **Files changed**. For #20 (142 files), read at least `docs/build/mother-app-v1.md` and your own spec's §5.3 and §7.3 and the questions marked "Resolved 07/11/2026" in its §10.
2. Optional but useful: run it yourself.
   ```bash
   git fetch origin
   git switch sang/mother-app-v1
   uv sync
   uv run python -m pytest
   uv run python -m uvicorn mb360.server:app --app-dir app
   ```
   Expected: `465 passed, 2 xfailed`, the app at http://127.0.0.1:8000.
3. Click **Review changes** (top right of *Files changed*):
   - **Approve** if it is fine. Write one line on what you checked, for example "Checked spec-ACC §5.3 and S-103 on the app".
   - **Comment** for remarks that do not block the merge.
   - **Request changes** if something must be fixed first. Write what and where; Sang fixes it on the same branch.
4. Click **Submit review**.

Same thing from the command line: `gh pr review 17 --approve --body "Checked spec-ACC §5.3 and S-103 on the app"`.

A stacked PR (#17 – #20) shows only its own changes while its base is the previous branch. That is the right view to review it in, so it can be approved before the earlier ones are merged.

## 3. Merging (Sang, after the approvals)

Merge **one at a time, in the order of section 1**. For every PR:

- Use **Create a merge commit**. Do **not** use *Squash and merge* or *Rebase and merge*: the later branches contain the original commits, and a squash or rebase on `main` would make them show those changes again or conflict.
- After merging, **do not click "Delete branch"**. `sang/mother-app-v1` must stay: Render deploys from it (`render.yaml`).

Steps:

1. **#15**: wait for the approval → **Merge pull request** → *Create a merge commit* → **Confirm merge**.
2. **#16**: same.
3. **#17**: its base is still `sang/tci-ui-shell`. Click **Edit** next to the PR title, change *base* to `main`, confirm. Check that *Files changed* now shows only #17's 22 files (if it shows #15's files too, #15 is not merged yet: stop). Then merge as in step 1.
4. **#18**, **#19**, **#20**: same as #17, one after the other. Change the base to `main` only **after** the previous PR is merged.

Same thing from the command line, in this order:

```bash
gh pr merge 15 --merge
gh pr merge 16 --merge
gh pr edit 17 --base main
gh pr merge 17 --merge
gh pr edit 18 --base main
gh pr merge 18 --merge
gh pr edit 19 --base main
gh pr merge 19 --merge
gh pr edit 20 --base main
gh pr merge 20 --merge
```

If GitHub shows **"This branch has conflicts"** after changing a base: stop and tell Sang. Do not resolve it in the browser.

PRs #2 and #3 (Chi's and Ánh's spec clarifications) are not part of this chain; leave them as they are.

## 4. After the merge

1. On `main`, two members run a fresh clone (one Windows, one macOS), as in gate G1:
   ```bash
   git clone https://github.com/PromotedKing/dbiz3-team-a-rubric.git
   cd dbiz3-team-a-rubric
   uv sync
   uv run tools/start_feature.py --use specs/011-tml-journey
   uv run data/seed/generate_seed.py --check
   uv run python -m pytest
   ```
2. Sang ticks G1 and G6 in `docs/build/mvp-alpha-checklist.md` with the commit of `main` and the reviewers' names, in a new PR (reviewed by someone else).
3. Optional: point Render at `main` by changing `branch: sang/mother-app-v1` to `branch: main` in `render.yaml`, in a PR. Until then the hosted app keeps following `sang/mother-app-v1`.
4. The `mvp-alpha` tag is put on `main` only when every gate is ticked. A tag is never moved afterwards (AGENTS.md rule 5).

**What happened (10/11/2026):** #17 – #20 were merged while their base was still the previous branch, so none of them reached `main`. PR #21 (`sang/mother-app-v1` → `main`) brought them in; `main` now has everything of #15 – #20. `render.yaml` points at `main` from `sang/render-main`.
