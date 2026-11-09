"""Fixes from the project review of 09/11/2026 (A2, C1, C2, C3)."""
import re
from pathlib import Path

from mb360 import serial, ui
from mb360.bot import llm

TEMPLATES = Path(__file__).resolve().parents[2] / "app" / "mb360" / "templates"


class WaitingLLM:
    """Records whether the database lock was held while the LLM service was being asked."""
    name = "waiting"

    def __init__(self):
        self.lock_held = None

    def answer(self, question, context):
        self.lock_held = serial.LOCK.locked()
        return "Câu trả lời thử."


def test_the_llm_is_asked_outside_the_database_lock(client, db, user_id, monkeypatch):
    """A2: while one mother waits for the LLM service, the others are not kept waiting."""
    fake = WaitingLLM()
    monkeypatch.setattr(llm, "get_client", lambda: fake)
    uid = user_id("tci-000131")
    r = client.post(f"/m/{uid}/chat", data={"text": "How can I eat beef safely during pregnancy?"})
    assert r.status_code == 303
    assert fake.lock_held is False
    assert not serial.LOCK.locked()
    cid = r.headers["location"].rsplit("/", 1)[1]
    assert db.execute("SELECT COUNT(*) FROM CHAT_MESSAGE WHERE conversation_id = ?", (cid,)).fetchone()[0] == 2


def test_a_failing_llm_stores_nothing_and_frees_the_lock(client, db, user_id, monkeypatch):
    class Broken:
        name = "broken"
        def answer(self, question, context):
            raise TimeoutError("no answer in 15 s")
    monkeypatch.setattr(llm, "get_client", lambda: Broken())
    before = db.execute("SELECT COUNT(*) FROM CHAT_MESSAGE").fetchone()[0]
    r = client.post(f"/m/{user_id('tci-000131')}/chat", data={"text": "How can I eat beef safely during pregnancy?"})
    assert r.status_code == 503 and not serial.LOCK.locked()
    assert db.execute("SELECT COUNT(*) FROM CHAT_MESSAGE").fetchone()[0] == before


def test_only_the_chatbot_question_takes_the_lock_itself():
    assert serial.locks_itself("POST", "/m/u1/chat") and serial.locks_itself("POST", "/m/u1/chat/c1")
    assert not serial.locks_itself("GET", "/m/u1/chat")
    assert not serial.locks_itself("POST", "/m/u1/chat/c1/handoff/m1")
    assert not serial.locks_itself("POST", "/m/u1/report")


def test_side_panel_names_both_keys(monkeypatch):
    """C2: the code tries Groq first, so the panel does not speak of Gemini only."""
    monkeypatch.setattr(llm, "describe", lambda: "local")
    assert "GROQ_API_KEY" in ui._chatbot_engine()


def test_no_internal_codes_on_staff_and_test_pages():
    """C3: decision and question numbers stay in the documents, not on the pages."""
    for name in ("case.html", "staff_select.html", "tci_accounts.html"):
        visible = re.sub(r"\{#.*?#\}", "", (TEMPLATES / name).read_text(encoding="utf-8"), flags=re.S)
        assert not re.search(r"\bD-\d\d\b|§10 Q\d", visible), name
