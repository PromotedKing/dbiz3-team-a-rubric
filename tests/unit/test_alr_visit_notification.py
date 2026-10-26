"""T005 — ALR FR-019, BR-003: "Visit result" notification (wording S-009 #9), never an "Alert"."""
from mb360.alr import notifications
from tests.alr_status_helpers import NOW


def _lan_visit(db, user_id):
    lan = user_id("tci-000123")
    visit = db.execute("SELECT visit_id FROM VISIT WHERE user_id = ? AND visit_date = '2026-09-15'", (lan,)).fetchone()[0]
    return lan, visit


def test_visit_result_notification(db, user_id):
    lan, visit = _lan_visit(db, user_id)
    nid = notifications.notify_visit_result(db, visit, NOW)
    n = db.execute("SELECT * FROM NOTIFICATION WHERE notification_id = ?", (nid,)).fetchone()
    assert (n["user_id"], n["type"], n["visit_id"], n["case_id"]) == (lan, "Visit result", visit, None)
    assert (n["title"], n["subtitle"]) == ("New visit results available", "Visit 15/09/2026")
    text = f"{n['title']} {n['subtitle']}".lower()
    assert "alert" not in text and "threshold" not in text


def test_switch_off_creates_nothing(db, user_id):
    lan, visit = _lan_visit(db, user_id)
    db.execute("UPDATE NOTIFICATION_PREFERENCE SET new_visit_result = 0 WHERE user_id = ?", (lan,))
    before = db.execute("SELECT COUNT(*) FROM NOTIFICATION").fetchone()[0]
    assert notifications.notify_visit_result(db, visit, NOW) is None
    assert db.execute("SELECT COUNT(*) FROM NOTIFICATION").fetchone()[0] == before
