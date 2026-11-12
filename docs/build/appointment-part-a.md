# Appointment demo — Part A / draft PR notes

Hải Anh, branch `haianh/appointment-book-cta`, based on `origin/main` (`1c087c7`). Part B and booking-session API work are excluded from this change.

## Base branch and Render

GitHub deployment 7650429879 succeeded on 09/11/2026 for `sang/mother-app-v1` at `346dd93`. `main` contains that commit and is five commits ahead; application code, tests and `render.yaml` have no differences between those refs. Therefore this work starts from `main`. The Blueprint still follows `sang/mother-app-v1`: merging into main alone will not deploy this change until the team updates the Render source. This PR does not change deployment configuration.

## Changes and cause of the empty filter

The Mai persona creates Report / Visit result notices but no Appointment notice. The tab badge counts all unread types, while the filter correctly selects exactly `type='Appointment'` for the selected mother. The base CSV seed already has an Appointment notice for U01; it does not belong to Mai. Thus the observed badge and empty Appointment filter are consistent; there is no filter type mismatch to fix.

The generator writes a relative host fixture for two retained seed mothers. U11 has a 09:00 appointment tomorrow and receives one unread Appointment notice; U04 (Phạm Ngọc Mai) has no appointment and keeps her stored EDD. Host demo installation reads the generated fixture, restores a missing An Nhiên account in an older local DB and preserves existing state. Notifications use stable UUIDs per mother/appointment time, so repeat checks do not duplicate them or reset `read_at`.

## Assumptions requiring review

- **Q4 cần nhóm trưởng/sản phẩm xác nhận**: for demo/test only, disabling reminders stops new notifications and keeps received notices on S-009. The S-010 §9 Q4 marker remains unchanged and unresolved.
- Reminding one calendar day before the visit is a demo assumption only; S-010 Q3 and the corresponding spec-APT marker remain unresolved. No production scheduling or TCI push delivery is claimed.
- Tomorrow is relative to the first host-fixture installation date, using the existing Vietnam clock. At startup on 10/11/2026 the visit is 11/11/2026 09:00. Reopening an existing DB preserves the visit rather than silently moving it. After that date, use a fresh demo/reset to recreate the tomorrow case. CSVs and generated JSON remain deterministic, independent of today's date.
- The generator writes 26 CSVs / 141 rows plus the report and host JSON. The app builds SQLite and installs host fixtures at runtime, not during Render build. Render free storage is ephemeral: a new deployment recreates these fixtures; user actions are not durable across fresh deployments. A local existing DB can restore missing fixture rows, without resetting switches or received notices.
- The no-appointment case currently has no `data-appointment` card, matching existing Home behavior. Part B is cancelled by the user on 11/11/2026 (D-86); no empty-card booking CTA or other booking launcher will be added.

## Traceability and files

| Request | Screen | Implementation / fixture | Verification |
|---|---|---|---|
| A1/A2: tomorrow, unread notice, default switch, account access | S-008, S-009, S-010; `/tci/accounts` | `data/seed/generate_seed.py`, four regenerated CSVs, `appointment-demo.json`, `app/mb360/appointment_demo.py`; hooks in `main.py`, `persona.py`, `acc/routes.py` | `test_accounts_open_home_with_tomorrow_card_and_no_appointment_case`, `test_appointment_filter_read_and_host_redirect` |
| A3/A4: relative dates, repeatability, redeploy | simulated TCI host | generated offsets, idempotent host installation | `test_fresh_deploy_uses_relative_dates_and_never_creates_appointment_table`, `test_existing_demo_database_upgrade_and_reopen_are_idempotent`; generator `--check` |
| A5: no appointment | S-008 | U04 / host fixture | account/Home test above; no notice generated |
| A6: off/on controls new delivery, keeps received notices | S-009 / S-010 | `create_reminders`, existing notification toggle route | `test_switch_off_stops_new_reminders_but_keeps_received_notices` |
| DM-04: no MB360 appointment table | external | schema unchanged | fresh-deploy table assertion, `test_plain_seed_has_no_host_appointments` |

Supporting files: `data/data-model-MB360.md` updates seed counts and explains the fixture boundary; `data/seed/README.md` documents generation; generated `seed-report.md` records the new rows. Existing `tests/seed/test_seed_acc.py` and `tests/seed/test_seed_load.py` now expect 4 accounts / 141 rows. Screen specs S-008/S-009/S-010 contain demo notes without resolving open questions. `docs/build/build-log.md` records this agent run.

Read-only `.specify/` review: no Appointment / Appointments / appointment_reminder / 272 references were found in Markdown there. Nothing changed in `.specify/`, snapshot specs or generated skills. This Part A entry originally deferred navigation alignment; on 11/11/2026 the user cancelled Part B and confirmed D-80 navigation in D-86. The documentation alignment is recorded separately in `docs/build/apt-navigation-alignment.md`.

## Manual test

1. Start the demo with `python -m uvicorn mb360.server:app --app-dir app`. Open `/tci/accounts` through the existing demo access gate.
2. Choose `tci-000133` (Nguyễn Thị An Nhiên). Home opens directly; check tomorrow at 09:00 and “Còn 1 ngày”.
3. Open “Từ bác sĩ”, filter “Lịch hẹn”. Check the unread reminder for tomorrow; tap it, confirm `/tci/booking`, return to S-009 and confirm it is read.
4. On S-010 switch “Nhắc lịch khám” off and back on; reload to confirm it persists. Existing reminders remain visible. The automated test simulates a new external appointment to verify that off blocks a new reminder and on permits it.
5. Choose `tci-000126` (Phạm Ngọc Mai). Check Home opens with no appointment card and the Appointment filter has no notices.
6. Reopen the same DB to check no duplicate notices/read-state reset. Use a fresh deploy/DB or the existing demo reset to recreate the next-day scenario; reset clears demo user actions.

## Validation

Validation completed on 11/11/2026 using the existing `.venv/Scripts/python.exe`:

- Focused appointment demo tests: **8 passed**.
- Full `python -m pytest tests -q`: **480 passed, 2 xfailed**, 1 TestClient dependency deprecation warning, 45.30 s. The xfails remain expected failures; no dependency was added/upgraded.
- Generator executed, then `generate_seed.py --check`: **OK**, 26 tables / 141 rows, 28 generated files identical to a fresh run.
- `tools/check_data_model.py`: **OK**, 175 columns / 40 relationships; all 26 CSVs load with valid foreign keys.
- `git diff --check`: passed.

`uv run` failed because its sandbox interpreter cache was unwritable; direct execution of the existing virtualenv worked. TestClient HTTP tests stalled inside the sandbox and passed with execution escalation. No manual browser/Render deployment validation was performed. Show status, diff and diff-stat before the Part A commit requested by Hải Anh: `feat(apt): add appointment reminder demo cases`. Stop after Part A; no push or Part B before approval.
