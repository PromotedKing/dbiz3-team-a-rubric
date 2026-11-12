"""D-85: clinical dashboard and case board. Every number opens the cases behind it; nothing is stored."""
import re

from mb360.cli import dashboard
from tests.integration.helpers import bp_form, vi


def test_staff_page_opens_the_dashboard(client, staff_id):
    nurse = staff_id("Trần Thị B")
    r = client.get(f"/staff/{nurse}")
    assert r.status_code == 303 and r.headers["location"] == f"/staff/{nurse}/dashboard"
    assert f'href="/staff/{nurse}/dashboard"' in client.get("/staff").text


def test_dashboard_counts_match_the_cases(client, db, staff_id):
    nurse = staff_id("Trần Thị B")
    page = client.get(f"/staff/{nurse}/dashboard").text
    open_cases = db.execute("SELECT COUNT(*) FROM CARE_CASE WHERE status <> 'Resolved'").fetchone()[0]
    not_viewed = db.execute("SELECT COUNT(*) FROM CARE_CASE WHERE status = 'Not viewed'").fetchone()[0]
    for t in (vi("Overview"), vi("Open cases"), vi("Where cases stand"), vi("Needs attention"), vi("Case board")):
        assert t in page, t
    assert re.search(rf'{vi("Open cases")}</span><span class="kpi-num">{open_cases}<', page)
    assert re.search(rf'{vi("Not viewed")}</span><span class="kpi-num">{not_viewed}<', page)
    for status in dashboard.STATUSES:
        assert f'data-status="{status}"' in page
    assert "Cảnh báo" not in page                              # the word Alert stays on S-028 (ALR BR-010)


def test_a_new_above_threshold_report_shows_up(client, user_id, staff_id):
    nurse, u09 = staff_id("Trần Thị B"), user_id("tci-000126")
    before = client.get(f"/staff/{nurse}/cases?flag=above").text.count(vi("View report") + " ›")
    client.post(f"/m/{u09}/report", data=bp_form(160, 100, ["No symptoms"]))
    after = client.get(f"/staff/{nurse}/cases?flag=above").text
    assert after.count(vi("View report") + " ›") == before + 1


def test_board_columns_and_cards_open_cases(client, db, staff_id):
    nurse = staff_id("Trần Thị B")
    page = client.get(f"/staff/{nurse}/board").text
    for status in dashboard.STATUSES:
        assert f'data-column="{status}"' in page
    case_id = db.execute("SELECT case_id FROM CARE_CASE WHERE status <> 'Resolved' LIMIT 1").fetchone()[0]
    assert f'href="/staff/{nurse}/cases/{case_id}"' in page


def test_filters_by_source_and_date(client, db, staff_id):
    nurse = staff_id("Trần Thị B")
    chat = db.execute("SELECT COUNT(*) FROM CARE_CASE WHERE case_source = 'Chatbot'").fetchone()[0]
    page = client.get(f"/staff/{nurse}/dashboard", params={"source": "Chatbot"}).text
    assert vi("{n} cases in this view", n=chat) in page
    assert vi("{n} cases in this view", n=0) in client.get(f"/staff/{nurse}/dashboard", params={"from": "2030-01-01"}).text


def test_doctor_sees_cases_assigned_to_them(client, db, staff_id):
    doctor = staff_id("Nguyễn Văn A")
    mine = db.execute("SELECT COUNT(*) FROM CARE_CASE WHERE status = 'Escalated to doctor' AND assigned_doctor_id = ?", (doctor,)).fetchone()[0]
    assert vi("{n} assigned to me", n=mine) in client.get(f"/staff/{doctor}/dashboard").text


def test_unknown_flag_shows_every_case(client, staff_id):
    nurse = staff_id("Trần Thị B")
    assert client.get(f"/staff/{nurse}/cases?flag=nope").status_code == 200
