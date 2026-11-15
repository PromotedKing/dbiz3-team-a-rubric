"""Two devices on one session (reported 15/11/2026): the slower device repeats an action the faster one already did.

Before: the repeated action answered with raw JSON ({"detail": …}), which a phone in dark mode shows as white text in the
corner of a black page. Now a repeated action shows the current state, and any remaining error is the themed error page."""
import re

import pytest
from fastapi.testclient import TestClient

from mb360 import tci_booking
from mb360.hlt import dashboard
from mb360.main import create_app
from tests.alr_status_helpers import RPT010, case_of_code
from tests.integration.helpers import vi
from tests.integration.test_tci_booking import booking_form, draft, host  # noqa: F401  (fixture)

DANGER = "Tôi bị ra máu"


@pytest.fixture(autouse=True)
def fake_llm(monkeypatch):
    monkeypatch.setenv("MB360_LLM", "fake")


def not_raw(r):
    """Never the raw error a browser shows as text on a blank page."""
    assert r.headers["content-type"].startswith("text/html"), r.headers["content-type"]
    assert '"detail"' not in r.text


def handoff_form(client, uid):
    r = client.post(f"/m/{uid}/chat", data={"text": DANGER})
    conv = r.headers["location"]
    return conv, re.search(r'action="(/m/[^"]+/handoff/[0-9a-f-]{36})"', client.get(conv).text).group(1)


@pytest.mark.parametrize("second", ["connect", "decline"])
def test_handoff_tapped_on_both_devices(client, db, user_id, second):
    """Device A taps "Connect to nurse"; device B, still showing the offer, taps again: B sees what A chose, one case."""
    uid = user_id("tci-000133")
    conv, form = handoff_form(client, uid)
    assert client.post(form, data={"choice": "connect"}).status_code == 303
    r = client.post(form, data={"choice": second})
    assert r.status_code == 303 and r.headers["location"] == conv
    assert vi("Sent to a nurse") in client.get(conv).text
    assert db.execute("SELECT COUNT(*) FROM CARE_CASE WHERE user_id = ? AND case_source = 'Chatbot'", (uid,)).fetchone()[0] == 1


@pytest.mark.parametrize("action", ["view", "escalate", "close"])
def test_case_action_repeated_from_a_second_screen(client, db, staff_id, action):
    nurse = staff_id("Trần Thị B")
    base = f"/staff/{nurse}/cases/{case_of_code(db, RPT010)}"
    if action == "close":
        client.post(f"{base}/view")
    assert client.post(f"{base}/{action}").status_code == 303
    r = client.post(f"{base}/{action}")
    assert r.status_code == 303 and r.headers["location"] == f"{base}?updated=1"
    assert vi("This case was already updated, maybe on another screen. Its current status is shown below.") in client.get(r.headers["location"]).text


def test_appointment_cancelled_on_both_devices(host, db):  # noqa: F811
    form = booking_form(db)
    host.post("/tci/booking/confirm", data=draft(host, form))
    appointment = db.execute(f"SELECT appointment_id FROM {tci_booking.TABLE} WHERE reason = ?", (form["reason"],)).fetchone()[0]
    for _ in range(2):
        r = host.post(f"/tci/appointments/{appointment}/cancel")
        assert r.status_code == 303 and r.headers["location"] == "/tci/appointments?tab=history"


def test_other_actions_repeated(client, db, user_id):
    uid = user_id("tci-000126")
    for _ in range(2):
        assert client.post(f"/m/{uid}/notices/read-all").status_code == 303
        assert client.post(f"/m/{uid}/setup", data={}).status_code == 303          # profile already set up → Home


def test_both_devices_ask_in_one_conversation(client, db, user_id):
    uid = user_id("tci-000133")
    conv = client.post(f"/m/{uid}/chat", data={"text": "Bà bầu nên ăn gì?"}).headers["location"]
    for q in ("Mẹ bầu nên ngủ tư thế nào?", "Nước ối là gì?"):
        assert client.post(conv, data={"text": q}).status_code == 303
    texts = [r[0] for r in db.execute("SELECT text FROM CHAT_MESSAGE WHERE conversation_id = ? AND sender = 'Mother' ORDER BY sent_at, rowid",
                                      (conv.rsplit("/", 1)[1],))]
    assert texts == ["Bà bầu nên ăn gì?", "Mẹ bầu nên ngủ tư thế nào?", "Nước ối là gì?"]


