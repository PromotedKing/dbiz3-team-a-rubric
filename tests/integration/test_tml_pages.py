"""T005 — TML US-1 #1 - #6, US-2 #1 - #6 (S-048, S-051 / S-052)."""
import re

import pytest

from mb360.tml import diary
from tests.integration.helpers import vi

PNG = b"\x89PNG\r\n\x1a\n" + b"\x00" * 64


@pytest.fixture(autouse=True)
def media(tmp_path, monkeypatch):
    monkeypatch.setattr(diary, "MEDIA_DIR", tmp_path)
    return tmp_path


def text(html):
    return re.sub(r"<[^>]+>", " ", html)


def test_home_week_card_opens_the_timeline(client, user_id):
    lan = user_id("tci-000123")
    assert f'href="/m/{lan}/timeline"' in client.get(f"/m/{lan}/home").text


def test_current_week(client, user_id):
    lan = user_id("tci-000123")
    page = client.get(f"/m/{lan}/timeline").text
    for t in (vi("Week {n}", n=28), "27/09/2026 – 03/10/2026", vi("‹ Week {n}", n=27), vi("Week {n} ›", n=29),
              vi("Indicators this week"), "27/09/2026", "57.0 kg", vi("Self-entered"), vi("No visit this week."),
              vi("Messages to Baby") + " · " + vi("Week {n}", n=28), vi("From Mom"), vi("From Dad"),
              vi("Diary") + " · " + vi("Week {n}", n=28), "The baby kicked a lot today.", vi("+ Add diary entry")):
        assert t in page, t
    assert "Size of" not in page and "Tip" not in page                       # D-02, D-04
    assert "alert" not in text(page).lower()


def test_other_weeks(client, user_id):
    lan = user_id("tci-000123")
    w26 = client.get(f"/m/{lan}/timeline", params={"week": 26}).text
    assert vi("Visit {date}", date="15/09/2026") in w26 and vi("From visit") in w26 and "13/09/2026 – 19/09/2026" in w26
    w22 = client.get(f"/m/{lan}/timeline", params={"week": 22}).text
    for t in (vi("Fetal length"), "27 cm", vi("Estimated weight"), "480 g",
              vi("Measurements per ultrasound report dated {date}", date="18/08/2026"), vi("Ultrasound image, {date}", date="18/08/2026")):
        assert t in w22, t
    assert vi("‹ Week {n}", n="") not in client.get(f"/m/{lan}/timeline", params={"week": 0}).text


def test_diary_form(client, user_id):
    lan = user_id("tci-000123")
    page = client.get(f"/m/{lan}/diary/new").text
    for t in (vi("Add diary entry"), vi("Week {n} – current week", n=28), vi("Date {date} (automatic)", date="27/09/2026"),
              vi("Happy"), vi("Calm"), vi("Nervous"), vi("Tired"), vi("Worried"), 'type="file"', vi("Cancel"), vi("Save diary entry")):
        assert t in page, t
    assert f'href="/m/{lan}/timeline"' in page                                # Cancel goes back to S-048


def test_save_diary_entry(client, user_id, media):
    lan = user_id("tci-000123")
    r = client.post(f"/m/{lan}/diary", data={"text": "Short walk today", "mood": "Calm"},
                    files=[("photos", ("walk.png", PNG, "image/png"))])
    assert r.status_code == 303 and r.headers["location"] == f"/m/{lan}/timeline?saved=1"
    page = client.get(r.headers["location"]).text
    assert vi("Diary entry saved") in page and "Short walk today" in page
    assert len(list(media.rglob("*.png"))) == 1


def test_empty_content_is_refused(client, user_id):
    r = client.post(f"/m/{user_id('tci-000123')}/diary", data={"text": "", "mood": ""})
    assert r.status_code == 422 and 'data-error-for="text"' in r.text


def test_no_edit_or_delete_controls(client, user_id):
    page = client.get(f"/m/{user_id('tci-000123')}/timeline").text
    assert ">" + vi("Edit") + "<" not in page and ">Edit<" not in page and ">Delete<" not in page
