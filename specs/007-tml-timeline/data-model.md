# Data model: TML timeline (US-1, US-2)

Data model: **`data/data-model-MB360.md`** (§6), schema `data/schema/schema-MB360.sql`. No field of its own.

| Table | Read / write | Through |
|---|---|---|
| PREGNANCY_PROFILE | read: EDD → weeks | FR-003, FR-006 |
| VISIT | read: visit cards | FR-005, BR-001, BR-003 |
| HEALTH_METRIC_RECORD | read: daily indicators | FR-012, BR-008 |
| DIARY_ENTRY | read: the week's entries; write: new entry (`text`, `mood`, `gestational_week` = current week, `entry_date` = today) | FR-003, FR-008 – FR-010, BR-002, BR-005 |
| DIARY_IMAGE | read: first photo; write: 0 – 5 rows (`file` = media path, `sort_order`) | FR-009 |
| FAMILY_MESSAGE | read only (US-3 pending Client) | FR-003 |

Not stored: Pregnancy Week Content (derived), the photo files themselves (in the git-ignored `media/` folder).
