"""T002 — ACC FR-025, FR-026; S-009 SR-001 (where a notification opens)."""
import pytest

from mb360.acc import notices
from tests.acc_helpers import NOW


def _add(db, uid, nid, type_="Report", created="2026-09-27 08:00", read=None, case=None, visit=None, flag=None):
    db.execute("""INSERT INTO NOTIFICATION (notification_id, user_id, type, title, subtitle, created_at, read_at, case_id, visit_id, watch_flag_id, appointment_ref)
                  VALUES (?, ?, ?, 'T', NULL, ?, ?, ?, ?, ?, NULL)""", (nid.ljust(36, "0"), uid, type_, created, read, case, visit, flag))
    return nid.ljust(36, "0")


@pytest.fixture
def lan(db, user_id):
    uid = user_id("tci-000123")
    db.execute("DELETE FROM NOTIFICATION")
    return uid


def test_list_is_hers_and_newest_first(db, lan, user_id):
    other = user_id("tci-000131")
    _add(db, lan, "a", created="2026-09-26 08:00")
    _add(db, lan, "b", created="2026-09-27 08:00")
    _add(db, other, "c")
    assert [n["notification_id"][0] for n in notices.list_for(db, lan)] == ["b", "a"]


def test_filter_by_type_and_unread(db, lan):
    _add(db, lan, "a", "Report", read="2026-09-27 08:30")
    _add(db, lan, "b", "Visit result")
    assert [n["notification_id"][0] for n in notices.list_for(db, lan, "Visit result")] == ["b"]
    assert [n["notification_id"][0] for n in notices.list_for(db, lan, "Unread")] == ["b"]
    assert len(notices.list_for(db, lan, "not-a-type")) == 2


def test_unread_count_covers_all_types(db, lan):            # ACC Q16: counts all
    _add(db, lan, "a", "Report")
    _add(db, lan, "b", "Visit result")
    _add(db, lan, "c", "Report", read="2026-09-27 08:30")
    assert notices.unread_count(db, lan) == 2


def test_opening_marks_read_once(db, lan):
    nid = _add(db, lan, "a", created="2026-09-27 08:00")
    notices.open_notice(db, lan, nid, NOW)
    assert db.execute("SELECT read_at FROM NOTIFICATION WHERE notification_id = ?", (nid,)).fetchone()[0] == "2026-09-27 10:00"
    db.execute("UPDATE NOTIFICATION SET read_at = '2026-09-27 09:00' WHERE notification_id = ?", (nid,))
    notices.open_notice(db, lan, nid, NOW)
    assert db.execute("SELECT read_at FROM NOTIFICATION WHERE notification_id = ?", (nid,)).fetchone()[0] == "2026-09-27 09:00"


def test_another_mothers_notification_is_refused(db, lan, user_id):
    nid = _add(db, user_id("tci-000131"), "a")
    assert notices.open_notice(db, lan, nid, NOW) is None
    assert db.execute("SELECT read_at FROM NOTIFICATION WHERE notification_id = ?", (nid,)).fetchone()[0] is None


def test_mark_all_read_only_hers(db, lan, user_id):
    other = user_id("tci-000131")
    _add(db, lan, "a")
    keep = _add(db, lan, "b", read="2026-09-27 09:00")
    theirs = _add(db, other, "c")
    notices.mark_all_read(db, lan, NOW)
    assert notices.unread_count(db, lan) == 0
    assert db.execute("SELECT read_at FROM NOTIFICATION WHERE notification_id = ?", (keep,)).fetchone()[0] == "2026-09-27 09:00"
    assert db.execute("SELECT read_at FROM NOTIFICATION WHERE notification_id = ?", (theirs,)).fetchone()[0] is None


def test_targets(db, lan):
    report = db.execute("SELECT case_id, metric_report_id FROM CARE_CASE WHERE user_id = ? AND metric_report_id IS NOT NULL", (lan,)).fetchone()
    chat = db.execute("SELECT case_id FROM CARE_CASE WHERE user_id = ? AND case_source = 'Chatbot'", (lan,)).fetchone()[0]
    flag = db.execute("SELECT flag_id FROM WATCH_FLAG WHERE user_id = ? LIMIT 1", (lan,)).fetchone()[0]
    visit = db.execute("SELECT visit_id FROM VISIT WHERE user_id = ? LIMIT 1", (lan,)).fetchone()[0]
    base = f"/m/{lan}"
    assert notices.open_notice(db, lan, _add(db, lan, "a", case=report["case_id"]), NOW) == f"{base}/reports/{report['metric_report_id']}"
    assert notices.open_notice(db, lan, _add(db, lan, "b", case=chat), NOW) == f"{base}/cases/{chat}"
    assert notices.open_notice(db, lan, _add(db, lan, "c"), NOW) == f"{base}/my-reports"
    assert notices.open_notice(db, lan, _add(db, lan, "d", "Visit result", visit=visit), NOW).startswith(f"{base}/timeline/day/")
    assert notices.open_notice(db, lan, _add(db, lan, "e", "Instruction reminder", flag=flag), NOW) == f"{base}/instructions"
    assert notices.open_notice(db, lan, _add(db, lan, "f", "Appointment"), NOW) == "/tci/booking"
