"""D-79, D-80 — one app in the look of the UI package (screens/ui-final): tabs, header, S-083, and what the package may not change."""
import re

import pytest

from mb360.acc import entry
from tests.acc_helpers import NOW, new_identity
from tests.alr_status_helpers import RPT002, report_id
from tests.integration.helpers import bp_form, vi

TABS = ["home", "timeline", "chatbot", "doctor", "profile"]


@pytest.fixture(autouse=True)
def fake_llm(monkeypatch):
    monkeypatch.setenv("MB360_LLM", "fake")


def tabs(page):
    return re.findall(r'data-tab="(\w+)"', page)


def active(page):
    return re.findall(r'class="tab on" href="[^"]+" data-tab="(\w+)"', page)


def test_the_five_root_screens_have_the_tab_bar(client, user_id):
    lan = user_id("tci-000123")
    for path, tab in (("home", "home"), ("timeline", "timeline"), ("chat", "chatbot"), ("notices", "doctor"), ("profile", "profile")):
        page = client.get(f"/m/{lan}/{path}").text
        assert tabs(page) == TABS, path
        assert active(page) == [tab], path
        for target in ("home", "timeline", "chat", "notices", "profile"):
            assert f'href="/m/{lan}/{target}"' in page, (path, target)
        assert '<html lang="vi">' in page and "/static/tci.css" in page


def test_child_screens_have_back_and_no_tab_bar(client, db, user_id):
    lan = user_id("tci-000123")
    for path in ("health", "self-tracked", "instructions", "report?metric=Blood%20pressure", "my-reports", "diary/new",
                 f"reports/{report_id(db, RPT002)}"):
        page = client.get(f"/m/{lan}/{path}").text
        assert "data-tabbar" not in page and "data-back" in page, path


def test_home_has_close_and_no_back(client, user_id):
    page = client.get(f"/m/{user_id('tci-000123')}/home").text
    assert "data-back" not in page and "data-close-app" in page
    dialog = page[page.index('id="close-sheet"'):]
    assert vi("Close Mother & Baby 360?") in dialog and vi("You will return to the TCI app. Your data stays saved, and you do not need to sign in next time.") in dialog
    assert vi("Stay") in dialog and 'action="/m/' in dialog and f'>{vi("Close app")}</button>' in dialog


def test_onboarding_screens_have_no_tab_bar(client, db):
    uid = entry.agree(db, new_identity(), True, NOW)
    for url in (f"/m/{uid}/guide", f"/m/{uid}/setup"):
        page = client.get(url).text
        assert "data-tabbar" not in page and "data-back" not in page, url
    assert "data-tabbar" not in client.post("/tci/open", data=new_identity(tci_account_ref="tci-test-002")).text


def test_unread_badge_counts_the_mothers_notifications(client, db, user_id):
    lan = user_id("tci-000123")
    db.execute("UPDATE NOTIFICATION SET read_at = '2026-09-27 10:00' WHERE user_id = ?", (lan,))
    assert "data-unread" not in client.get(f"/m/{lan}/home").text
    client.post(f"/m/{lan}/report", data=bp_form(150, 95, ["No symptoms"]))          # ALR FR-018 writes one notification
    assert '<span class="badge" data-unread>1</span>' in client.get(f"/m/{lan}/home").text


def test_word_alert_only_on_s028(client, db, user_id):
    """ALR BR-010 / D-22 on the Vietnamese screens: "Cảnh báo" (Alert) only on the Metric alert screen."""
    u09 = user_id("tci-000126")
    alert_word = vi("Alert")
    alert_page = client.get(client.post(f"/m/{u09}/report", data=bp_form(150, 95, ["No symptoms"])).headers["location"]).text
    assert alert_word in alert_page
    status_url = client.post(f"/m/{u09}/report", data=bp_form(120, 80, ["Palpitations"])).headers["location"]
    for path in ("home", "timeline", "chat", "notices", "profile", "health", "self-tracked", "instructions",
                 "report?metric=Blood%20pressure", "my-reports", "diary/new"):
        page = client.get(f"/m/{u09}/{path}")
        assert page.status_code == 200 and alert_word not in page.text, path
    for url in (status_url, "/", "/tci", "/tci/booking", "/staff", "/session-expired"):
        assert alert_word not in client.get(url).text, url


# What the UI package may not change (D-80, screens/ui-final/README.md U3 – U8)

