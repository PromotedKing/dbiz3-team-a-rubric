"""T005 — ALR FR-018: "Report" notifications for the mother (wording: S-009 #8, #11; §10 Q23)."""
from mb360.alr import notifications
from tests.alr_status_helpers import NOW, RPT002, case_of_code, notifications as rows_of


def _lan(user_id):
    return user_id("tci-000123")


def test_case_created(db, user_id):
    case = case_of_code(db, RPT002)
    before = len(rows_of(db, _lan(user_id)))
    notifications.notify(db, case, "created", NOW)
    new = rows_of(db, _lan(user_id))[before:]
    assert len(new) == 1
    n = new[0]
    assert (n["type"], n["case_id"], n["read_at"]) == ("Report", case, None)
    assert n["title"] == "Your Blood pressure report has been sent to clinical staff"
    assert n["subtitle"] == "150/95 mmHg · Above threshold"


def test_staff_response(db, user_id, staff_id):
    notifications.notify(db, case_of_code(db, RPT002), "response", NOW, staff_id=staff_id("Trần Thị B"))
    assert rows_of(db, _lan(user_id))[-1]["title"] == "Nurse Trần Thị B responded to your Blood pressure report"


def test_status_change(db, user_id):
    notifications.notify(db, case_of_code(db, RPT002), "Viewed", NOW)
    n = rows_of(db, _lan(user_id))[-1]
    assert n["title"] == "Your Blood pressure report is Viewed" and n["subtitle"] == "Report BC-0926-015"


def test_switch_off_creates_nothing(db, user_id):
    db.execute("UPDATE NOTIFICATION_PREFERENCE SET report_response = 0 WHERE user_id = ?", (_lan(user_id),))
    before = len(rows_of(db, _lan(user_id)))
    assert notifications.notify(db, case_of_code(db, RPT002), "created", NOW) is None
    assert len(rows_of(db, _lan(user_id))) == before


def test_lengths_fit_the_schema(db, user_id):
    notifications.notify(db, case_of_code(db, RPT002), "Escalated to doctor", NOW)
    n = rows_of(db, _lan(user_id))[-1]
    assert len(n["title"]) <= 100 and len(n["subtitle"] or "") <= 200
