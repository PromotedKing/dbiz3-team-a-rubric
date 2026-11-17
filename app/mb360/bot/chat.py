"""BOT FR-001 – FR-004, FR-007 – FR-010, BR-001, BR-002, D-34, D-67 (research R3, R4).

The context passed to the LLM holds only the earlier question / answer pairs of this conversation and the
gestational week — never anything from the medical record (BR-001)."""
import json
import re
import sqlite3
import uuid
from datetime import date, datetime, timedelta

from ..alr import cases
from ..alr.reports import gestational_week
from . import classify, guard, lookup

DB_TIME = "%Y-%m-%d %H:%M"
MAX_LEN = 500   # D-46
ANSWER_MAX = 500   # the schema holds every CHAT_MESSAGE.text to 500 characters; the limit for answers is open (DM-36)
HANDOFF_TEXT = "This needs a proper consultation. It will be sent to a nurse if you agree"
DECLINE_TEXT = ("I can only help with pregnancy, prenatal care, nutrition and postpartum wellness. "
                "Could you ask me a pregnancy question?")   # wording open (BOT §10 Q13)


HOTLINE = "1900 xxxx"   # placeholder (BOT §10 Q8)
SMALL_TALK = {          # D-95 (proposed): fixed replies, shown through the label table (no LLM)
    "greeting": "Hello, Mom! I can answer general questions about pregnancy and read your data in this app. What would you like to ask?",
    "thanks": "You're welcome, Mom! Ask me anytime.",
    "identity": ("I am the pregnancy assistant of Mother & Baby 360. I answer general questions about pregnancy and read your "
                 "data in this app; I do not diagnose and do not replace your doctor."),
    "bye": "Goodbye, Mom! Take care of yourself and the baby.",
    "unclear": "Could you ask the whole question again, Mom? For example: “What was my last blood pressure?”",
}
HOSPITAL_TEXT = ("For prices, packages, insurance, addresses and opening hours of Thu Cuc Hospital, please see the TCI app "
                 "or call {hotline}.")   # D-95: no hospital data in the app yet, so never guessed by the LLM
REPEAT_MINUTES = 5   # D-90 (proposed): the same question again within this time is the same request (e.g. a second tab)


class ChatError(Exception):
    def __init__(self, status: int, message: str):
        super().__init__(message)
        self.status, self.message = status, message


class AlreadyAsked(ChatError):
    """D-90: the mother sent this question a moment ago (another tab or device): show that conversation, store nothing."""
    def __init__(self, conversation_id: str):
        super().__init__(303, "Already asked")
        self.conversation_id = conversation_id


def danger_of(row) -> bool:
    """D-101 (proposed): the danger flag of a mother's question as stored when it was classified (parsed_intent "danger").
    Rows stored before 17/11/2026 have no flag: classified again from their text, as S-034 did until then."""
    if not row or not row["is_risk"]:
        return False
    parsed = json.loads(row["parsed_intent"]) if row["parsed_intent"] else {}
    return bool(parsed["danger"]) if "danger" in parsed else classify.classify(row["text"])["danger"]


def _key(text: str) -> str:
    """The question as compared for D-90: lower case, without accents and punctuation."""
    return " ".join(re.findall(r"\w+", classify.plain(text or "")))


def _asked_just_now(conn, user_id: str, text: str, at: str) -> str | None:
    """The conversation where the mother sent the same question in the last REPEAT_MINUTES, or None (D-90)."""
    since = (datetime.strptime(at, DB_TIME) - timedelta(minutes=REPEAT_MINUTES)).strftime(DB_TIME)
    rows = conn.execute("""SELECT m.text, m.conversation_id FROM CHAT_MESSAGE m JOIN CONVERSATION v ON v.conversation_id = m.conversation_id
                           WHERE v.user_id = ? AND m.sender = 'Mother' AND m.sent_at >= ?
                           ORDER BY m.sent_at DESC, m.rowid DESC""", (user_id, since)).fetchall()
    key = _key(text)
    return next((r["conversation_id"] for r in rows if _key(r["text"]) == key), None)


def _open_case_for_same_question(conn, user_id: str, text: str) -> str | None:
    """D-90: an open Chatbot case of this mother opened from the same question (BOT §10 Q11)."""
    rows = conn.execute("""SELECT c.case_id, m.text FROM CARE_CASE c JOIN CHAT_MESSAGE m ON m.message_id = c.chat_message_id
                           WHERE c.user_id = ? AND c.case_source = 'Chatbot' AND c.status <> 'Resolved'
                           ORDER BY c.created_at DESC""", (user_id,)).fetchall()
    key = _key(text)
    return next((r["case_id"] for r in rows if _key(r["text"]) == key), None)


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


