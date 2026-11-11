"""T002 — TML US-4 #1 – #4, FR-013, FR-014, BR-003, BR-006, BR-007 (S-105 and the album page)."""
import re

from tests.integration.helpers import vi


def test_journey_weeks_are_visible_newest_first_and_mark_current(client, user_id):
    path = f"/m/{user_id('tci-000123')}/journey"
    page = client.get(path, params={"stage": "Full journey"}).text
    for label in ("Highlights", "See the timeline", "Week by week"):
        assert vi(label) not in page
    assert "<details" not in page
    weeks = re.findall(r'<section[^>]*data-week="(\d+)"[^>]*>(.*?)</section>', page, re.S)
    numbers = [int(number) for number, _ in weeks]
    assert len(numbers) > 1 and numbers == sorted(numbers, reverse=True)
    assert [int(number) for number, card in weeks if "data-current-week" in card] == [28]
    assert f'data-current-week>{vi("Current")}</span>' in page
    past = client.get(path, params={"stage": "Second trimester"}).text
    assert 'data-week="' in past and "data-current-week" not in past


def test_journey_without_diary_keeps_visits_and_handles_missing_image(client, db, user_id):
    lan = user_id("tci-000123")
    db.execute("DELETE FROM DIARY_IMAGE WHERE diary_id IN (SELECT diary_id FROM DIARY_ENTRY WHERE user_id = ?)", (lan,))
    db.execute("DELETE FROM DIARY_ENTRY WHERE user_id = ?", (lan,))
    db.execute("UPDATE VISIT SET ultrasound_image = 'missing-journey-image.png' WHERE user_id = ?", (lan,))
    response = client.get(f"/m/{lan}/journey", params={"stage": "Second trimester"})
    assert response.status_code == 200
    assert vi("Visit {date}", date="18/08/2026") in response.text
    assert 'src="/media/missing-journey-image.png"' not in response.text
    assert vi("Ultrasound image, {date}", date="18/08/2026") in response.text


def test_reached_stage_without_content_has_empty_state(client, db, user_id):
    lan = user_id("tci-000123")
    db.execute("DELETE FROM DIARY_IMAGE WHERE diary_id IN (SELECT diary_id FROM DIARY_ENTRY WHERE user_id = ?)", (lan,))
    db.execute("DELETE FROM DIARY_ENTRY WHERE user_id = ?", (lan,))
    db.execute("DELETE FROM FAMILY_MESSAGE WHERE user_id = ?", (lan,))
    response = client.get(f"/m/{lan}/journey", params={"stage": "Third trimester"})
    assert response.status_code == 200
    assert vi("Nothing to show for this stage yet.") in response.text
    assert vi("Nothing to export yet.") in response.text


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
    weeks = [int(n) for n in re.findall(r'data-week="(\d+)"', r.text)]
    assert len(weeks) > 1 and weeks == sorted(weeks)
    assert "data-current-week" not in r.text
    assert "data-zoom" not in r.text
    assert 'addEventListener("load"' not in client.get(f"/m/{lan}/journey/album", params={"stage": "Full journey"}).text


def test_album_without_content_goes_back(client, user_id):
    lan = user_id("tci-000125")
    r = client.get(f"/m/{lan}/journey/album", params={"stage": "Third trimester"})
    assert r.status_code == 303 and r.headers["location"].startswith(f"/m/{lan}/journey")


def test_no_due_date_goes_to_setup(client, user_id):
    u07 = user_id("tci-000129")
    r = client.get(f"/m/{u07}/journey")
    assert r.status_code == 303 and r.headers["location"] == f"/m/{u07}/setup"
