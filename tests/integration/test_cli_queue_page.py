"""T009 — US-1 #1 - #4, US-2 #1, BR-005 (S-061 "Cases to handle")."""
from tests.cli_helpers import case_by_code
from tests.integration.helpers import vi


def test_staff_page_is_a_sign_in_form_not_a_list_of_staff(client):
    """D-107 (T-02): /staff no longer lists the seed staff to pick from."""
    page = client.get("/staff").text
    assert "data-staff-login" in page
    for name in ("Trần Thị B", "Hoàng Thị Yến", "Lê Thị Hạnh", "Nguyễn Văn A", "Phạm Quốc Dũng", "Vũ Minh Hải"):
        assert name not in page


def test_nurse_queue_header_and_default_filter(client, db, staff_id):
    """D-102 (spec-CLI §10 Q5): the nurse's list opens on "Not viewed", the cases waiting for her; "All" is one click away."""
    nurse = staff_id("Trần Thị B")
    page = client.get(f"/staff/{nurse}/cases").text
    assert vi("Nurse: {name}", name="Trần Thị B") in page
    assert 'data-active-filter="Not viewed"' in page
    assert page.count(vi("View report") + " ›") == db.execute("SELECT COUNT(*) FROM CARE_CASE WHERE status = 'Not viewed'").fetchone()[0]
    page = client.get(f"/staff/{nurse}/cases", params={"status": "All"}).text
    assert page.count(vi("View report") + " ›") == db.execute("SELECT COUNT(*) FROM CARE_CASE").fetchone()[0]


def test_doctor_default_filter_and_notifications(client, staff_id):
    page = client.get(f"/staff/{staff_id('Nguyễn Văn A')}/cases").text
    assert vi("Dr. {name}", name="Nguyễn Văn A") in page
    assert 'data-active-filter="Escalated to doctor"' in page
    assert page.count(vi("View report") + " ›") == 1
    assert '<span class="badge">1</span>' in page


def test_filter_and_empty_state(client, db, staff_id):
    nurse = staff_id("Trần Thị B")
    expected = db.execute("SELECT COUNT(*) FROM CARE_CASE WHERE status = 'Not viewed'").fetchone()[0]
    assert client.get(f"/staff/{nurse}/cases", params={"status": "Not viewed"}).text.count(vi("View report") + " ›") == expected
    db.execute("UPDATE CARE_CASE SET status = 'Not viewed' WHERE status = 'Viewed'")
    assert vi("No cases to handle.") in client.get(f"/staff/{nurse}/cases", params={"status": "Viewed"}).text


def test_view_report_opens_the_case(client, db, staff_id, boundary_case):
    nurse, case = staff_id("Trần Thị B"), boundary_case
    assert f'href="/staff/{nurse}/cases/{case}"' in client.get(f"/staff/{nurse}/cases").text


def test_nurse_default_view_is_not_viewed_by_priority(client, db, staff_id):
    """D-102 + D-104: "Not viewed" combined with "Sort: Priority" — above threshold first, then the longest wait."""
    from mb360.cli import queue
    nurse = staff_id("Trần Thị B")
    rows = queue.list_cases(db, "Not viewed", viewer=nurse, order=queue.PRIORITY)
    page = client.get(f"/staff/{nurse}/cases").text
    positions = [page.index(f'/cases/{r["case_id"]}') for r in rows]
    assert positions == sorted(positions) and len(rows) >= 2
    assert vi("Sort: Priority") in page
