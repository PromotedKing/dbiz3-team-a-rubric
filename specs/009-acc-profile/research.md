# Research: ACC profile

**R1. Hospital link.** The latest EMR_LINKAGE_REQUEST row by `requested_at` gives the status (seed data, ACC-01). `Linked` makes the due date read-only (BR-003, S-011 SR-002).

**R2. Editing.** S-011 posts `edd` (ignored when linked) and `height_cm`. The due-date rule is the one of `acc/setup.py` (`validate` with `date_type = EDD`): not in the past, week 0 – 42. A height must be a number or empty; no range (D-16).

**R3. Notification targets (S-009 SR-001).** Report with a case → S-026 (`/reports/{id}`, or `/cases/{id}` for a chatbot case). Report without a case → S-029. Visit result → S-023. Instruction reminder → S-027 (proposed, S-009 §5 #7a). Appointment → the simulated TCI booking page.

**R4. Stored text.** Notification titles are stored in English by ALR FR-018 and by the seed. They are shown through `ui.t_known`, which now also reads `{field}` rows; text that is not a label (seed sample text) is shown as stored and is not a missing label.

**R5. Switches.** One POST per toggle with the column and the value; only `new_visit_result` and `watch_flag_reminder` are accepted (allow-list), `updated_at` is set. A mother with no preference row gets the defaults of ACC Q22 (a) first.

**R6. Reading on GET.** Opening a notification is a link that marks it read and redirects. It is idempotent: the first `read_at` is kept (ACC §5.1 FR-026).
