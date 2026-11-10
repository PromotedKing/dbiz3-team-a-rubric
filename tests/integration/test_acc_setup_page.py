"""T006 — ACC US-2 #1 - #6 (S-007 / S-046 pregnancy setup)."""
from mb360.acc import entry
from tests.acc_helpers import NOW, count, new_identity
from tests.integration.helpers import vi


def _new_mother(db):
    return entry.agree(db, new_identity(), True, NOW)


def test_card_from_edd(client, db):
    uid = _new_mother(db)
    page = client.get(f"/m/{uid}/setup", params={"date_type": "EDD", "date": "2026-12-20"}).text
    for text in (vi("Pregnancy setup"), vi("Calculated by the system"), vi("Week {n} + {d} days", n=28, d=0),
                 vi("Today {today} · Due {edd}", today="27/09/2026", edd="20/12/2026"), vi("Date of first antenatal check-up")):
        assert text in page, text


def test_card_from_lmp(client, db):
    uid = _new_mother(db)
    page = client.get(f"/m/{uid}/setup", params={"date_type": "LMP", "date": "2026-04-01"}).text
    assert vi("Week {n} + {d} days", n=25, d=4) in page and vi("Today {today} · Due {edd}", today="27/09/2026", edd="06/01/2027") in page


def test_invalid_post_saves_nothing(client, db):
    uid = _new_mother(db)
    r = client.post(f"/m/{uid}/setup", data={"date_type": "EDD", "date": "2026-09-01"})
    assert r.status_code == 422 and 'data-error-for="date"' in r.text
    assert count(db, "PREGNANCY_PROFILE", "user_id = ?", (uid,)) == 0


def test_valid_post_goes_home(client, db):
    uid = _new_mother(db)
    r = client.post(f"/m/{uid}/setup", data={"date_type": "EDD", "date": "2026-12-20", "height_cm": "", "weight_kg": ""})
    assert r.status_code == 303 and r.headers["location"] == f"/m/{uid}/home"
    assert count(db, "PREGNANCY_PROFILE", "user_id = ?", (uid,)) == 1


def test_setup_is_skipped_when_a_due_date_exists(client, user_id):
    lan = user_id("tci-000123")
    r = client.get(f"/m/{lan}/setup")
    assert r.status_code == 303 and r.headers["location"] == f"/m/{lan}/home"
