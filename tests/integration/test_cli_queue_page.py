"""T009 — US-1 #1 - #4, US-2 #1, BR-005 (S-061 "Cases to handle")."""
from tests.cli_helpers import RPT006, case_by_code
from tests.integration.helpers import vi


def test_staff_selector_lists_the_seed_staff(client):
    page = client.get("/staff").text
    for name in ("Trần Thị B", "Hoàng Thị Yến", "Lê Thị Hạnh", "Nguyễn Văn A", "Phạm Quốc Dũng", "Vũ Minh Hải"):
        assert name in page


def test_nurse_queue_header_and_default_filter(client, staff_id):
    page = client.get(f"/staff/{staff_id('Trần Thị B')}/cases").text
    assert vi("Nurse: {name}", name="Trần Thị B") in page
    assert 'data-active-filter="All"' in page
    assert page.count(vi("View report") + " ›") == 10


def test_doctor_default_filter_and_notifications(client, staff_id):
    page = client.get(f"/staff/{staff_id('Nguyễn Văn A')}/cases").text
    assert vi("Dr. {name}", name="Nguyễn Văn A") in page
    assert 'data-active-filter="Escalated to doctor"' in page
    assert page.count(vi("View report") + " ›") == 1
    assert '<span class="badge">1</span>' in page


def test_filter_and_empty_state(client, db, staff_id):
    nurse = staff_id("Trần Thị B")
    assert client.get(f"/staff/{nurse}/cases", params={"status": "Not viewed"}).text.count(vi("View report") + " ›") == 4
    db.execute("UPDATE CARE_CASE SET status = 'Not viewed' WHERE status = 'Viewed'")
    assert vi("No cases to handle.") in client.get(f"/staff/{nurse}/cases", params={"status": "Viewed"}).text


def test_view_report_opens_the_case(client, db, staff_id):
    nurse, case = staff_id("Trần Thị B"), case_by_code(db, RPT006)
    assert f'href="/staff/{nurse}/cases/{case}"' in client.get(f"/staff/{nurse}/cases").text
