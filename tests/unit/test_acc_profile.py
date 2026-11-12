"""T001 — ACC US-3, FR-017, FR-020, FR-022, FR-023, BR-003; S-010 switches."""
import pytest

from mb360.acc import profile
from tests.acc_helpers import NOW


def _pp(db, uid):
    return db.execute("SELECT * FROM PREGNANCY_PROFILE WHERE user_id = ?", (uid,)).fetchone()


def test_load_returns_the_read_only_profile(db, user_id):
    d = profile.load(db, user_id("tci-000123"), NOW)
    assert d["week"] == 28 and d["week_day"] == 0 and d["edd"] == "2026-12-20"
    assert d["phone"].count("•") == 3
    assert d["link"]["status"] in ("Linked", "Pending") and d["link"]["facility"]
    assert d["consent"] is True
    assert d["instructions"] == ["Blood pressure", "Blood glucose"]
    assert d["height_cm"] is not None


def test_mother_without_profile_has_no_week(db, mother_without_profile):
    d = profile.load(db, mother_without_profile, NOW)
    assert d["week"] is None and d["edd"] is None


def test_the_latest_link_request_decides(db, older_pending_link):
    assert profile.is_linked(db, older_pending_link)


def test_mask_phone():
    assert profile.mask_phone("0912345678") == "0912 ••• 678"
    assert profile.mask_phone("") == ""


def test_br003_linked_due_date_cannot_be_changed(db):
    uid = db.execute("SELECT user_id FROM USER_ACCOUNT WHERE tci_account_ref = ?", ("tci-000123",)).fetchone()[0]
    before = _pp(db, uid)["edd"]
    profile.save(db, uid, {"edd": "2027-01-15", "height_cm": "170"}, NOW)
    after = _pp(db, uid)
    assert after["edd"] == before and float(after["height_cm"]) == 170


def test_pending_due_date_can_be_changed_and_clears_the_lmp(db, pending_mother):
    uid = pending_mother
    db.execute("UPDATE PREGNANCY_PROFILE SET lmp = '2026-03-01' WHERE user_id = ?", (uid,))
    profile.save(db, uid, {"edd": "2027-01-15", "height_cm": ""}, NOW)
    after = _pp(db, uid)
    assert after["edd"] == "2027-01-15" and after["lmp"] is None and after["height_cm"] is None and after["edd_source"] == "Self-entered"


def test_unchanged_due_date_keeps_the_lmp(db, pending_mother):
    uid = pending_mother
    edd = _pp(db, uid)["edd"]
    db.execute("UPDATE PREGNANCY_PROFILE SET lmp = '2026-03-01' WHERE user_id = ?", (uid,))
    profile.save(db, uid, {"edd": edd, "height_cm": "160"}, NOW)
    assert _pp(db, uid)["lmp"] == "2026-03-01"


@pytest.mark.parametrize("form, field", [
    ({"edd": "2020-01-01", "height_cm": ""}, "edd"),      # past
    ({"edd": "2030-01-01", "height_cm": ""}, "edd"),      # week outside 0 – 42
    ({"edd": "", "height_cm": ""}, "edd"),
    ({"edd": "2027-01-15", "height_cm": "abc"}, "height_cm"),
])
def test_invalid_values_write_nothing(db, form, field, pending_mother):
    uid = pending_mother
    before = dict(_pp(db, uid))
    with pytest.raises(profile.ProfileError) as e:
        profile.save(db, uid, form, NOW)
    assert field in e.value.errors
    assert dict(_pp(db, uid)) == before


def test_linked_height_error_writes_nothing(db):
    uid = db.execute("SELECT user_id FROM USER_ACCOUNT WHERE tci_account_ref = ?", ("tci-000123",)).fetchone()[0]
    before = dict(_pp(db, uid))
    with pytest.raises(profile.ProfileError):
        profile.save(db, uid, {"height_cm": "tall"}, NOW)
    assert dict(_pp(db, uid)) == before


def test_switches_save_immediately(db, user_id):
    uid = user_id("tci-000123")
    profile.set_switch(db, uid, "watch_flag_reminder", True, NOW)
    p = profile.preferences(db, uid)
    assert p["watch_flag_reminder"] == 1
    assert db.execute("SELECT updated_at FROM NOTIFICATION_PREFERENCE WHERE user_id = ?", (uid,)).fetchone()[0] == "2026-09-27 10:00"
    profile.set_switch(db, uid, "watch_flag_reminder", False, NOW)
    assert profile.preferences(db, uid)["watch_flag_reminder"] == 0


@pytest.mark.parametrize("key", ["report_response", "user_id", "x; DROP TABLE USER_ACCOUNT"])
def test_locked_hidden_and_unknown_switches_are_refused(db, user_id, key):
    uid = user_id("tci-000123")
    before = dict(profile.preferences(db, uid))
    with pytest.raises(profile.ProfileError):
        profile.set_switch(db, uid, key, False, NOW)
    assert dict(profile.preferences(db, uid)) == before


def test_missing_preference_row_uses_the_defaults(db, user_id):
    uid = user_id("tci-000123")
    db.execute("DELETE FROM NOTIFICATION_PREFERENCE WHERE user_id = ?", (uid,))
    assert dict(profile.preferences(db, uid)) == {"report_response": 1, "new_visit_result": 1, "appointment_reminder": 1, "watch_flag_reminder": 0}
    profile.set_switch(db, uid, "new_visit_result", False, NOW)
    assert profile.preferences(db, uid)["new_visit_result"] == 0 and profile.preferences(db, uid)["report_response"] == 1