def test_unknown_item_shows_the_error_page(client, user_id, staff_id):
    uid = user_id("tci-000133")
    r = client.get(f"/m/{uid}/chat/00000000-0000-0000-0000-000000000000")
    assert r.status_code == 404
    not_raw(r)
    assert vi("Could not complete this") in r.text and f'href="/m/{uid}/home"' in r.text
    r = client.get(f"/staff/{staff_id('Trần Thị B')}/cases/unknown")
    assert r.status_code == 404 and "/cases\"" in r.text
    not_raw(r)


def test_unexpected_error_shows_the_error_page(db, user_id, monkeypatch):
    def broken(*args, **kwargs):
        raise RuntimeError("test failure")
    monkeypatch.setattr(dashboard, "load", broken)
    with TestClient(create_app(db), raise_server_exceptions=False) as client:
        r = client.get(f"/m/{user_id('tci-000133')}/health")
    assert r.status_code == 500
    not_raw(r)
    assert vi("Something went wrong. Please try again.") in r.text and "test failure" not in r.text


def test_report_before_the_pregnancy_profile_goes_to_setup(client, mother_without_profile):
    """ACC BR-006: a report needs the week; without a profile both the form and the submit lead to S-007 (was a 500 error)."""
    uid = mother_without_profile
    for r in (client.get(f"/m/{uid}/report?metric=Blood+pressure"),
              client.post(f"/m/{uid}/report", data={"metric": "Blood pressure", "systolic": "120", "diastolic": "80"})):
        assert r.status_code == 303 and r.headers["location"] == f"/m/{uid}/setup"


def test_profile_edit_before_the_pregnancy_profile_goes_to_setup(client, mother_without_profile):
    r = client.post(f"/m/{mother_without_profile}/profile/edit", data={"edd": "2027-02-20", "height_cm": "158"})
    assert r.status_code == 303 and r.headers["location"] == f"/m/{mother_without_profile}/setup"


def test_two_tabs_ask_the_same_danger_question_and_connect(client, db, user_id):
    """Reported 15/11/2026: tab A and tab B both open on the chatbot, both send "chảy máu" and tap "Connect to nurse"."""
    uid = user_id("tci-000133")
    conv_a, form_a = handoff_form(client, uid)
    r = client.post(f"/m/{uid}/chat", data={"text": DANGER})               # tab B, still on the welcome screen
    assert r.status_code == 303 and r.headers["location"] == conv_a
    assert client.post(form_a, data={"choice": "connect"}).status_code == 303
    assert client.post(form_a, data={"choice": "connect"}).status_code == 303   # tab B taps on what it now shows
    assert db.execute("SELECT COUNT(*) FROM CARE_CASE WHERE user_id = ? AND case_source = 'Chatbot'", (uid,)).fetchone()[0] == 1
    assert db.execute("""SELECT COUNT(*) FROM CHAT_MESSAGE m JOIN CONVERSATION c ON c.conversation_id = m.conversation_id
                         WHERE c.user_id = ? AND m.sender = 'Mother' AND m.text = ?""", (uid, DANGER)).fetchone()[0] == 1


def test_general_question_about_a_danger_sign(client, user_id):
    """D-92 (proposed): answered as a general question, with the hotline line under the answer; a plain general answer has none."""
    uid = user_id("tci-000133")
    page = client.get(client.post(f"/m/{uid}/chat", data={"text": "chảy máu là có vấn đề gì, mình hỏi chung"}).headers["location"]).text
    assert vi("[Sample chatbot answer]") in page and vi("Signs that need medical attention") not in page
    assert "data-hotline" in page
    page = client.get(client.post(f"/m/{uid}/chat", data={"text": "Bà bầu nên ăn gì để đủ sắt?"}).headers["location"]).text
    assert "data-hotline" not in page                       # a new conversation with a plain general answer
