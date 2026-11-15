"""T005 — BOT FR-001 – FR-004, FR-007 – FR-010, BR-001, D-34, D-67 (chat logic with the fake LLM)."""
import json

import pytest

from mb360.bot import chat, llm
from tests.acc_helpers import NOW


def chat_mother(user_id):
    return user_id("tci-000133")


def messages(db, conv):
    return db.execute("SELECT * FROM CHAT_MESSAGE WHERE conversation_id = ? ORDER BY sent_at, rowid", (conv,)).fetchall()


def count(db, table):
    return db.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]


def test_general_question(db, user_id):
    fake = llm.FakeLLM()
    conv = chat.ask(db, chat_mother(user_id), None, "How can I eat beef safely during pregnancy?", NOW, fake)
    msgs = messages(db, conv)
    assert [(m["sender"], m["is_risk"]) for m in msgs] == [("Mother", 0), ("Chatbot", 0)]
    assert json.loads(msgs[0]["parsed_intent"]) == {"intent": "general"}
    assert msgs[1]["text"] == "[Sample chatbot answer]"
    assert db.execute("SELECT COUNT(*) FROM AI_RESPONSE_LOG WHERE conversation_id = ?", (conv,)).fetchone()[0] == 1
    data = json.loads(db.execute("SELECT current_session_data FROM CONVERSATION WHERE conversation_id = ?", (conv,)).fetchone()[0])
    assert data == {"gestational_week": 24, "earlier_turns": 0}


def test_context_holds_only_earlier_turns_and_the_week(db, user_id):
    mother = user_id("tci-000126")
    db.execute("UPDATE PATIENT_CLINICAL_PROFILE SET blood_type = ?, allergies = ? WHERE user_id = ?",
               ("O−", "Seafood", mother))
    """BR-001: the medical record is never sent to the chatbot service."""
    fake = llm.FakeLLM()
    conv = chat.ask(db, mother, None, "How can I eat beef safely during pregnancy?", NOW, fake)
    chat.ask(db, mother, conv, "And what about fish during pregnancy?", NOW, fake)
    question, context = fake.last_input
    assert question == "And what about fish during pregnancy?"
    assert context == {"gestational_week": 31,
                       "earlier": [{"question": "How can I eat beef safely during pregnancy?", "answer": "[Sample chatbot answer]"}]}
    sent = json.dumps(fake.last_input, ensure_ascii=False)
    for private in ("O−", "Seafood", "145/92", "BC-0926-011", "Phạm Ngọc Mai", "TC-00126"):
        assert private not in sent


def test_risk_question_offers_a_nurse_without_answer_or_case(db, user_id):
    fake = llm.FakeLLM()
    cases = count(db, "CARE_CASE")
    conv = chat.ask(db, chat_mother(user_id), None, "I have had a little bleeding since this morning, is that okay?", NOW, fake)
    msgs = messages(db, conv)
    assert fake.last_input is None                                          # not sent to the LLM (BR-002)
    assert msgs[0]["is_risk"] == 1 and msgs[0]["handoff_choice"] is None
    assert msgs[1]["text"] == "This needs a proper consultation. It will be sent to a nurse if you agree"
    assert count(db, "CARE_CASE") == cases                                  # no case at this step (D-34)


def test_connect_to_nurse_creates_one_chatbot_case(db, user_id):
    conv = chat.ask(db, chat_mother(user_id), None, "I have had a little bleeding since this morning, is that okay?", NOW, llm.FakeLLM())
    q = messages(db, conv)[0]
    case_id = chat.handoff(db, chat_mother(user_id), q["message_id"], "connect", NOW)
    case = db.execute("SELECT * FROM CARE_CASE WHERE case_id = ?", (case_id,)).fetchone()
    assert (case["case_source"], case["status"], case["chat_message_id"], case["metric_report_id"]) == ("Chatbot", "Not viewed", q["message_id"], None)
    assert db.execute("SELECT role FROM CASE_STATUS_HISTORY WHERE case_id = ?", (case_id,)).fetchone()[0] == "System"
    assert db.execute("SELECT COUNT(*) FROM NOTIFICATION WHERE case_id = ? AND type = 'Report'", (case_id,)).fetchone()[0] == 1
    assert db.execute("SELECT handoff_choice FROM CHAT_MESSAGE WHERE message_id = ?", (q["message_id"],)).fetchone()[0] == "Connect to nurse"
    with pytest.raises(chat.ChatError):
        chat.handoff(db, chat_mother(user_id), q["message_id"], "decline", NOW)       # one choice per question


def test_no_thanks_creates_no_case(db, user_id):
    conv = chat.ask(db, chat_mother(user_id), None, "I feel tired, is that normal?", NOW, llm.FakeLLM())
    q = messages(db, conv)[0]
    cases = count(db, "CARE_CASE")
    assert chat.handoff(db, chat_mother(user_id), q["message_id"], "decline", NOW) is None
    assert count(db, "CARE_CASE") == cases
    assert db.execute("SELECT handoff_choice FROM CHAT_MESSAGE WHERE message_id = ?", (q["message_id"],)).fetchone()[0] == "No thanks"


def test_out_of_scope_question_is_declined(db, user_id):
    fake = llm.FakeLLM()
    conv = chat.ask(db, chat_mother(user_id), None, "How do I change a car tyre?", NOW, fake)
    msgs = messages(db, conv)
    assert fake.last_input is None and msgs[0]["is_risk"] == 0
    assert msgs[1]["text"].startswith("I can only help with pregnancy, prenatal care, nutrition and postpartum wellness.")


@pytest.mark.parametrize("text", ["", "   ", "x" * 501])
def test_invalid_question_stores_nothing(db, user_id, text):
    before = count(db, "CHAT_MESSAGE"), count(db, "CONVERSATION")
    with pytest.raises(chat.ChatError):
        chat.ask(db, chat_mother(user_id), None, text, NOW, llm.FakeLLM())
    assert (count(db, "CHAT_MESSAGE"), count(db, "CONVERSATION")) == before


class _Says(llm.FakeLLM):
    def __init__(self, text):
        super().__init__()
        self.text = text

    def answer(self, question, context):
        super().answer(question, context)
        return self.text


def test_unsafe_answer_is_held_back_and_logged(db, user_id):
    """Output check (§10 Q16): a dose in the answer → the fallback is shown; the raw answer and the reason are logged."""
    raw = "Mẹ uống viên sắt 60 mg mỗi ngày."
    conv = chat.ask(db, chat_mother(user_id), None, "Bà bầu nên ăn gì để đủ sắt?", NOW, _Says(raw))
    assert messages(db, conv)[1]["text"] == chat.guard.FALLBACK_TEXT
    data, entry = db.execute("SELECT ai_response_data, audit_log_entry FROM AI_RESPONSE_LOG WHERE conversation_id = ?", (conv,)).fetchone()
    assert data == raw and json.loads(entry) == {"client": "fake", "model": None, "output_check": ["dose"], "shown": "fallback"}


def test_safe_answer_is_shown_and_logged_as_passed(db, user_id):
    conv = chat.ask(db, chat_mother(user_id), None, "Bà bầu nên ăn gì để đủ sắt?", NOW, _Says("Mẹ ăn thịt bò nạc và rau xanh đậm."))
    assert messages(db, conv)[1]["text"] == "Mẹ ăn thịt bò nạc và rau xanh đậm."
    entry = json.loads(db.execute("SELECT audit_log_entry FROM AI_RESPONSE_LOG WHERE conversation_id = ?", (conv,)).fetchone()[0])
    assert entry["output_check"] == "passed" and entry["shown"] == "answer"
