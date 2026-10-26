# Research: ACC onboarding (US-1, US-2)

## R1. Simulated TCI app (§10 Q9 open)
- **Decision**: `GET /tci` = TCI app home (S-001 state 1): one "Mother & Baby 360" tile per seed TCI identity, and a form "Simulate another TCI account" (full name, date of birth, sex, phone, medical record number; the TCI reference is generated). `POST /tci/open` passes the identity as form fields (FR-015 input "TCI identity token" stand-in).
- **Rationale**: the sub-app has no sign-in (D-01) and the identity mechanism is open; login is Session 11.

## R2. Opening the sub-app (FR-015, BR-007, BR-004, BR-006)
- **Decision**: `open_subapp(conn, identity, now)` returns one of:
  - `not_female` — sex ≠ Female: nothing written (BR-007);
  - `consent` — no User Account with this TCI reference yet (first opening): show S-001 state 2;
  - `setup` / `home` — returning mother: refresh the TCI copy (DM-18 default), write a SESSION row, go to S-007 / S-046 when there is no PREGNANCY_PROFILE, otherwise S-008 (BR-006).

## R3. Agreeing (FR-011, FR-015, BR-004)
- **Decision**: `agree(conn, identity, accepted, now)`: refused when the box is unticked (nothing written); otherwise one transaction writes USER_ACCOUNT (copy of the identity, `sex` = Female, `role` = Mother), CONSENT_RECORD (`accepted` = 1, `accepted_at` = now, `terms_version` empty, `tci_data_permission` = 1), NOTIFICATION_PREFERENCE (1, 1, 1, 0 — DM-41 seed defaults) and SESSION (12 h — the ordinary seed sessions; Q9 provisional), then S-104. "Later" writes nothing and returns to `/tci`.

## R4. Onboarding guide S-104 (FR-028)
- **Decision**: 4 pages (`?page=1..4`), "Next", "Skip", "Get started" (last page). "Skip" / "Get started" go to setup or home (FR-003). The guide is reached only from the first agreement, so it is never shown again.

## R5. Pregnancy setup (FR-004, FR-005, D-72)
- **Decision**: one date type (EDD or LMP) with its date is required. EDD from LMP = LMP + 280 days (Q10 provisional). Error when the EDD is before today or the week ((280 − (EDD − today)) // 7) is outside 0 – 42. Height and weight: numbers if given (no range — Q11). First visit date (optional): not after today, not before EDD − 280 days. Save (one transaction): PREGNANCY_PROFILE (`edd`, `lmp`, `edd_source` = Self-entered, `height_cm`, `first_visit_date`); the weight as a HEALTH_METRIC_RECORD (Weight, Group 1, kg, Self-entered, `measured_at` = now, gestational week). The "Calculated by the system" card ("Week N · day D", "Today dd/mm/yyyy · Due dd/mm/yyyy") is shown when the page is reloaded with a valid date (the date field reloads the page on change, like "Change metric" on S-025A).

## R6. Home S-008 (FR-016, FR-017)
- **Decision**: "Hello, {given name}!" (the last word of the full name, as drawn: "Hello, Lan!"), the week card "Week N" + "Due date: dd/mm/yyyy", the "Doctor's instructions" card (active instruction metrics) → S-027, the "My reports" card → S-029.
