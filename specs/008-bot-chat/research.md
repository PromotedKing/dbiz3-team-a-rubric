# Research: BOT chat (US-1, US-2)

## R1. LLM client (D-76, team decision 26/10/2026)
- **Decision**: `LLMClient.answer(question, context) -> str`. `FakeLLM` returns "[Sample chatbot answer]" (the text used by the seed) and records the last call (for the BR-001 test). `GeminiLLM` posts to the Google AI Studio REST endpoint `models/{GEMINI_MODEL}:generateContent` with the key from `GEMINI_API_KEY`, a system instruction (pregnancy, prenatal care, nutrition, postpartum wellness only; decline anything else; never diagnose; never answer about the mother's own condition) and the conversation context; standard library only, 20 s timeout. `get_client()` reads `.env` at the repository root (a small parser) and returns GeminiLLM only when both settings exist.
- **Rationale**: tests and other laptops work without a key (MVP Alpha G1, G3); the key never enters the repository.

## R2. Classification (FR-006, FR-010, FR-011, BR-002, BR-005)
- **Decision**, in this order, case-insensitive, accents kept: (1) a danger phrase → `needs_nurse` + `danger`; (2) a personal-health marker → `needs_nurse`; (3) no pregnancy-topic word → `out_of_scope`; (4) otherwise `general`. Lists in `bot/keywords.json` (provisional). Only `general` calls the LLM.

## R3. A question (FR-001 – FR-005, FR-007, BR-001, BR-004, D-67)
- **Decision**: text required, ≤ 500 characters (D-46). Store the mother's CHAT_MESSAGE (`parsed_intent` = {"intent": category}, `is_risk` = 1 for needs_nurse), then the Chatbot CHAT_MESSAGE: the LLM answer (general), the decline (out_of_scope), or the hand-off text "This needs a proper consultation. It will be sent to a nurse if you agree" (needs_nurse — the text the seed stores). For a general answer, one AI_RESPONSE_LOG row (`ai_response_data`, `audit_log_entry` = {"client": "fake" | "gemini"}). CONVERSATION.`current_session_data` = {"gestational_week": N, "earlier_turns": k} like the seed. The context given to the LLM = the earlier question / answer pairs of this conversation + the gestational week — nothing from VISIT, HEALTH_METRIC_RECORD, METRIC_REPORT, PATIENT_CLINICAL_PROFILE, WATCH_FLAG (BR-001).

## R4. Hand-off (FR-008, FR-009, D-34)
- **Decision**: on the risk question: `handoff_choice` = Connect to nurse → CARE_CASE (`case_source` Chatbot, `chat_message_id`, Not viewed) + first history row + "created" notification through `alr.cases.open_chatbot_case` (ALR FR-021 c, FR-018); S-034 shows "Sent to a nurse". "No thanks" → no case, hotline shown. A second tap is refused (one choice per question).

## R5. Display (BR-004, FR-011)
- **Decision**: S-031 welcome when no conversation is open; S-034 lists the messages with `dd/mm/yyyy · HH:mm`; every general answer carries "For reference only; does not replace your doctor's advice."; a danger question's hand-off bubble starts with "Signs that need medical attention" (derived from the question, not stored — FR-011); "•••" (S-033) is shown while the form is sending.
