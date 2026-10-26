# Quickstart: BOT chat (US-1, US-2)

Same install as `specs/001-alr-core/quickstart.md`, then:

```bash
uv run tools/start_feature.py --use specs/008-bot-chat
uv run python -m pytest
uv run python -m uvicorn mb360.main:app --app-dir app --reload
```

Without a key the chatbot uses the **fake LLM** (answers "[Sample chatbot answer]"). To try Gemini, each member creates their own key in Google AI Studio and puts two lines in `.env` at the repository root (the file is git-ignored — never commit it; see `env.example`):

```text
GEMINI_API_KEY=<your key>
GEMINI_MODEL=<a model name listed in Google AI Studio>
```

## Validation scenarios

| # | Steps | Expected |
|---|---|---|
| 1 | `/` → **Ngô Thị Thảo** → Home → "Health chatbot ›" | S-031: "Hello, Mom!", disclaimer, 4 suggested questions |
| 2 | Tap "How can I eat beef safely during pregnancy?" | S-034: the question, an answer bubble, "For reference only; does not replace your doctor's advice." |
| 3 | Ask "I have had a little bleeding since this morning, is that okay?" | "Signs that need medical attention", "This needs a proper consultation.", "Connect to nurse" / "No, thanks", "If you have any emergency signs, call 1900 xxxx."; no answer |
| 4 | "Connect to nurse" | "Sent to a nurse"; nurse `/staff` → Trần Thị B → the case (source Chatbot) is in the queue with the whole conversation |
| 5 | Ask "How do I change a car tyre?" | polite decline, no buttons |
| 6 | Ask "I feel tired, is that normal?" → "No, thanks" | no case; hotline shown |
