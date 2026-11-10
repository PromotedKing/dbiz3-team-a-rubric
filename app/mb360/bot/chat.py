"""BOT FR-001 – FR-004, FR-007 – FR-010, BR-001, BR-002, D-34, D-67 (research R3, R4).

The context passed to the LLM holds only the earlier question / answer pairs of this conversation and the
gestational week — never anything from the medical record (BR-001)."""
import json
import sqlite3
import uuid
from datetime import date, datetime

from ..alr import cases
from ..alr.reports import gestational_week
from . import classify

DB_TIME = "%Y-%m-%d %H:%M"
MAX_LEN = 500   # D-46
ANSWER_MAX = 500   # the schema holds every CHAT_MESSAGE.text to 500 characters; the limit for answers is open (DM-36)
HANDOFF_TEXT = "This needs a proper consultation. It will be sent to a nurse if you agree"
DECLINE_TEXT = ("I can only help with pregnancy, prenatal care, nutrition and postpartum wellness. "
                "Could you ask me a pregnancy question?")   # wording open (BOT §10 Q13)


class ChatError(Exception):
    def __init__(self, status: int, message: str):
        super().__init__(message)
        self.status, self.message = status, message


def _week(conn, user_id: str, now: datetime) -> int | None:
    row = conn.execute("SELECT edd FROM PREGNANCY_PROFILE WHERE user_id = ?", (user_id,)).fetchone()
    return gestational_week(date.fromisoformat(row[0]), now.date()) if row else None


def _earlier(conn, conversation_id: str) -> list[dict]:
    """Earlier general question / answer pairs of the conversation (FR-003, D-67)."""
    msgs = conn.execute("SELECT sender, text, parsed_intent FROM CHAT_MESSAGE WHERE conversation_id = ? ORDER BY sent_at, rowid",
                        (conversation_id,)).fetchall()
    pairs, pending = [], None
    for m in msgs:
        if m["sender"] == "Mother":
            intent = json.loads(m["parsed_intent"]).get("intent") if m["parsed_intent"] else None
            pending = m["text"] if intent == "general" else None
        elif pending is not None:
            pairs.append({"question": pending, "answer": m["text"]})
            pending = None
    return pairs


def fit(answer: str, limit: int = ANSWER_MAX) -> str:
    """An LLM answer cut to the stored limit at the end of a sentence (or a word), so it can always be saved."""
    answer = answer.replace("**", "").strip()
    if len(answer) <= limit:
        return answer
    cut = answer[:limit - 1]
    end = max(cut.rfind(c) for c in ".!?\n")
    return cut[:end + 1].strip() if end >= limit // 2 else cut[:cut.rfind(" ")].rstrip(",;:") + "…"


def _message(conn, conversation_id, sender, text, at, intent=None, is_risk=0) -> str:
    mid = str(uuid.uuid4())
    conn.execute("""INSERT INTO CHAT_MESSAGE (message_id, conversation_id, sender, text, parsed_intent, is_risk, handoff_choice, sent_at)
                    VALUES (?, ?, ?, ?, ?, ?, NULL, ?)""",
                 (mid, conversation_id, sender, text, json.dumps({"intent": intent}) if intent else None, is_risk, at))
    return mid


def prepare(conn: sqlite3.Connection, user_id: str, conversation_id: str | None, text: str, now: datetime) -> dict:
    """Checks the question and reads what the answer needs. `context` is set only for a general question (BR-002):
    it is all that goes to the LLM service (BR-001)."""
    text = (text or "").strip()
    if not text:
        raise ChatError(422, "Type your question.")
    if len(text) > MAX_LEN:
        raise ChatError(422, f"At most {MAX_LEN} characters.")
    if conversation_id and conn.execute("SELECT 1 FROM CONVERSATION WHERE conversation_id = ? AND user_id = ?",
                                        (conversation_id, user_id)).fetchone() is None:
        raise ChatError(404, "Unknown conversation")
    kind = classify.classify(text)
    week = _week(conn, user_id, now)
    context = None
    if kind["category"] == "general":
        context = {"gestational_week": week, "earlier": _earlier(conn, conversation_id) if conversation_id else []}
    return {"user_id": user_id, "conversation_id": conversation_id, "text": text, "kind": kind, "week": week,
            "at": now.strftime(DB_TIME), "context": context}


def ask(conn: sqlite3.Connection, user_id: str, conversation_id: str | None, text: str, now: datetime, client) -> str:
    q = prepare(conn, user_id, conversation_id, text, now)
    return save(conn, q, client.answer(q["text"], q["context"]) if q["context"] is not None else None, client)


def save(conn: sqlite3.Connection, q: dict, answer: str | None, client) -> str:
    """Stores the question and the chatbot's reply in one transaction; returns the conversation."""
    user_id, conversation_id, text, kind, week, at = q["user_id"], q["conversation_id"], q["text"], q["kind"], q["week"], q["at"]
    try:
        if conversation_id is None:
            conversation_id = str(uuid.uuid4())
            conn.execute("INSERT INTO CONVERSATION (conversation_id, user_id, current_session_data) VALUES (?, ?, NULL)",
                         (conversation_id, user_id))
        turns = len(_earlier(conn, conversation_id))
        _message(conn, conversation_id, "Mother", text, at, kind["category"], 1 if kind["category"] == "needs_nurse" else 0)
        if kind["category"] == "needs_nurse":
            _message(conn, conversation_id, "Chatbot", HANDOFF_TEXT, at)          # FR-007: no case yet (D-34)
        elif kind["category"] == "out_of_scope":
            _message(conn, conversation_id, "Chatbot", DECLINE_TEXT, at)          # FR-010
        else:
            _message(conn, conversation_id, "Chatbot", fit(answer), at)
            conn.execute("INSERT INTO AI_RESPONSE_LOG (log_id, conversation_id, ai_response_data, audit_log_entry) VALUES (?, ?, ?, ?)",
                         (str(uuid.uuid4()), conversation_id, answer, json.dumps({"client": getattr(client, "name", "unknown")})))
        conn.execute("UPDATE CONVERSATION SET current_session_data = ? WHERE conversation_id = ?",
                     (json.dumps({"gestational_week": week, "earlier_turns": turns}), conversation_id))
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    return conversation_id


def handoff(conn: sqlite3.Connection, user_id: str, message_id: str, choice: str, now: datetime) -> str | None:
    """FR-008 (connect → Chatbot case through ALR FR-021) / FR-009 (decline → no case)."""
    m = conn.execute("""SELECT m.* FROM CHAT_MESSAGE m JOIN CONVERSATION v ON v.conversation_id = m.conversation_id
                        WHERE m.message_id = ? AND v.user_id = ?""", (message_id, user_id)).fetchone()
    if m is None or m["sender"] != "Mother" or not m["is_risk"]:
        raise ChatError(404, "No hand-off offer for this message")
    if m["handoff_choice"] is not None:
        raise ChatError(409, "A choice was already made for this question")
    if choice not in ("connect", "decline"):
        raise ChatError(422, "Unknown choice")
    try:
        conn.execute("UPDATE CHAT_MESSAGE SET handoff_choice = ? WHERE message_id = ?",
                     ("Connect to nurse" if choice == "connect" else "No thanks", message_id))
        case_id = cases.open_chatbot_case(conn, user_id, message_id, now) if choice == "connect" else None
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    return case_id
