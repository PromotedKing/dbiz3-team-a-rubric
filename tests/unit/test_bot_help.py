"""D-111 (proposed), 26/11/2026: "/help" and "what can I ask?" get a fixed guide (no LLM) listing what the chatbot does,
with example questions the mother can tap; every example is answered the way its group says, and none opens the nurse offer."""
import html
import json
import re

import pytest

from mb360 import ui
from mb360.bot import chat, classify, llm
from tests.acc_helpers import NOW

HELP = {"category": "small_talk", "danger": False, "reply": "help"}


@pytest.fixture(autouse=True)
def fake_llm(monkeypatch):
    monkeypatch.setenv("MB360_LLM", "fake")


@pytest.mark.parametrize("q", ["/help", "help", "Help?", "?", "/HELP ", "trợ giúp", "tro giup", "Hướng dẫn", "menu",
                               "Tôi có thể làm gì ở đây?", "Mình có thể hỏi những gì?", "Cách dùng chatbot này thế nào?",
                               "bạn làm được gì", "Bạn giúp được gì cho mẹ bầu?", "Chatbot có thể giúp gì khi mang thai?",
                               "What can you do?", "What can I ask?", "How do I use this?"])
def test_help_questions(q):
    assert classify.classify(q) == HELP


@pytest.mark.parametrize("q, category", [
    ("Bị ra máu thì làm gì?", "needs_nurse"),                     # a danger sign always wins
    ("Tôi bị đau đầu, bạn giúp được gì?", "needs_nurse"),         # her own health always wins
    ("Tôi có thể làm gì để ngủ ngon khi mang thai?", "general"),  # a real question with "có thể làm gì"
    ("Hướng dẫn cách cho con bú", "general"),                    # "hướng dẫn" alone is a command, inside a question it is not
    ("Huyết áp gần nhất của tôi là bao nhiêu? help", "lookup"),
])
def test_help_never_hides_a_real_question(q, category):
    assert classify.classify(q)["category"] == category


@pytest.mark.parametrize("q, reply", [("Bạn là ai?", "identity"), ("Cảm ơn bạn đã giúp", "thanks"), ("Thanks for your help", "thanks")])
def test_other_small_talk_is_unchanged(q, reply):
    assert classify.classify(q)["reply"] == reply


def test_every_example_is_answered_as_its_group_says():
    expected = {"Pregnancy questions": "general", "Your data in this app": "lookup"}
    for title, _, examples in chat.HELP_GUIDE:
        for q in examples:
            for shown in (q, ui.t(q)):                    # English and the Vietnamese chip text the mother sends
                assert classify.classify(shown)["category"] == expected[title], shown


def test_help_reply_is_fixed_and_fits(db, user_id):
    assert len(chat.HELP_TEXT) <= chat.ANSWER_MAX
    fake = llm.FakeLLM()
    conv = chat.ask(db, user_id("tci-000123"), None, "/help", NOW, fake)
    mother, bot = db.execute("SELECT parsed_intent, text FROM CHAT_MESSAGE WHERE conversation_id = ? ORDER BY rowid", (conv,)).fetchall()
    assert json.loads(mother[0]) == {"intent": "small_talk"} and bot[1] == chat.HELP_TEXT
    assert fake.last_input is None                                       # no LLM call
    assert db.execute("SELECT COUNT(*) FROM AI_RESPONSE_LOG WHERE conversation_id = ?", (conv,)).fetchone()[0] == 0


def test_help_inside_a_conversation_is_not_read_as_a_follow_up(db, user_id):
    from datetime import timedelta
    uid = user_id("tci-000123")
    conv = chat.ask(db, uid, None, "Huyết áp gần nhất của tôi là bao nhiêu?", NOW, llm.FakeLLM())
    chat.ask(db, uid, conv, "Còn hỏi được gì nữa?", NOW + timedelta(minutes=10), llm.FakeLLM())
    assert db.execute("SELECT text FROM CHAT_MESSAGE WHERE conversation_id = ? ORDER BY rowid DESC LIMIT 1", (conv,)).fetchone()[0] == chat.HELP_TEXT


def test_help_guide_on_the_chat_page(client, user_id):
    uid = user_id("tci-000133")
    welcome = client.get(f"/m/{uid}/chat").text
    assert "data-help-hint" in welcome and "/help" in welcome
    r = client.post(f"/m/{uid}/chat", data={"text": "/help"})
    page = html.unescape(client.get(r.headers["location"]).text)
    guide = page[page.index("data-help"):]
    assert ui.t("Here is what I can help with, Mom:") in guide
    for title, what, examples in chat.HELP_GUIDE:
        assert ui.t(title) in guide and ui.t(what) in guide
        for q in examples:
            assert f'data-suggest="{ui.t(q)}"' in guide                  # tap to ask, as on S-031
    assert ui.t("If you have any emergency signs, call {hotline}.", hotline=chat.HOTLINE) in guide
    assert ui.t("For reference only; does not replace your doctor's advice.") not in page   # not an AI answer
    assert not re.search(r"Cảnh báo", page)
