"""T006 — US-2 #1; FR-001 – FR-003, FR-006, BR-009 (S-029 page)."""
import re

from tests.alr_status_helpers import RPT001, RPT002, RPT010, chatbot_case, report_id
from tests.integration.helpers import bp_form
from tests.integration.helpers import vi


def test_my_reports_page(client, db, user_id):
    lan = user_id("tci-000123")
    page = client.get(f"/m/{lan}/my-reports").text
    assert vi("My reports") in page and 'data-active-status="All"' in page
    assert page.count("data-report-row") == 4
    assert vi("No action needed") in page
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
    assert vi("You have not submitted any reports.") in client.get(f"/m/{user_id('tci-000133')}/my-reports").text


def test_report_navigation_without_duplicate_instructions_link(client, user_id):
    u09 = user_id("tci-000126")
    target = f'href="/m/{u09}/my-reports"'
    assert target not in client.get(f"/m/{u09}/instructions").text
    alert = client.post(f"/m/{u09}/report", data=bp_form(150, 95, ["No symptoms"])).headers["location"]
    assert target in client.get(alert).text
    status = client.post(f"/m/{u09}/report", data=bp_form(120, 80, ["Palpitations"])).headers["location"]
    assert target in client.get(status).text


def test_status_filter_can_return_to_all(client, user_id):
    """The first option stays in the menu, so a status filter can be cleared."""
    page = client.get(f"/m/{user_id('tci-000123')}/my-reports", params={"status": "Resolved"}).text
    option = re.search(r'<select id="report-status".*?(<option value=""[^>]*>)', page, re.S).group(1)
    assert "hidden" not in option


def test_active_instructions_render_in_a_card_after_responses(client, db):
    row = db.execute("""SELECT r.user_id, r.report_id FROM METRIC_REPORT r JOIN CARE_CASE c ON c.metric_report_id = r.report_id
                        JOIN STAFF_RESPONSE s ON s.case_id = c.case_id LIMIT 1""").fetchone()
    path = f"/m/{row['user_id']}/reports/{row['report_id']}"
    db.execute("UPDATE WATCH_FLAG SET active = 0 WHERE user_id = ?", (row["user_id"],))
    page = client.get(path).text
    assert "data-response" in page and "response-instructions" not in page
    db.execute("""INSERT INTO WATCH_FLAG (flag_id, user_id, visit_id, metric, flagged_by, flagged_at, note, template_id, custom_text, active)
                  SELECT '00000000-0000-0000-0000-000000000099', ?, NULL, metric, flagged_by, flagged_at, 'Sample instruction', template_id, custom_text, 1 FROM WATCH_FLAG LIMIT 1""", (row["user_id"],))
    page = client.get(path).text
    assert page.rindex("data-response") < page.index('class="card bl response-instructions"')
    assert "Sample instruction" in page
    assert f'href="/m/{row["user_id"]}/instructions"' not in page
    instructions = page.split('class="card bl response-instructions"', 1)[1].split("</section>", 1)[0]
    assert 'class="sec instruction-latest"' in instructions
    assert f'href="/m/{row["user_id"]}/history?metric=' in instructions
    assert f'href="/m/{row["user_id"]}/report?' not in instructions