def test_s023_and_s026_stay_reachable(client, db, user_id):
    lan = user_id("tci-000123")
    assert f'href="/m/{lan}/health"' in client.get(f"/m/{lan}/home").text
    my_reports = client.get(f"/m/{lan}/my-reports").text
    assert f'href="/m/{lan}/reports/{report_id(db, RPT002)}"' in my_reports
    assert vi("Handling progress") in client.get(f"/m/{lan}/reports/{report_id(db, RPT002)}").text


def test_a_report_is_not_described_as_going_straight_to_the_doctor(client, user_id):
    lan = user_id("tci-000123")
    page = client.get(f"/m/{lan}/report", params={"metric": "Blood pressure"}).text
    assert "chuyển ngay cho bác sĩ" not in page and "Bác sĩ xem và trả lời" not in page
    assert vi("Clinical staff view and respond under") in page


def test_handoff_keeps_the_decline_button_and_promises_no_call_back(client, user_id):
    uid = user_id("tci-000133")
    page = client.get(client.post(f"/m/{uid}/chat", data={"text": "I have had a little bleeding since this morning, is that okay?"}).headers["location"]).text
    assert vi("Connect to nurse") in page and vi("No, thanks") in page
    assert "gọi lại" not in page


def test_alert_shows_only_the_template_guidance(client, db, user_id):
    u04 = user_id("tci-000126")                                          # W07: no template, no custom text (BR-013)
    page = client.get(client.post(f"/m/{u04}/report", data=bp_form(150, 95, ["No symptoms"])).headers["location"]).text
    assert "nghiêng trái" not in page                                    # sample text of the package (U8)
    default = db.execute("SELECT content FROM GUIDANCE_TEMPLATE WHERE is_default = 1").fetchone()[0]
    assert default in page


def test_report_tabs_show_only_active_instructions(client, user_id):
    page = client.get(f"/m/{user_id('tci-000123')}/report", params={"metric": "Blood pressure"}).text     # D-11, U16
    assert 'name="metric" value="Blood pressure"' in page and 'name="metric" value="Symptom"' in page
    assert 'name="metric" value="Urine protein"' not in page


# Screens

def test_home_shows_the_due_date_card_and_metrics(client, user_id):
    page = client.get(f"/m/{user_id('tci-000123')}/home").text
    for t in (vi("Due date"), "20/12/2026", ">84<", vi("days to go"), vi("Week {n} + {d} days", n=28, d=0), vi("Third trimester"),
              vi("Report metric / symptom"), vi("My metrics"), vi("Weight"), ">57.0<", vi("Metric history")):
        assert t in page, t
    weight = page[page.index(">57.0<") - 400:page.index(">57.0<") + 400]
    assert vi("Above threshold") not in weight and vi("Normal") not in weight    # group 1: no threshold label (SR-003)


def test_home_report_button_opens_a_metric_from_the_instructions(client, user_id):
    lan, u06 = user_id("tci-000123"), user_id("tci-000128")
    assert f'href="/m/{lan}/report?metric=Blood%20pressure"' in client.get(f"/m/{lan}/home").text
    assert f'href="/m/{u06}/report?metric=Symptom"' in client.get(f"/m/{u06}/home").text          # no instruction


def test_book_tab_of_the_tci_host_stores_nothing(client, db):
    before = db.total_changes
    page = client.get("/tci/booking").text
    assert vi("TCI app booking flow") in page and db.total_changes == before    # APT BR-002
    assert 'href="/tci/booking"' in client.get("/tci").text


def test_session_expired(client):
    page = client.get("/session-expired").text
    assert vi("Session expired") in page and vi("Back to TCI app") in page and "data-tabbar" not in page


def test_profile_tab(client, user_id):
    page = client.get(f"/m/{user_id('tci-000123')}/profile").text
    assert "Nguyễn Thị Lan" in page and "TC-00123" in page and vi("{w} weeks {d} days", w=28, d=0) in page


def test_theme_tokens_are_served(client):
    css = client.get("/static/tci.css")
    assert css.status_code == 200
    for token in ("--p:#00A651", "--bg:#F5F5F5", "--al-bg:#FEEDE1", "border-radius:16px"):
        assert token in css.text, token
    assert client.get("/static/staff.css").status_code == 200


def test_the_app_starts_on_the_tci_home(client):
    r = client.get("/")
    assert r.status_code == 303 and r.headers["location"] == "/tci"
