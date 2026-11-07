"""D-81: the v1.0.0 mother app: first opening of a mother known to the hospital, Home, Màn 10, session check, chatbot answers."""
from datetime import datetime

import pytest
from fastapi.testclient import TestClient

from mb360 import clock, persona, tci_feed
from mb360.acc import entry, notices
from mb360.bot import classify, llm
from tests.integration.helpers import vi

NOW = datetime(2026, 11, 2, 10, 0)


@pytest.fixture
def app_client(db):
    from mb360.main import create_app

    clock.set(NOW)
    persona.install(db, NOW)
    return TestClient(create_app(db), follow_redirects=False)


def open_from_tci(client, db):
    me = tci_feed.host_account(db)
    return client.post("/tci/open", data={"tci_account_ref": me["tci_account_ref"], "full_name": me["full_name"], "phone": me["phone"],
                                          "date_of_birth": me["date_of_birth"], "sex": "Female", "record_code": me["record_code"]})


def test_first_opening_goes_consent_guide_setup_home(app_client, db):
    consent = open_from_tci(app_client, db)
    assert consent.status_code == 200 and vi("Connect to your TCI account") in consent.text
    me = tci_feed.host_account(db)
    r = app_client.post("/tci/consent", data={"tci_account_ref": me["tci_account_ref"], "full_name": me["full_name"], "phone": me["phone"],
                                              "date_of_birth": me["date_of_birth"], "sex": "Female", "record_code": me["record_code"],
                                              "action": "agree", "agree": "on"})
    assert r.headers["location"] == f"/m/{persona.USER}/guide" and entry.COOKIE in r.cookies
    done = app_client.get(f"/m/{persona.USER}/guide/done")
    assert done.headers["location"] == f"/m/{persona.USER}/setup"
    setup = app_client.get(done.headers["location"]).text
    assert tci_feed.hospital_edd(db, persona.USER) in setup and vi("Week {n} + {d} days", n=24, d=3) in setup
    home = app_client.post(f"/m/{persona.USER}/setup", data={"date_type": "EDD", "date": tci_feed.hospital_edd(db, persona.USER)})
    page = app_client.get(home.headers["location"]).text
    assert ">109<" in page and vi("Next appointment") in page and "09/11/2026 · 08:30" in page and vi("{n} days left", n=7) in page
    assert vi("Your doctor sent {n} notice", n=1) in page


def test_second_opening_goes_straight_home(app_client, db):
    entry.agree(db, dict(tci_feed.host_account(db)), True, NOW)
    db.execute("INSERT INTO PREGNANCY_PROFILE (user_id, edd, lmp, edd_source, height_cm, first_visit_date) VALUES (?, ?, NULL, 'Self-entered', NULL, NULL)",
               (persona.USER, tci_feed.hospital_edd(db, persona.USER)))
    r = open_from_tci(app_client, db)
    assert r.headers["location"] == f"/m/{persona.USER}/home"


def test_answer_from_the_doctor_opens_the_structured_detail(app_client, db):
    db.execute("INSERT INTO PREGNANCY_PROFILE (user_id, edd, lmp, edd_source, height_cm, first_visit_date) VALUES (?, '2027-02-19', NULL, 'Self-entered', NULL, NULL)", (persona.USER,))
    n = next(c["n"] for c in notices.cards_for(db, persona.USER) if c["doctor"] and not c["n"]["read_at"])
    page = app_client.get(f"/m/{persona.USER}/notices/{n['notification_id']}")
    assert page.status_code == 200
    for t in (vi("WHAT YOU REPORTED"), "146/94 mmHg", vi("DOCTOR'S COMMENT"), vi("WHAT YOU NEED TO DO"), vi("Your doctor booked an earlier visit"), vi("Understood"), "04/11/2026 · 08:00"):
        assert t in page.text, t
    assert notices.unread_count(db, persona.USER) == 0


