# Data model: BOT chat (US-1, US-2)

Data model: **`data/data-model-MB360.md`** (§6), schema `data/schema/schema-MB360.sql`. No field of its own.

| Table | Read / write | Through |
|---|---|---|
| CONVERSATION | write: one per conversation, `current_session_data` = {gestational_week, earlier_turns} | FR-003, D-67 |
| CHAT_MESSAGE | write: the mother's question (`parsed_intent`, `is_risk`) and the Chatbot reply; update `handoff_choice` | FR-001, FR-002, FR-006 – FR-010 |
| AI_RESPONSE_LOG | write: one row per LLM answer | FR-004 |
| CARE_CASE, CASE_STATUS_HISTORY, NOTIFICATION | write on "Connect to nurse" (through ALR FR-021, FR-018) | FR-008 |
| PREGNANCY_PROFILE | read: EDD → gestational week (the only profile value in the context — BR-001) | FR-003 |

Never read by the chatbot: VISIT, HEALTH_METRIC_RECORD, METRIC_REPORT, PATIENT_CLINICAL_PROFILE, WATCH_FLAG (BR-001).
