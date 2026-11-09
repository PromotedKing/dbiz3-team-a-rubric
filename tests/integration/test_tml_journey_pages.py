"""T002 — TML US-4 #1 – #4, FR-013, FR-014, BR-003, BR-006, BR-007 (S-105 and the album page)."""
from tests.integration.helpers import vi


def test_links_to_the_journey(client, user_id):
    lan = user_id("tci-000123")
    assert f'href="/m/{lan}/journey"' in client.get(f"/m/{lan}/timeline").text
    assert f'href="/m/{lan}/journey"' in client.get(f"/m/{lan}/profile").text


def test_journey_page(client, user_id):
    lan = user_id("tci-000123")
    page = client.get(f"/m/{lan}/journey").text
    for t in (vi("My journey"), vi("First trimester"), vi("Second trimester"), vi("Third trimester"), vi("Full journey"),
              vi("Export PDF album"), "The baby kicked a lot today.", vi("Week {n}", n=28), vi("You are in week {n}", n=28)):
        assert t in page, t
    assert "alert" not in page.lower() and vi("Alert") not in page
    assert 'method="post"' not in page and ">" + vi("Edit") + "<" not in page and ">Delete<" not in page    # BR-006


def test_measurements_come_with_their_report_date(client, user_id):             # BR-003
    page = client.get(f"/m/{user_id('tci-000123')}/journey", params={"stage": "Second trimester"}).text
    for t in (vi("Visit {date}", date="18/08/2026"), vi("From visit"), "27 cm", "480 g", vi("Measurements per ultrasound report dated {date}", date="18/08/2026")):
        assert t in page, t


def test_not_reached_stage_disables_the_export(client, user_id):
    lan = user_id("tci-000125")
    page = client.get(f"/m/{lan}/journey", params={"stage": "Third trimester"}).text
    assert vi("Not reached yet") in page and f'/m/{lan}/journey/album' not in page and vi("Nothing to export yet.") in page


def test_album_page_is_print_ready_and_stores_nothing(client, db, user_id):     # FR-014, BR-007
    lan = user_id("tci-000123")
    before = db.total_changes
    r = client.get(f"/m/{lan}/journey/album", params={"stage": "Full journey", "print": 1})
    assert r.status_code == 200 and db.total_changes == before
    for t in ("Nguyễn Thị Lan", vi("Full journey"), "The baby kicked a lot today.", 'addEventListener("load"', "@media print"):
        assert t in r.text, t
    assert "data-tabbar" not in r.text
    assert 'addEventListener("load"' not in client.get(f"/m/{lan}/journey/album", params={"stage": "Full journey"}).text


def test_album_without_content_goes_back(client, user_id):
    lan = user_id("tci-000125")
    r = client.get(f"/m/{lan}/journey/album", params={"stage": "Third trimester"})
    assert r.status_code == 303 and r.headers["location"].startswith(f"/m/{lan}/journey")


def test_no_due_date_goes_to_setup(client, user_id):
    u07 = user_id("tci-000129")
    r = client.get(f"/m/{u07}/journey")
    assert r.status_code == 303 and r.headers["location"] == f"/m/{u07}/setup"
