# Data model: ACC profile

No new table or column; `data/` is unchanged.

| Entity | Read | Written |
|---|---|---|
| USER_ACCOUNT | full name, phone, medical record number | — (TCI account, BR-002) |
| PREGNANCY_PROFILE | due date, LMP, source, height | `height_cm`; `edd` and `lmp` only when not linked |
| EMR_LINKAGE_REQUEST | status, record code, facility, dates | — (seed, ACC-01) |
| CONSENT_RECORD | latest `accepted` | — |
| WATCH_FLAG | active metrics | — |
| NOTIFICATION_PREFERENCE | 4 switches | `new_visit_result`, `watch_flag_reminder`, `updated_at` |
| NOTIFICATION | list, unread count | `read_at` |
