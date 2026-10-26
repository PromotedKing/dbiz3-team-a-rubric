"""T004 — ACC FR-004, FR-005, D-72; LMP -> EDD provisional (§10 Q10)."""
from datetime import date

import pytest

from mb360.acc import entry, setup
from tests.acc_helpers import NOW, count, new_identity

TODAY = date(2026, 9, 27)


def test_calculate_from_edd():
    assert setup.calculate("EDD", date(2026, 12, 20), TODAY) == {"edd": date(2026, 12, 20), "week": 28, "day": 0}


def test_calculate_from_lmp():
    assert setup.calculate("LMP", date(2026, 4, 1), TODAY) == {"edd": date(2027, 1, 6), "week": 25, "day": 4}


def form(**kw):
    base = {"date_type": "EDD", "date": "2026-12-20", "height_cm": "", "weight_kg": "", "first_visit_date": ""}
    base.update(kw)
    return base


@pytest.mark.parametrize("kw, field", [
    ({"date": "2026-09-01"}, "date"),                       # due date in the past
    ({"date": "2027-08-01"}, "date"),                       # more than 280 days ahead: week < 0
    ({"date": ""}, "date"),                                 # no date
    ({"date_type": ""}, "date_type"),
    ({"height_cm": "abc"}, "height_cm"),
    ({"weight_kg": "abc"}, "weight_kg"),
    ({"first_visit_date": "2026-10-01"}, "first_visit_date"),   # after today
    ({"first_visit_date": "2026-03-01"}, "first_visit_date"),   # before EDD - 280 days (2026-03-15)
])
def test_invalid_setup(kw, field):
    assert field in setup.validate(form(**kw), TODAY)


def test_valid_setup_has_no_error():
    assert setup.validate(form(height_cm="158.5", weight_kg="57.2", first_visit_date="2026-05-10"), TODAY) == {}


def test_save_writes_profile_and_weight(db):
    uid = entry.agree(db, new_identity(), True, NOW)
    setup.save(db, uid, form(date_type="LMP", date="2026-04-01", height_cm="158.5", weight_kg="57.2", first_visit_date="2026-05-10"), NOW)
    p = db.execute("SELECT * FROM PREGNANCY_PROFILE WHERE user_id = ?", (uid,)).fetchone()
    assert (p["edd"], p["lmp"], p["edd_source"], float(p["height_cm"]), p["first_visit_date"]) == \
        ("2027-01-06", "2026-04-01", "Self-entered", 158.5, "2026-05-10")
    w = db.execute("SELECT * FROM HEALTH_METRIC_RECORD WHERE user_id = ?", (uid,)).fetchall()
    assert len(w) == 1
    assert (w[0]["metric"], w[0]["metric_group"], w[0]["value"], w[0]["unit"], w[0]["source"], w[0]["gestational_week"]) == \
        ("Weight", "Group 1", "57.2", "kg", "Self-entered", 25)


def test_height_and_weight_may_be_empty(db):
    uid = entry.agree(db, new_identity(), True, NOW)
    setup.save(db, uid, form(), NOW)
    assert count(db, "PREGNANCY_PROFILE", "user_id = ?", (uid,)) == 1
    assert count(db, "HEALTH_METRIC_RECORD", "user_id = ?", (uid,)) == 0


def test_invalid_save_writes_nothing(db):
    uid = entry.agree(db, new_identity(), True, NOW)
    with pytest.raises(setup.SetupError) as e:
        setup.save(db, uid, form(date="2026-09-01"), NOW)
    assert "date" in e.value.errors
    assert count(db, "PREGNANCY_PROFILE", "user_id = ?", (uid,)) == 0
