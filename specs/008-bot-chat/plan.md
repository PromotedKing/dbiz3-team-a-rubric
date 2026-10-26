# Implementation Plan: BOT chat — health chatbot with hand-off to a nurse

**Branch**: `sang/008-bot-chat` (based on `sang/007-tml-timeline`, PR #13) | **Date**: 2026-10-26 | **Spec**: [spec.md](spec.md) (snapshot of `specs/spec-BOT.md` v1.8.0)

**Input**: Feature specification from `specs/008-bot-chat/spec.md`

## Summary

Build BOT **US-1 (P1)** "Ask a common maternity question" and **US-2 (P1)** "Get routed to a human when it matters": S-031 welcome (greeting, disclaimer, 4 suggested questions), S-032 – S-034 conversation (question, "•••", answer with disclaimer), classification of each question (FR-006): general → LLM answer; personal health or danger phrase → no answer, hand-off offer (FR-007) with the notice "Signs that need medical attention" for a danger phrase (FR-011); outside pregnancy topics → polite decline (FR-010). "Connect to nurse" creates a Chatbot case in the nurse queue (FR-008, ALR FR-021); "No, thanks" shows the hotline (FR-009). Team decision 26/10/2026 (Sang): **an LLM client interface with a fake client by default; the Google AI Studio (Gemini) client is used only when a key is present in the local `.env`** (D-76).

## Technical Context

**Language/Version**: Python 3.11+ (uv) — unchanged · **Primary Dependencies**: unchanged — the Gemini client uses the standard library (`urllib`), no SDK package · **Storage**: SQLite from schema + seed (unchanged) · **Testing**: pytest with the fake LLM only (no network, no key) · **Target Platform**: local laptop · **Project Type**: web application (same project) · **Constraints**: the medical record is never sent to the LLM (BR-001); no diagnosis, risk questions never answered (BR-002); the API key lives only in `.env` (git-ignored, constitution IV); "Alert" never used by the chatbot (D-22) · **Scale/Scope**: S-031, S-032 – S-034

## Constitution Check

| Principle | How this plan complies | Status |
|---|---|---|
| I. The spec is the source of truth | BOT US-1 #1, #3, #4, US-2 #1 – #4, FR-001 – FR-011, BR-001 – BR-005; screen specs S-031, S-034. Open points kept open: risk keywords (Q2, D-47 Pending SME), borderline classification (Q12), hotline number (Q8), decline wording (Q13), error text / timeout (Q10), repeated questions (Q11) | PASS |
| II. Business rules are test-first | Tests for BR-001 (payload sent to the LLM), BR-002, BR-004, BR-005, FR-006 – FR-011 and every scenario, written and seen failing first | PASS |
| III. Thin vertical slices | Two P1 stories on one conversation screen | PASS |
| IV. Synthetic data and no secrets | No key in any committed file; `.env` git-ignored; tests never call the network | PASS |
| V. Humans approve every change | Branch + pull request reviewed by a member who did not write it (Chi reviews BOT) | PASS |

## Project Structure

```text
specs/008-bot-chat/  spec.md, plan.md, research.md, data-model.md, quickstart.md, contracts/http-routes.md, tasks.md
app/mb360/bot/
├── __init__.py
├── llm.py              # LLMClient: FakeLLM (default), GeminiLLM (only with GEMINI_API_KEY + GEMINI_MODEL in .env)
├── classify.py         # FR-006, FR-010, FR-011: general / needs_nurse (+ danger) / out_of_scope
├── keywords.json       # D-47 danger phrases, personal-health markers, pregnancy topics — provisional, Pending SME
├── chat.py             # FR-001 – FR-005, FR-007 – FR-009, BR-001: store messages, context, log, hand-off
└── routes.py
app/mb360/alr/cases.py  # + open_chatbot_case (ALR FR-021 c)
app/mb360/templates/    chat.html (S-031 / S-032 – S-034)
.env.example            # names of the two settings, no value
tests/unit/test_bot_classify.py, test_bot_chat.py
tests/integration/test_bot_pages.py
```

## Complexity Tracking

| Item | Why it matters | What the plan does until it is answered |
|---|---|---|
| BOT Q2 / D-47 — danger phrases (Pending SME) | FR-006, FR-011 | The team list (D-47 groups + PRD M5 examples, English and Vietnamese) in `bot/keywords.json`, marked provisional; changing the file changes the behaviour (tested) |
| BOT Q12 — how a "personal health" question is recognised | FR-006 | A provisional list of first-person health markers ("I have", "I feel", "tôi bị", "em bị", "is that normal", "có sao không" …) in the same file; when unsure the chatbot routes to a nurse rather than answers (safer side of BR-002) |
| FR-010 with the fake LLM | Deciding "outside pregnancy topics" normally belongs to the LLM's system prompt | The code first checks the provisional pregnancy-topic words; a question with none of them is declined without calling the LLM. With Gemini, the system prompt also tells the model to decline |
| BOT Q13 — decline wording | FR-010 | "I can only help with pregnancy, prenatal care, nutrition and postpartum wellness. Could you ask me a pregnancy question?" (S-034 #10b example) |
| BOT Q8 — hotline number | FR-007, FR-009 | "1900 xxxx" placeholder as drawn |
| BOT Q10 — error text and timeout | LLM failure | Gemini call timeout 20 s; on failure **nothing is stored** and the question is put back in the input with "⚠ Could not get an answer. Retry" — this differs from the DM-29 default ("the question row is kept"), recorded in the build log for the BOT owner |
| BOT Q11 — the same risk question asked again | One case or several | One case per question the mother sends to a nurse ("Connect to nurse" can be tapped once per question) |
| A new conversation or the last one | No rule in the spec | Each visit to S-031 starts a new conversation when the first question is sent; follow-up questions stay in it (FR-003, D-67) |
| Gemini model name | `generateContent` needs a model | Read from `GEMINI_MODEL` in `.env`; without both settings the fake client is used |
