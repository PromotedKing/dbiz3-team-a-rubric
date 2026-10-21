"""T006 — US-2 #1; FR-001 – FR-003, FR-006, BR-009 (S-029 page)."""
from tests.alr_status_helpers import RPT001, RPT002, RPT010, chatbot_case, report_id
from tests.integration.helpers import bp_form


def test_my_reports_page(client, db, user_id):
    lan = user_id("tci-000123")
    page = client.get(f"/m/{lan}/my-reports").text
    assert "My reports" in page and 'data-active-status="All"' in page
    assert page.count("data-report-row") == 4
    assert "No action needed" in page
    assert f'href="/m/{lan}/reports/{report_id(db, RPT001)}"' not in page          # no link without a status
    assert f'href="/m/{lan}/reports/{report_id(db, RPT002)}"' in page
    assert f'href="/m/{lan}/reports/{report_id(db, RPT010)}"' in page
    assert f'href="/m/{lan}/cases/{chatbot_case(db, lan)}"' in page
    assert "alert" not in page.lower()


def test_filters(client, user_id):
    lan = user_id("tci-000123")
    assert client.get(f"/m/{lan}/my-reports", params={"status": "Resolved"}).text.count("data-report-row") == 1
    assert client.get(f"/m/{lan}/my-reports", params={"type": "Chatbot"}).text.count("data-report-row") == 1


def test_empty_state(client, user_id):
    assert "You have not submitted any reports." in client.get(f"/m/{user_id('tci-000129')}/my-reports").text


def test_links_to_my_reports(client, user_id):
    u09 = user_id("tci-000131")
    target = f'href="/m/{u09}/my-reports"'
    assert target in client.get(f"/m/{u09}/instructions").text
    alert = client.post(f"/m/{u09}/report", data=bp_form(150, 95, ["No symptoms"])).headers["location"]
    assert target in client.get(alert).text
    status = client.post(f"/m/{u09}/report", data=bp_form(120, 80, ["Palpitations"])).headers["location"]
    assert target in client.get(status).text
