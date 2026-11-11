# APT documentation alignment — 11/11/2026

Hải Anh confirms the team follows D-80 and the current app: no Appointments root tab, no Home booking CTA. Part B (booking-session API, adapter and new booking stub flow) is cancelled. D-86 records this confirmation without changing the code or adopting an API proposal.

## Updated sources and downstream documents

| Artifact | Alignment |
|---|---|
| `docs/prd.md` | C1 and backlog keep the read-only card/reminders; the booking entry belongs to TCI. FR-001 is host-only. |
| `specs/spec-APT.md` v1.7.0 | FR-001 and its I/O are host-only / N/A in MB360; BR-001/BR-003, scenarios, scope, screen inventory and historical question references follow D-80. FR-005 describes the existing card, omitted when no appointment exists; FR-009 and S-009 host redirect remain. |
| `docs/decisions.md` D-86 | Records the owner's explicit confirmation; D-80 history is preserved. D-77 / DM-04, external integration questions and S-010 Q3/Q4 stay unchanged. |
| `screens/screen-spec-S-008.md` | Removes the old button requirement, corrects root tabs and destinations, documents no-appointment behavior and cancellation of Part B. |
| Other screen specs with historical Appointments rows | Adds an explicit precedence note: those rows/images describe superseded wireframes. Current root tabs follow D-80; child screens have back navigation without a root tab bar. Unrelated screen behavior and open questions are untouched. |
| `docs/function-list.md`, `docs/screen-list.md` | Traceability no longer requires the old CTA/tab as a current sub-app feature. |
| `docs/architecture/system-configuration.md`, `docs/architecture/usage-flow.md` | Booking entry is in TCI; no Home launcher. Original DBIZ2 flow diagrams remain historical reference. |
| `screens/ui-final/README.md` | U1/U2 historical comparison is followed by the owner's current confirmation. |
| `docs/build/mvp-alpha-checklist.md`, `docs/build/appointment-part-a.md` | Removes the claim that the navigation decision or Part B implementation is still pending. Real TCI integration stays unconfirmed. |

## Files intentionally unchanged

- Application code, tests, data model, schema and seed: no runtime behavior or data change is needed; the current implementation is the behavior the team selected. Part A remains intact.
- `.specify/`, generated skills and read-only `specs/<feature>/spec.md` snapshots: not edited. No APT feature snapshot exists. Existing ACC/CLI snapshots contain historical references to APT, not a current APT implementation contract. Any future snapshot refresh must use the supported tool and receive authorization for its `.specify/feature.json` write; this documentation-only alignment does not run that workflow.
- Original images, PDFs, historical decision entries and build-log entries remain historical evidence. English label-reference rows are a vocabulary catalogue, not proof that the current app renders a booking button.
- `REVIEW_appointment_timeline.md` is the user's untracked file; not edited or staged.

## Validation and review

Existing shell tests: `python -m pytest tests/integration/test_app_shell.py -q` → **18 passed**, one existing TestClient dependency deprecation warning. These cover the five root screens' current tabs, child screens without tabs and the TCI booking stand-in. Documentation diff/Markdown-table checks and preservation of S-010 Q3/Q4 are checked separately. No new tests are needed for this documentation-only change; the prior full Part A run was 480 passed / 2 xfailed.

Shared documents need their listed owners/reviewers (notably Trung for PRD/decisions, Chi/Ánh for screens). The requested decision is recorded as the user's team confirmation, not as a new Client/SME approval. The initial documentation run stopped before committing. Hải Anh subsequently requested publishing these documents on the same branch for review; show status and diff-stat before the commit and push.
