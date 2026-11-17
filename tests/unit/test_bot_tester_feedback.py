"""Tester feedback 17/11/2026 (D-101, proposed).

1. The chatbot's danger flag is stored on the question when it is classified (CHAT_MESSAGE.parsed_intent "danger"), read
   by the Chatbot case through chat_message_id, and shown on the clinical web — it no longer depends on the keyword list
   of the day. (BR-012 of PR #43, "a nurse cannot close it", is not built here: that spec is not accepted yet.)
2. Everyday illnesses and questions about taking a medicine, vitamin or supplement get the nurse offer, never the decline
   and never a Groq answer (BR-002); general knowledge about them still reaches the LLM."""
import json

import pytest

from mb360.bot import chat, classify, llm
from mb360.cli import dashboard, queue
from tests.acc_helpers import NOW


def ask(db, uid, q):
    conv = chat.ask(db, uid, None, q, NOW, llm.FakeLLM())
    return db.execute("SELECT * FROM CHAT_MESSAGE WHERE conversation_id = ? AND sender = 'Mother'", (conv,)).fetchone()


def connect(db, uid, q):
    m = ask(db, uid, q)
    return m, chat.handoff(db, uid, m["message_id"], "connect", NOW)


def test_the_flag_is_stored_when_the_question_is_classified(db, user_id):
    uid = user_id("tci-000133")
    m = ask(db, uid, "Tôi bị ra máu")
    assert json.loads(m["parsed_intent"]) == {"intent": "needs_nurse", "danger": True} and chat.danger_of(m)
    m = ask(db, uid, "Em bị sốt nhẹ")
    assert json.loads(m["parsed_intent"]) == {"intent": "needs_nurse", "danger": False} and not chat.danger_of(m)


def test_the_stored_flag_does_not_change_with_the_keyword_list(db, user_id, monkeypatch):
    m = ask(db, user_id("tci-000133"), "Tôi bị ra máu")
    lists = classify._lists()
    monkeypatch.setattr(classify, "_lists", lambda: {**lists, "danger_phrases": []})
    assert chat.danger_of(m) is True


def test_rows_stored_before_the_flag_are_classified_again(db, user_id):
    m = ask(db, user_id("tci-000133"), "Tôi bị ra máu")
    db.execute("UPDATE CHAT_MESSAGE SET parsed_intent = ? WHERE message_id = ?", (json.dumps({"intent": "needs_nurse"}), m["message_id"]))
    assert chat.danger_of(db.execute("SELECT * FROM CHAT_MESSAGE WHERE message_id = ?", (m["message_id"],)).fetchone()) is True


def test_the_clinical_web_sees_the_flag(db, user_id, client, staff_id):
    uid = user_id("tci-000133")
    _, danger_case = connect(db, uid, "Tôi bị ra máu")
    _, plain_case = connect(db, uid, "Em bị sốt nhẹ")
    rows = {r["case_id"]: r for r in queue.list_cases(db)}
    assert rows[danger_case]["danger"] is True and rows[plain_case]["danger"] is False
    board = {r["case_id"]: r for r in dashboard.cases(db, NOW)}
    assert board[danger_case]["danger"] and board[danger_case]["alarm"] and not board[plain_case]["danger"]
    nurse = staff_id("Trần Thị B")
    assert "data-danger" in client.get(f"/staff/{nurse}/cases/{danger_case}").text
    assert "data-danger" not in client.get(f"/staff/{nurse}/cases/{plain_case}").text
    assert client.get(f"/staff/{nurse}/cases").text.count("data-danger") >= 1


@pytest.mark.parametrize("q", ["Sổ mũi phải làm sao?", "Tiêu chảy phải làm sao", "Đau họng uống gì", "I have a cold, what should I do?",
                               "Em uống paracetamol được không?", "Em có nên uống thêm canxi không?", "Em uống thêm vitamin D được không?",
                               "Uống DHA loại nào tốt?", "Em quên uống viên sắt hôm qua", "Em uống thực phẩm chức năng được không?"])
def test_illness_and_medicine_decisions_go_to_the_nurse(q):
    assert classify.classify(q) == {"category": "needs_nurse", "danger": False}


@pytest.mark.parametrize("q", ["Paracetamol là gì?", "Bà bầu uống vitamin gì?", "Axit folic uống đến khi nào?", "Canxi uống lúc nào tốt nhất?",
                               "Tiêm phòng cúm khi mang thai được không?", "Is the flu shot safe in pregnancy?"])
def test_general_knowledge_about_them_still_reaches_the_llm(q):
    assert classify.classify(q)["category"] == "general"
