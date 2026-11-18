"""BR-012 (D-98, proposed) — a nurse may not close a must-escalate case; escalating is the only way on.

"Above threshold" comes from THRESHOLD_RULE (never a number written in a test); the chatbot's danger
flag is read through CARE_CASE.`chat_message_id` → CHAT_MESSAGE.`is_risk` (spec-CLI §10 Q24).
"""
import pytest

from mb360.alr import cases, reports, thresholds
from mb360.cli import actions

from tests.cli_helpers import NOW


def make_case(db, user, systolic, diastolic, symptoms=()):
    report = reports.store_report(db, user, {
        "metric": "Blood pressure", "systolic": systolic, "diastolic": diastolic,
        "measured_at": "2026-09-27T07:00", "symptoms": list(symptoms),
    }, NOW)
    case = cases.open_case(db, user, report["report_id"], "Metric report", NOW)
    db.commit()
    return case


def label_of(db, case_id):
    row = db.execute(
        """SELECT h.metric, h.value, h.glucose_context FROM CARE_CASE c
           JOIN METRIC_REPORT r ON r.report_id = c.metric_report_id
           JOIN HEALTH_METRIC_RECORD h ON h.record_id = r.health_metric_record_id WHERE c.case_id = ?""",
        (case_id,)).fetchone()
    return thresholds.evaluate(db, row["metric"], row["value"], row["glucose_context"])


# ---------------------------------------------------------------- which cases must be escalated

def test_above_threshold_report_must_be_escalated(db, assigned_mother):
    case = make_case(db, assigned_mother, "150", "95")
    assert label_of(db, case) == thresholds.ABOVE
    assert actions.must_escalate(db, case) == "above"


def test_a_normal_report_may_still_be_closed_by_the_nurse(db, assigned_mother):
    case = make_case(db, assigned_mother, "118", "76")
    assert label_of(db, case) == thresholds.NORMAL
    assert actions.must_escalate(db, case) is None


def test_a_symptom_report_has_no_threshold_label_so_it_is_not_must_escalate(db, assigned_mother):
    """BR-005: no measured value, no label — the nurse keeps the decision (BR-001)."""
    report = reports.store_report(db, assigned_mother, {"metric": "Symptom", "symptoms": ["Palpitations"]}, NOW)
    case = cases.open_case(db, assigned_mother, report["report_id"], "Symptom", NOW)
    db.commit()
    assert actions.must_escalate(db, case) is None


def test_a_chatbot_case_flagged_as_danger_must_be_escalated(db):
    """The flag is on the Chat Message, reached through the case (§10 Q24)."""
    found = {}
    for row in db.execute("""SELECT c.case_id, m.is_risk FROM CARE_CASE c
                             JOIN CHAT_MESSAGE m ON m.message_id = c.chat_message_id
                             WHERE c.case_source = 'Chatbot'"""):
        found[bool(row["is_risk"])] = row["case_id"]
    assert found, "the seed has at least one chatbot case"
    for is_risk, case_id in found.items():
        assert actions.must_escalate(db, case_id) == ("danger" if is_risk else None)


# ---------------------------------------------------------------- what the nurse may do

@pytest.mark.parametrize("status_steps", [(), ("view",)])
def test_nurse_cannot_close_an_above_threshold_case(db, assigned_mother, staff_id, status_steps):
    """Not viewed and Viewed alike: "Close case" is gone, "Escalate to doctor" stays (BR-012)."""
    nurse = staff_id("Trần Thị B")
    case = make_case(db, assigned_mother, "150", "95")
    for _ in status_steps:
        actions.mark_viewed(db, case, nurse, NOW)
    can = actions.allowed(db, case, nurse)
    assert "close" not in can and "escalate" in can and "guidance" in can


def test_closing_it_anyway_is_refused_and_writes_nothing(db, assigned_mother, staff_id):
    nurse = staff_id("Trần Thị B")
    case = make_case(db, assigned_mother, "150", "95")
    before = db.execute("SELECT COUNT(*) FROM CASE_STATUS_HISTORY").fetchone()[0]
    with pytest.raises(actions.ActionError) as e:
        actions.close_case(db, case, nurse, NOW)
    assert e.value.status == 403 and "above threshold" in e.value.message
    assert db.execute("SELECT status, closed_at FROM CARE_CASE WHERE case_id = ?", (case,)).fetchone()["status"] == "Not viewed"
    assert db.execute("SELECT COUNT(*) FROM CASE_STATUS_HISTORY").fetchone()[0] == before


def test_the_nurse_can_still_escalate_it(db, assigned_mother, staff_id):
    """BR-012 narrows BR-001; it never blocks the way on."""
    case = make_case(db, assigned_mother, "150", "95")
    actions.escalate(db, case, staff_id("Trần Thị B"), NOW)
    assert db.execute("SELECT status FROM CARE_CASE WHERE case_id = ?", (case,)).fetchone()[0] == "Escalated to doctor"


def test_a_doctor_still_closes_it_once_escalated(db, assigned_mother, staff_id):
    case = make_case(db, assigned_mother, "150", "95")
    doctor = actions.escalate(db, case, staff_id("Trần Thị B"), NOW)
    assert "close" in actions.allowed(db, case, doctor)
    actions.close_case(db, case, doctor, NOW)
    assert db.execute("SELECT status FROM CARE_CASE WHERE case_id = ?", (case,)).fetchone()[0] == "Resolved"


def test_a_normal_case_is_still_closed_by_the_nurse(db, assigned_mother, staff_id):
    """The rule narrows nothing else: D-37 stands for every other case."""
    case = make_case(db, assigned_mother, "118", "76")
    actions.close_case(db, case, staff_id("Trần Thị B"), NOW)
    assert db.execute("SELECT status FROM CARE_CASE WHERE case_id = ?", (case,)).fetchone()[0] == "Resolved"
