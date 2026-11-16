"""T006 — BOT US-1 #1, #3, #4, US-2 #1 - #4, BR-004 (S-031, S-034) with the fake LLM."""
import re

import pytest
from tests.integration.helpers import vi

DANGER = "I have had a little bleeding since this morning, is that okay?"


@pytest.fixture(autouse=True)
def fake_llm(monkeypatch):
    monkeypatch.setenv("MB360_LLM", "fake")      # never call the network from tests


def text(html):
    return re.sub(r"<[^>]+>", " ", html)


def ask(client, uid, q):
    r = client.post(f"/m/{uid}/chat", data={"text": q})
    assert r.status_code == 303
    return r.headers["location"], client.get(r.headers["location"]).text


def test_home_links_to_the_chatbot(client, user_id):
    uid = user_id("tci-000133")
    assert f'href="/m/{uid}/chat"' in client.get(f"/m/{uid}/home").text


def test_welcome_screen(client, user_id):
    page = client.get(f"/m/{user_id('tci-000133')}/chat").text
    for t in map(vi, ("Health chatbot", "Hello, Mom!", "I can answer general questions about pregnancy and baby care.",
                      "The chatbot provides general reference information only and does not replace your doctor's advice.",
                      "Trouble sleeping during pregnancy", "Should I exercise?", "Leg cramps", "Type your question…", "Send")):
        assert t in page, t
    assert "alert" not in text(page).lower()


def test_general_answer_has_the_disclaimer(client, user_id):
    _, page = ask(client, user_id("tci-000133"), "How can I eat beef safely during pregnancy?")
    assert vi("[Sample chatbot answer]") in page
    assert vi("For reference only; does not replace your doctor's advice.") in page


def test_danger_question_and_connect_to_nurse(client, db, user_id, staff_id):
    uid = user_id("tci-000133")
    url, page = ask(client, uid, DANGER)
    for t in (vi("Signs that need medical attention"), vi("You need to be checked right away"), vi("Connect to nurse"), vi("No, thanks"),
              vi("Call the emergency hotline")):
        assert t in page, t
    assert vi("[Sample chatbot answer]") not in page
    form = re.search(r'action="(/m/[^"]+/handoff/[0-9a-f-]{36})"', page).group(1)
    r = client.post(form, data={"choice": "connect"})
    assert r.status_code == 303
    assert vi("Sent to a nurse") in client.get(url).text
    case = db.execute("SELECT case_id FROM CARE_CASE WHERE user_id = ? AND case_source = 'Chatbot'", (uid,)).fetchone()[0]
    nurse = staff_id("Trần Thị B")
    assert f"/staff/{nurse}/cases/{case}" in client.get(f"/staff/{nurse}/cases").text
    assert DANGER in client.get(f"/staff/{nurse}/cases/{case}").text
    assert "alert" not in text(page).lower()


def test_personal_question_without_notice_and_decline(client, db, user_id):
    uid = user_id("tci-000133")
    url, page = ask(client, uid, "I feel tired, is that normal?")
    assert vi("Connect to nurse") in page and vi("Signs that need medical attention") not in page
    form = re.search(r'action="(/m/[^"]+/handoff/[0-9a-f-]{36})"', page).group(1)
    before = db.execute("SELECT COUNT(*) FROM CARE_CASE").fetchone()[0]
    client.post(form, data={"choice": "decline"})
    after_page = client.get(url).text
    assert "1900 xxxx" in after_page and vi("Connect to nurse") + "</button>" not in after_page
    assert db.execute("SELECT COUNT(*) FROM CARE_CASE").fetchone()[0] == before


def test_out_of_scope_is_declined_without_buttons(client, user_id):
    _, page = ask(client, user_id("tci-000133"), "How do I change a car tyre?")
    assert vi("I can only help with pregnancy, prenatal care, nutrition and postpartum wellness. "
              "Could you ask me a pregnancy question?") in page
    assert vi("Connect to nurse") not in page


def test_empty_question_is_refused(client, user_id):
    assert client.post(f"/m/{user_id('tci-000133')}/chat", data={"text": ""}).status_code == 422


def test_lookup_answer_links_to_the_screen(client, user_id):
    """FR-012, BR-006 (D-89, proposed): the app answers from her data, says it does not assess it, links to S-025."""
    uid = user_id("tci-000126")
    _, page = ask(client, uid, "Huyết áp lần trước của em là bao nhiêu?")
    shown = text(page)
    assert "145/92 mmHg" in shown and vi("The chatbot only repeats your data from the app and does not assess it. If you are worried, ask a nurse.") in shown
    assert f'href="/m/{uid}/history?metric=Blood%20pressure"' in page and vi("View in the app") in shown
    assert vi("For reference only; does not replace your doctor's advice.") not in shown     # not an AI answer


def test_small_talk_and_hospital_information_on_the_page(client, user_id):
    """D-95 (proposed): fixed replies in Vietnamese, no AI disclaimer (they are not AI answers)."""
    uid = user_id("tci-000133")
    _, page = ask(client, uid, "Chào bạn")
    assert vi("You're welcome, Mom! Ask me anytime.") not in page
    assert "Chào mẹ!" in text(page) and vi("For reference only; does not replace your doctor's advice.") not in page
    _, page = ask(client, uid, "Giá khám thai ở Thu Cúc bao nhiêu?")
    assert "mẹ xem trong app TCI hoặc gọi 1900 xxxx" in text(page)
