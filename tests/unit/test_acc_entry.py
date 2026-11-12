"""T003 — ACC FR-015, FR-011, BR-004, BR-006, BR-007; DM-18, DM-41 defaults (§10 Q22)."""
from datetime import datetime, timedelta

import pytest

from mb360.acc import entry
from tests.acc_helpers import NOW, count, new_identity, seed_identity

TABLES = ("USER_ACCOUNT", "CONSENT_RECORD", "NOTIFICATION_PREFERENCE", "SESSION")


def snapshot(db):
    return {t: count(db, t) for t in TABLES}


def test_first_opening_asks_for_consent_and_writes_nothing(db):
    before = snapshot(db)
    assert entry.open_subapp(db, new_identity(), NOW) == ("consent", None)
    assert snapshot(db) == before


def test_non_female_account_gets_the_notice_and_nothing_is_written(db):
    before = snapshot(db)
    assert entry.open_subapp(db, new_identity(sex="Male"), NOW) == ("not_female", None)
    assert snapshot(db) == before


def test_returning_mother_goes_home_with_a_session_and_a_refreshed_copy(db):
    ident = seed_identity(db, "tci-000123")
    ident["phone"] = "0900000177"
    outcome, uid = entry.open_subapp(db, ident, NOW)
    assert outcome == "home"
    assert db.execute("SELECT phone FROM USER_ACCOUNT WHERE user_id = ?", (uid,)).fetchone()[0] == "0900000177"   # DM-18
    s = db.execute("SELECT * FROM SESSION WHERE user_id = ? ORDER BY created_at DESC, rowid DESC", (uid,)).fetchone()
    fmt = "%Y-%m-%d %H:%M"
    assert s["role"] == "Mother" and s["created_at"] == "2026-09-27 10:00"
    assert datetime.strptime(s["expires_at"], fmt) - datetime.strptime(s["created_at"], fmt) == timedelta(hours=12)


def test_returning_mother_without_due_date_goes_to_setup(db, mother_without_profile):
    assert entry.open_subapp(db, seed_identity(db, "tci-000133"), NOW) == ("setup", mother_without_profile)


def test_unticked_consent_is_refused(db):
    before = snapshot(db)
    with pytest.raises(entry.EntryError):
        entry.agree(db, new_identity(), False, NOW)
    assert snapshot(db) == before


def test_agree_creates_account_consent_preferences_and_session(db):
    uid = entry.agree(db, new_identity(), True, NOW)
    u = db.execute("SELECT * FROM USER_ACCOUNT WHERE user_id = ?", (uid,)).fetchone()
    assert (u["tci_account_ref"], u["full_name"], u["date_of_birth"], u["sex"], u["role"], u["record_code"]) == \
        ("tci-test-001", "Trịnh Thị Test", "1997-05-20", "Female", "Mother", "TC-09999")
    c = db.execute("SELECT * FROM CONSENT_RECORD WHERE user_id = ?", (uid,)).fetchone()
    assert (c["accepted"], c["tci_data_permission"], c["terms_version"], c["accepted_at"]) == (1, 1, None, "2026-09-27 10:00")
    p = db.execute("SELECT * FROM NOTIFICATION_PREFERENCE WHERE user_id = ?", (uid,)).fetchone()
    assert (p["report_response"], p["new_visit_result"], p["appointment_reminder"], p["watch_flag_reminder"]) == (1, 1, 1, 0)
    assert count(db, "SESSION", "user_id = ?", (uid,)) == 1
    assert entry.open_subapp(db, new_identity(), NOW)[0] == "setup"          # no due date yet (BR-006)


def test_agreeing_twice_does_not_create_a_second_account(db):
    first = entry.agree(db, new_identity(), True, NOW)
    second = entry.agree(db, new_identity(), True, NOW + timedelta(minutes=1))
    assert first == second
    assert count(db, "USER_ACCOUNT", "tci_account_ref = 'tci-test-001'") == 1
