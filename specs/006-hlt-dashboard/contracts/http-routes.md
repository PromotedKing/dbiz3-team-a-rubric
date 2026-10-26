# HTTP routes: HLT dashboard (US-1, US-2)

| Method | Path | Screen | Behaviour | Spec |
|---|---|---|---|---|
| GET | `/m/{user_id}/health?refreshed=&saved=` | S-023 | 3 sections; "Data updated." after Refresh; "Metrics saved" after S-024 | FR-001 – FR-005, FR-008 |
| GET | `/m/{user_id}/self-tracked` | S-024 | 4 group 1 metrics, "Measured at" prefilled with now, sleep as bedtime / wake-up | FR-007 |
| POST | `/m/{user_id}/self-tracked` | S-024 | fields `weight`, `weight_at`, `temperature`, `temperature_at`, `heart_rate`, `heart_rate_at`, `bedtime`, `wakeup`; invalid → 422 with field errors, nothing saved; valid → 303 `/m/{user_id}/health?saved=1` | FR-007, BR-003 |

S-008 Home gets a "Health metrics ›" link to S-023.
