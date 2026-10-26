# HTTP routes: ACC onboarding (US-1, US-2)

| Method | Path | Screen | Behaviour | Spec |
|---|---|---|---|---|
| GET | `/tci` | S-001 state 1 (simulated TCI app) | "Mother & Baby 360" tile per seed TCI account + form to simulate another TCI account | R1 |
| POST | `/tci/open` | S-001 | identity fields → notice (not female, 200), consent sheet (first opening, 200), or 303 to setup / home (returning) | FR-015, BR-004, BR-006, BR-007 |
| POST | `/tci/consent` | S-001 state 2 | `action` = agree / later, `agree` checkbox, identity fields. Later → 303 `/tci`; unticked → 422 sheet with the error at the checkbox; agree → 303 `/m/{user_id}/guide` | FR-011, FR-015, BR-004 |
| GET | `/m/{user_id}/guide?page=` | S-104 | pages 1 – 4, Next, Skip, Get started | FR-028 |
| GET | `/m/{user_id}/guide/done` | — | 303 to setup (no due date) or home | FR-003, BR-006 |
| GET | `/m/{user_id}/setup?date_type=&date=` | S-007 / S-046 | form; "Calculated by the system" card when a valid date is given; 303 home when a profile exists | FR-004, BR-006 |
| POST | `/m/{user_id}/setup` | S-007 / S-046 | fields `date_type` (EDD / LMP), `date`, `height_cm`, `weight_kg`, `first_visit_date`; invalid → 422 with field errors; valid → save, 303 home | FR-004, FR-005, D-72 |
| GET | `/m/{user_id}/home` | S-008 (minimal) | greeting, week card, Doctor's instructions card, My reports card; 303 setup when there is no due date | FR-016, FR-017, BR-006 |