def test_home_counts_answered_cases_not_status_notices(db):
    persona.install(db, NOW)
    case = db.execute("SELECT case_id FROM NOTIFICATION WHERE user_id = ? AND read_at IS NULL", (persona.USER,)).fetchone()[0]
    for i in range(3):
        db.execute("""INSERT INTO NOTIFICATION (notification_id, user_id, type, title, subtitle, created_at, read_at, case_id, visit_id, watch_flag_id, appointment_ref)
                      VALUES (?, ?, 'Report', 'status', NULL, '2026-11-02 09:00', NULL, ?, NULL, NULL, NULL)""", (f"{i:036d}", persona.USER, case))
    assert notices.home_notice(db, persona.USER)[1] == 1


def test_parse_response_keeps_plain_text_as_the_comment():
    assert notices.parse_response("Mẹ yên tâm nhé.") == {"comment": "Mẹ yên tâm nhé.", "todo": [], "follow_up": None}
    assert notices.parse_response("A\n- B\nHẹn khám: C") == {"comment": "A", "todo": ["B"], "follow_up": "C"}


def test_session_belongs_to_one_mother_and_expires(db):
    persona.install(db, NOW)
    token = entry._new_session(db, persona.USER, NOW)
    assert entry.valid_session(db, token, persona.USER, NOW)
    assert not entry.valid_session(db, None, persona.USER, NOW)
    assert not entry.valid_session(db, token, "someone-else", NOW)
    assert not entry.valid_session(db, token, persona.USER, datetime(2026, 11, 3, 10, 0))


def test_no_appointment_card_without_the_host_feed(client, user_id):
    assert vi("Next appointment") not in client.get(f"/m/{user_id('tci-000123')}/home").text


def test_past_appointment_is_not_shown(db):
    persona.install(db, NOW)
    assert tci_feed.next_appointment(db, persona.USER, NOW)["days"] == 7
    assert tci_feed.next_appointment(db, persona.USER, datetime(2026, 12, 1, 10, 0)) is None


@pytest.mark.parametrize("label", ["Trouble sleeping during pregnancy", "Should I exercise?", "Leg cramps"])
def test_suggested_questions_are_general_and_get_an_answer(label):
    question = vi(label)
    assert classify.classify(question)["category"] == "general"
    answer = llm.LocalAnswers().answer(question, {})
    assert answer != llm.LocalAnswers.GENERAL + llm.LocalAnswers.CLOSING and "bác sĩ" in answer


def test_danger_question_never_reaches_the_answers():
    assert classify.classify("Em bị đau bụng dữ dội và có ra máu") == {"category": "needs_nurse", "danger": True}


def test_sample_mother_has_data_only_as_the_schema_allows(db):
    persona.install(db, NOW)
    assert db.execute("PRAGMA foreign_key_check").fetchall() == []
    assert db.execute("SELECT 1 FROM CONSENT_RECORD WHERE user_id = ?", (persona.USER,)).fetchone() is None
    assert db.execute("SELECT 1 FROM PREGNANCY_PROFILE WHERE user_id = ?", (persona.USER,)).fetchone() is None


def test_close_app_ends_the_session_and_clears_the_cookie(app_client, db):
    entry.agree(db, dict(tci_feed.host_account(db)), True, NOW)
    token = entry.latest_session(db, persona.USER)
    app_client.cookies.set(entry.COOKIE, token)
    r = app_client.post(f"/m/{persona.USER}/close")
    assert r.status_code == 303 and r.headers["location"] == "/tci"
    assert 'mb360_session=""' in r.headers["set-cookie"] or "Max-Age=0" in r.headers["set-cookie"]
    from datetime import timedelta
    assert not entry.valid_session(db, token, persona.USER, NOW + timedelta(minutes=1))
    assert entry.valid_session(db, entry._new_session(db, persona.USER, NOW), persona.USER, NOW)      # reopening from TCI starts a new one


def test_ending_a_session_later_uses_the_closing_time(db):
    persona.install(db, NOW)
    token = entry._new_session(db, persona.USER, NOW)
    from datetime import timedelta
    entry.end_session(db, token, persona.USER, NOW + timedelta(minutes=30))
    assert db.execute("SELECT expires_at FROM SESSION WHERE session_token = ?", (token,)).fetchone()[0] == "2026-11-02 10:30"
    assert not entry.valid_session(db, token, persona.USER, NOW + timedelta(minutes=30))
