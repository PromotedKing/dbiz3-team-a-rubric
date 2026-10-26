# Tasks: BOT chat — health chatbot with hand-off to a nurse

**Input**: `specs/008-bot-chat/` — plan.md, spec.md (US-1, US-2), research.md, data-model.md, contracts/http-routes.md, quickstart.md

**Tests**: required by the constitution; each test task comes before the code it checks. **No test calls the network or needs a key.**

**Out of scope**: answer rating (S-037, BOT-02), voice input (BOT-01), the real Gemini call (tried by hand when a member has a key).

## Phase 1: Setup

- [X] T001 Create `app/mb360/bot/__init__.py` and `.env.example` (setting names only); confirm `.env` is git-ignored; no new dependency

## Phase 2: Foundational

- [X] T002 [P] Seed test in `tests/seed/test_seed_bot.py` (checked with queries): 9 CONVERSATION, 16 CHAT_MESSAGE, 8 AI_RESPONSE_LOG rows; every non-empty `current_session_data` has `gestational_week` and `earlier_turns` (one conversation leaves it empty — optional column); the two chatbot cases point to a risk question (`is_risk` 1, `handoff_choice` Connect to nurse); Ngô Thị Thảo (U09) has no conversation
- [X] T003 [P] `tests/unit/test_bot_llm.py` — **R1**: without `GEMINI_API_KEY` / `GEMINI_MODEL` `get_client()` returns the fake client; with both (set in the test environment, no call made) it returns the Gemini client; the fake client answers "[Sample chatbot answer]" and records its last input

## Phase 3: US-1 + US-2 (P1) 🎯

### Tests (write first, see them fail)

- [X] T004 [P] [US1] `tests/unit/test_bot_classify.py` — **FR-006, FR-010, FR-011, BR-002, BR-005**: "How can I eat beef safely during pregnancy?" → general; "I have had a little bleeding since this morning, is that okay?" → needs_nurse + danger; "Tôi bị chảy máu" → needs_nurse + danger; "không thấy thai máy" → danger; "I feel tired, is that normal?" → needs_nurse, not danger; "How do I change a car tyre?" → out_of_scope; adding a phrase to the keyword file changes the result (not hard-coded)
- [X] T005 [P] [US1] `tests/unit/test_bot_chat.py` — **FR-001 – FR-004, FR-007 – FR-010, BR-001, D-34, D-67**: a general question stores the question (`is_risk` 0, intent general), the answer, 1 AI_RESPONSE_LOG row and `current_session_data` {gestational_week 20, earlier_turns 0}; a follow-up in the same conversation sends the earlier pair and the week to the LLM and **nothing else** (no visit value, no metric, no report text, no blood type in the recorded input); a risk question does not call the LLM, stores `is_risk` 1 and the hand-off text, **no case**; connect → `handoff_choice` Connect to nurse + one Chatbot CARE_CASE Not viewed + history (System) + a Report notification; decline → No thanks, no case; a second choice → refused; out-of-scope → decline text, no LLM call, no case; text of 501 characters or empty → refused, nothing stored
- [X] T006 [P] [US2] `tests/integration/test_bot_pages.py` — **US-1 #1, #3, #4, US-2 #1 – #4, BR-004**: Home links to S-031; S-031 shows "Hello, Mom!", "I can answer general questions about pregnancy and baby care.", the disclaimer, the 4 suggested questions, "Type your question…", "Send"; POST a general question → 303 to S-034 with the answer and "For reference only; does not replace your doctor's advice."; POST a danger question → "Signs that need medical attention", "This needs a proper consultation.", "Connect to nurse", "No, thanks", "If you have any emergency signs, call 1900 xxxx."; connect → "Sent to a nurse" and the nurse queue on `/staff` lists a Chatbot case whose S-064 shows the conversation; a non-danger personal question has the offer without the notice; decline → hotline, no case; out-of-scope → the decline text and no buttons; the word "alert" never appears on S-031 / S-034

### Implementation

- [ ] T007 [US1] `app/mb360/bot/llm.py` (R1) — makes T003 pass
- [ ] T008 [P] [US1] `app/mb360/bot/classify.py` + `bot/keywords.json` (R2) — makes T004 pass
- [ ] T009 [US1] `app/mb360/bot/chat.py` + `alr.cases.open_chatbot_case` (R3, R4) — makes T005 pass
- [ ] T010 [US1] `app/mb360/bot/routes.py` + register in `main.py`; template `chat.html`; "Health chatbot ›" on Home — makes T006 pass

## Phase 4: Polish

- [ ] T011 Walk quickstart.md scenarios 1 – 6 with the fake LLM
- [ ] T012 [P] Build log entries; note that the Gemini client is untested until a member adds a key

## Dependencies

Phase 1 → 2 → 3 → 4. T003 → T007; T004 → T008; T005 → T009; T006 → T010.
