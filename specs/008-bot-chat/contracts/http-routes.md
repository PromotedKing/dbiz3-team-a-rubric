# HTTP routes: BOT chat (US-1, US-2)

| Method | Path | Screen | Behaviour | Spec |
|---|---|---|---|---|
| GET | `/m/{user_id}/chat` | S-031 | greeting, disclaimer, 4 suggested questions (each sends that question), "Type your question…" + Send | FR-001, BR-004 |
| POST | `/m/{user_id}/chat` | S-032 → S-034 | `text` (≤ 500); starts a conversation; empty / too long → 422; otherwise 303 `/m/{user_id}/chat/{conversation_id}` | FR-001 – FR-007, FR-010, FR-011 |
| GET | `/m/{user_id}/chat/{conversation_id}` | S-034 | the conversation; answer bubbles with the disclaimer; hand-off bubble with buttons (and the notice for a danger phrase); "Sent to a nurse" / hotline after a choice | FR-005, FR-007 – FR-011 |
| POST | `/m/{user_id}/chat/{conversation_id}` | S-034 | a follow-up question in the same conversation | FR-003 |
| POST | `/m/{user_id}/chat/{conversation_id}/handoff/{message_id}` | S-034 | `choice` = connect / decline → 303 back; a second choice → 409 | FR-008, FR-009 |

Home S-008 gets "Health chatbot ›".
