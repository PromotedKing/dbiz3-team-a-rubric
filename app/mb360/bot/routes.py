"""BOT routes — specs/008-bot-chat/contracts/http-routes.md (S-031, S-032 – S-034)."""
import json
import sqlite3
from datetime import datetime
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from .. import clock
from . import chat, classify, llm

TEMPLATES = Jinja2Templates(directory=str(Path(__file__).resolve().parents[1] / "templates"))
TEMPLATES.env.filters["show_time"] = lambda t: datetime.strptime(t, "%Y-%m-%d %H:%M").strftime("%d/%m/%Y · %H:%M") if t else ""
SUGGESTED = ("How can I eat beef safely during pregnancy?", "How can I produce more breast milk?",
             "What should I look for when choosing formula for my baby?", "How should Dad read to the baby during pregnancy?")
HOTLINE = "1900 xxxx"   # placeholder (BOT §10 Q8)


def register(app: FastAPI, conn: sqlite3.Connection) -> None:
    def mother(user_id: str) -> sqlite3.Row:
        row = conn.execute("SELECT * FROM USER_ACCOUNT WHERE user_id = ?", (user_id,)).fetchone()
        if row is None:
            raise HTTPException(404, "Unknown mother")
        return row

    def bubbles(conversation_id: str) -> list[dict]:
        rows = conn.execute("SELECT * FROM CHAT_MESSAGE WHERE conversation_id = ? ORDER BY sent_at, rowid", (conversation_id,)).fetchall()
        out, last_q = [], None
        for m in rows:
            if m["sender"] == "Mother":
                intent = json.loads(m["parsed_intent"]).get("intent") if m["parsed_intent"] else None
                last_q = {"row": m, "intent": intent, "danger": classify.classify(m["text"])["danger"] if m["is_risk"] else False}
                out.append({"kind": "question", "m": m})
            else:
                kind = {"needs_nurse": "handoff", "out_of_scope": "decline"}.get(last_q["intent"] if last_q else None, "answer")
                out.append({"kind": kind, "m": m, "q": last_q["row"] if last_q else None, "danger": last_q["danger"] if last_q else False})
        return out

    def page(request: Request, user, conversation_id: str | None, status: int = 200, error: str | None = None, text: str = ""):
        return TEMPLATES.TemplateResponse(request, "chat.html", {
            "user": user, "conversation_id": conversation_id, "bubbles": bubbles(conversation_id) if conversation_id else [],
            "suggested": SUGGESTED, "hotline": HOTLINE, "error": error, "text": text}, status_code=status)

    async def handle_ask(request: Request, user_id: str, conversation_id: str | None):
        user = mother(user_id)
        text = (await request.form()).get("text") or ""
        try:
            conversation_id = chat.ask(conn, user_id, conversation_id, text, clock.now(), llm.get_client())
        except chat.ChatError as e:
            if e.status == 404:
                raise HTTPException(404, e.message)
            return page(request, user, conversation_id, 422, e.message, text)
        except Exception:   # LLM unavailable (BOT §10 Q10): nothing stored, the question is put back for "Retry"
            return page(request, user, conversation_id, 503, "⚠ Could not get an answer. Retry", text)
        return RedirectResponse(f"/m/{user_id}/chat/{conversation_id}", status_code=303)

    @app.get("/m/{user_id}/chat", response_class=HTMLResponse)
    def welcome(request: Request, user_id: str):
        return page(request, mother(user_id), None)

    @app.post("/m/{user_id}/chat", response_class=HTMLResponse)
    async def first_question(request: Request, user_id: str):
        return await handle_ask(request, user_id, None)

    @app.get("/m/{user_id}/chat/{conversation_id}", response_class=HTMLResponse)
    def conversation(request: Request, user_id: str, conversation_id: str):
        user = mother(user_id)
        if conn.execute("SELECT 1 FROM CONVERSATION WHERE conversation_id = ? AND user_id = ?", (conversation_id, user_id)).fetchone() is None:
            raise HTTPException(404, "Unknown conversation")
        return page(request, user, conversation_id)

    @app.post("/m/{user_id}/chat/{conversation_id}", response_class=HTMLResponse)
    async def follow_up(request: Request, user_id: str, conversation_id: str):
        return await handle_ask(request, user_id, conversation_id)

    @app.post("/m/{user_id}/chat/{conversation_id}/handoff/{message_id}")
    async def handoff(request: Request, user_id: str, conversation_id: str, message_id: str):
        mother(user_id)
        choice = (await request.form()).get("choice") or ""
        try:
            chat.handoff(conn, user_id, message_id, choice, clock.now())
        except chat.ChatError as e:
            raise HTTPException(e.status, e.message)
        return RedirectResponse(f"/m/{user_id}/chat/{conversation_id}", status_code=303)