def _message(conn, conversation_id, sender, text, at, intent=None, is_risk=0, extra=None) -> str:
    mid = str(uuid.uuid4())
    parsed = {"intent": intent, **(extra or {})} if intent else None
    conn.execute("""INSERT INTO CHAT_MESSAGE (message_id, conversation_id, sender, text, parsed_intent, is_risk, handoff_choice, sent_at)
                    VALUES (?, ?, ?, ?, ?, ?, NULL, ?)""",
                 (mid, conversation_id, sender, text, json.dumps(parsed, ensure_ascii=False) if parsed else None, is_risk, at))
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
    earlier = _asked_just_now(conn, user_id, text, now.strftime(DB_TIME))
    if earlier:
        raise AlreadyAsked(earlier)
    kind = classify.classify(text)
    if conversation_id and kind["category"] in ("general", "out_of_scope", "small_talk"):     # D-95: read with the previous question
        prev = conn.execute("""SELECT parsed_intent FROM CHAT_MESSAGE WHERE conversation_id = ? AND sender = 'Mother'
                               ORDER BY sent_at DESC, rowid DESC LIMIT 1""", (conversation_id,)).fetchone()
        kind = classify.follow_up(text, json.loads(prev[0]) if prev and prev[0] else None) or kind
    if kind["category"] == "out_of_scope" and classify.unclear_follow_up(text):
        kind = {"category": "small_talk", "danger": False, "reply": "unclear"}
    week = _week(conn, user_id, now)
    context = lookup_answer = None
    fixed = (SMALL_TALK[kind["reply"]] if kind["category"] == "small_talk"
             else HOSPITAL_TEXT.format(hotline=HOTLINE) if kind["category"] == "hospital_info" else None)
    if kind["category"] == "general":
        context = {"gestational_week": week, "earlier": _earlier(conn, conversation_id) if conversation_id else []}
    elif kind["category"] == "lookup":                                            # FR-012: built here, no LLM (BR-006)
        lookup_answer = lookup.answer(conn, user_id, kind["lookup"], now)
    return {"user_id": user_id, "conversation_id": conversation_id, "text": text, "kind": kind, "week": week,
            "at": now.strftime(DB_TIME), "context": context, "lookup_answer": lookup_answer, "fixed": fixed}


def ask(conn: sqlite3.Connection, user_id: str, conversation_id: str | None, text: str, now: datetime, client) -> str:
    q = prepare(conn, user_id, conversation_id, text, now)
    return save(conn, q, client.answer(q["text"], q["context"]) if q["context"] is not None else None, client)


def save(conn: sqlite3.Connection, q: dict, answer: str | None, client) -> str:
    """Stores the question and the chatbot's reply in one transaction; returns the conversation."""
    user_id, conversation_id, text, kind, week, at = q["user_id"], q["conversation_id"], q["text"], q["kind"], q["week"], q["at"]
    earlier = _asked_just_now(conn, user_id, text, at)       # stored by another tab while this one waited for the LLM (D-90)
    if earlier:
        return earlier
    try:
        if conversation_id is None:
            conversation_id = str(uuid.uuid4())
            conn.execute("INSERT INTO CONVERSATION (conversation_id, user_id, current_session_data) VALUES (?, ?, NULL)",
                         (conversation_id, user_id))
        turns = len(_earlier(conn, conversation_id))
        _message(conn, conversation_id, "Mother", text, at, kind["category"], 1 if kind["category"] == "needs_nurse" else 0,
                 kind.get("lookup") or ({"danger": kind["danger"]} if kind["category"] == "needs_nurse" else None))   # D-101
        if q.get("fixed"):
            _message(conn, conversation_id, "Chatbot", q["fixed"], at)               # D-95: small talk, hospital information
        elif kind["category"] == "lookup":
            _message(conn, conversation_id, "Chatbot", fit(q["lookup_answer"]), at)   # FR-012; not an AI answer, so no AI_RESPONSE_LOG
        elif kind["category"] == "needs_nurse":
            _message(conn, conversation_id, "Chatbot", HANDOFF_TEXT, at)          # FR-007: no case yet (D-34)
        elif kind["category"] == "out_of_scope":
            _message(conn, conversation_id, "Chatbot", DECLINE_TEXT, at)          # FR-010
        else:
            held = guard.check(answer)                                            # output check (§10 Q16)
            _message(conn, conversation_id, "Chatbot", guard.FALLBACK_TEXT if held else fit(answer), at)
            entry = {"client": getattr(client, "name", "unknown"), "model": getattr(client, "model", None),
                     "output_check": held or "passed", "shown": "fallback" if held else "answer"}
            conn.execute("INSERT INTO AI_RESPONSE_LOG (log_id, conversation_id, ai_response_data, audit_log_entry) VALUES (?, ?, ?, ?)",
                         (str(uuid.uuid4()), conversation_id, answer, json.dumps(entry)))
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
        case_id = None
        if choice == "connect":                 # D-90: one open case per question, even when asked again in another tab
            case_id = _open_case_for_same_question(conn, user_id, m["text"]) or cases.open_chatbot_case(conn, user_id, message_id, now)
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    return case_id
