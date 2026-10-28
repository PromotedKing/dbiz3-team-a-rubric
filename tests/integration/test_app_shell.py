"""D-79 — one app shell for every module: header, 5-tab bar, ✕ → S-083, TCI theme (ui-label-reference §11)."""
import re

import pytest

from mb360.acc import entry
from tests.acc_helpers import NOW, new_identity
from tests.alr_status_helpers import RPT002, report_id
from tests.integration.helpers import bp_form, vi


@pytest.fixture(autouse=True)
def fake_llm(monkeypatch):
    monkeypatch.setenv("MB360_LLM", "fake")


def tabs(page):
    return re.findall(r'data-tab="(\w+)"', page)


def active(page):
    return re.findall(r'class="tab active" href="[^"]+" data-tab="(\w+)"', page)


def mother_pages(lan, db):
    return {f"/m/{lan}/home": "home", f"/m/{lan}/timeline": "home", f"/m/{lan}/diary/new": "home",
            f"/m/{lan}/health": "health", f"/m/{lan}/self-tracked": "health", f"/m/{lan}/instructions": "health",
            f"/m/{lan}/report?metric=Blood%20pressure": "health", f"/m/{lan}/my-reports": "health",
            f"/m/{lan}/reports/{report_id(db, RPT002)}": "health", f"/m/{lan}/chat": "chatbot", f"/m/{lan}/profile": "profile"}


def test_every_mother_screen_has_the_five_tabs(client, db, user_id):
    lan = user_id("tci-000123")
    for url, tab in mother_pages(lan, db).items():
        page = client.get(url).text
        assert tabs(page) == ["home", "health", "appointments", "chatbot", "profile"], url
        assert active(page) == [tab], url
        for path in ("home", "health", "chat", "profile"):
            assert f'href="/m/{lan}/{path}"' in page, (url, path)
        assert f'href="/tci/booking?from={lan}"' in page, url            # Appointments: TCI booking flow (APT BR-003)
        assert "data-close-app" in page and 'id="close-sheet"' in page, url
        assert '<html lang="vi">' in page and "/static/app.css" in page


def test_home_has_no_back_button_and_other_screens_have_one(client, db, user_id):
    lan = user_id("tci-000123")
    assert "data-back" not in client.get(f"/m/{lan}/home").text
    assert 'href="/m/' + lan + '/home" aria-label="' + vi("Back") + '" data-back' in client.get(f"/m/{lan}/health").text


def test_close_sheet_s083(client, user_id):
    page = client.get(f"/m/{user_id('tci-000123')}/home").text
    sheet = page[page.index('id="close-sheet"'):]
    assert vi("Close Mother & Baby 360?") in sheet and vi("You can come back at any time from the TCI app.") in sheet
    assert vi("Stay") in sheet and f'href="/tci">{vi("Close app")}' in sheet


def test_onboarding_screens_have_no_tab_bar(client, db):
    uid = entry.agree(db, new_identity(), True, NOW)
    for url in (f"/m/{uid}/guide", f"/m/{uid}/setup"):
        page = client.get(url).text
        assert "data-tabbar" not in page and "data-back" not in page, url
    assert "data-tabbar" not in client.post("/tci/open", data=new_identity(tci_account_ref="tci-test-002")).text


def test_word_alert_only_on_s028(client, db, user_id):
    """ALR BR-010 / D-22 on the Vietnamese screens: "Cảnh báo" (Alert) only on the Metric alert screen."""
    u09 = user_id("tci-000131")
    alert_word = vi("Alert")
    alert_page = client.get(client.post(f"/m/{u09}/report", data=bp_form(150, 95, ["No symptoms"])).headers["location"]).text
    assert alert_word in alert_page
    status_url = client.post(f"/m/{u09}/report", data=bp_form(120, 80, ["Palpitations"])).headers["location"]   # S-026
    others = [u for u in mother_pages(u09, db) if "/reports/" not in u] + [status_url, "/", "/tci", "/staff"]
    for url in others:
        page = client.get(url)
        assert page.status_code == 200 and alert_word not in page.text, url


def test_appointments_tab_opens_the_tci_booking_flow(client, db, user_id):
    lan = user_id("tci-000123")
    before = db.total_changes
    page = client.get("/tci/booking", params={"from": lan}).text
    assert vi("TCI app booking flow") in page and f'href="/m/{lan}/home"' in page
    assert "data-tabbar" not in page and db.total_changes == before          # nothing stored (APT BR-002)
    assert f'href="/m/' not in client.get("/tci/booking", params={"from": "not-a-user"}).text


def test_profile_tab(client, user_id):
    page = client.get(f"/m/{user_id('tci-000123')}/profile").text
    assert "Nguyễn Thị Lan" in page and vi("Record no. {code}", code="TC-00123") in page and vi("Week {n}", n=28) in page


def test_home_self_tracked_cards(client, user_id):
    page = client.get(f"/m/{user_id('tci-000123')}/home").text            # S-008 #10 - #15
    for t in (vi("Self-tracked metrics"), vi("Weight"), "57.0 kg", "27/09/2026 · 07:30", vi("Sleep"), "7 h 30 min"):
        assert t in page, t
    assert vi("Above threshold") not in page and vi("Normal") not in page    # group 1: no threshold label (SR-003)


def test_theme_tokens_are_served(client):
    css = client.get("/static/app.css")
    assert css.status_code == 200
    for token in ("--color-primary: #00A651", "--color-bg: #F5F5F5", "--status-alert-bg: #FEEDE1", "--radius-card: 16px"):
        assert token in css.text, token


def test_demo_start_page_links_both_sides(client, user_id):
    page = client.get("/").text
    assert 'href="/tci"' in page and 'href="/staff"' in page
    assert f'href="/m/{user_id("tci-000123")}/home"' in page
