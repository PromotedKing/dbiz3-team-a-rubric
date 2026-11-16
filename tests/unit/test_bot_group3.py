"""D-95 (proposed), 16/11/2026: small talk, follow-up questions read with the previous one, and hospital information that
the app does not hold (prices, packages, address, hours, insurance) — answered by fixed replies, never guessed by the LLM."""
import json
from datetime import timedelta

import pytest

from mb360 import ui
from mb360.bot import chat, classify, llm

LAN = "tci-000123"


@pytest.fixture
def talk(db, user_id):
    """One conversation; each call asks the next question in it and returns (intent, shown text, LLM input)."""
    from tests.acc_helpers import NOW
    state = {"conv": None, "n": 0}

    def ask(q):
        state["n"] += 1
        fake = llm.FakeLLM()
        state["conv"] = chat.ask(db, user_id(LAN), state["conv"], q, NOW + timedelta(minutes=10 * state["n"]), fake)
        mother, bot = db.execute("""SELECT parsed_intent, text FROM CHAT_MESSAGE WHERE conversation_id = ? ORDER BY rowid DESC LIMIT 2""",
                                 (state["conv"],)).fetchall()[::-1]
        return json.loads(mother[0]), ui.t_known(bot[1]), fake.last_input
    return ask


@pytest.mark.parametrize("q, reply", [("Chào bạn", "greeting"), ("Cảm ơn", "thanks"), ("Bạn là ai?", "identity"), ("Tạm biệt", "bye"),
                                      ("Hello", "greeting"), ("Thanks a lot", "thanks")])
def test_small_talk(q, reply):
    assert classify.classify(q) == {"category": "small_talk", "danger": False, "reply": reply}


@pytest.mark.parametrize("q", ["Chào bạn, bà bầu nên ăn gì?", "Cảm ơn, còn mất ngủ khi mang thai thì sao?", "Khi nào bé chào đời?"])
def test_small_talk_never_hides_a_real_question(q):
    assert classify.classify(q)["category"] == "general"


@pytest.mark.parametrize("q", ["Giá khám thai ở Thu Cúc bao nhiêu?", "Bệnh viện Thu Cúc ở đâu?", "Gói thai sản Thu Cúc gồm những gì?",
                               "Bảo hiểm có chi trả sinh không?", "Giờ làm việc của phòng khám?", "Số hotline bệnh viện là gì?"])
def test_hospital_information_is_never_guessed(talk, q):
    intent, shown, llm_input = talk(q)
    assert intent == {"intent": "hospital_info"} and llm_input is None
    assert shown == "Giá khám, gói dịch vụ, bảo hiểm, địa chỉ và giờ làm việc của Bệnh viện Thu Cúc: mẹ xem trong app TCI hoặc gọi 1900 xxxx nhé."


def test_follow_ups_after_a_metric(talk):
    talk("Huyết áp lần trước của em là bao nhiêu?")
    intent, shown, _ = talk("Còn lần trước nữa?")
    assert intent == {"intent": "lookup", "topic": "readings", "metric": "Blood pressure"}
    assert shown.startswith("Các lần đo huyết áp gần nhất của mẹ: 150/95 mmHg (26/09/2026 · 20:15); 128/82 mmHg")
    intent, shown, _ = talk("Còn cân nặng thì sao?")
    assert intent == {"intent": "lookup", "topic": "readings", "metric": "Weight"}
    intent, _, llm_input = talk("Giải thích rõ hơn được không?")          # explaining her values is the nurse's job (BR-002)
    assert intent == {"intent": "needs_nurse"} and llm_input is None


def test_switch_metric_keeps_the_period(talk):
    talk("Huyết áp tuần này của em thế nào?")
    intent, shown, _ = talk("Thế còn nhịp tim?")
    assert intent == {"intent": "lookup", "topic": "trend", "metric": "Heart rate", "when": "week"}
    assert shown.startswith("Nhịp tim trong 7 ngày qua:")


def test_explain_after_a_general_answer_sends_the_earlier_turns(talk):
    talk("Bà bầu nên ăn gì để đủ sắt?")
    intent, _, llm_input = talk("Giải thích rõ hơn được không?")
    assert intent == {"intent": "general"}
    assert llm_input[1]["earlier"] == [{"question": "Bà bầu nên ăn gì để đủ sắt?", "answer": "[Sample chatbot answer]"}]


def test_follow_up_with_nothing_to_follow(talk):
    intent, shown, llm_input = talk("Còn lần trước nữa?")
    assert intent == {"intent": "small_talk"} and llm_input is None
    assert shown.startswith("Mẹ hỏi lại đầy đủ giúp mình nhé?")
    assert talk("Thời tiết hôm nay thế nào?")[0] == {"intent": "out_of_scope"}
