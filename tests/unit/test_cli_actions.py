"""T006 — CLI BR-002 / D-43: status only moves forward; skipped "Viewed" is recorded; history rows."""
import pytest

from mb360.cli import actions, queue
from tests.cli_helpers import NOW, RPT010, case_by_code, case_row, history, written


def test_mark_as_viewed(db, staff_id, boundary_case):
    case, nurse = boundary_case, staff_id("Trần Thị B")
    actions.mark_viewed(db, case, nurse, NOW)
    assert case_row(db, case)["status"] == "Viewed"
    h = history(db, case)["Viewed"]
    assert (h["changed_by"], h["role"], h["changed_at"]) == (nurse, "Nurse", "2026-09-27 10:00")


def test_escalate_from_not_viewed_records_viewed_first_and_assigns_the_doctor(db, staff_id, boundary_case):
    """Her responsible doctor (Phạm Quốc Dũng) is Away in the seed, so BR-011 step 2 sends the case to
    the doctor on duty — the nurse never chooses (D-97, proposed). Routing itself: test_cli_routing.py."""
    case, nurse = boundary_case, staff_id("Trần Thị B")
    actions.escalate(db, case, nurse, NOW)
    row = case_row(db, case)
    assert row["status"] == "Escalated to doctor"
    assert row["assigned_doctor_id"] == staff_id("Vũ Minh Hải")
    h = history(db, case)
    assert h["Viewed"]["changed_by"] == h["Escalated to doctor"]["changed_by"] == nurse
    assert h["Viewed"]["changed_at"] == h["Escalated to doctor"]["changed_at"]


def test_nurse_close_from_not_viewed_records_viewed_then_resolved(db, staff_id):
    case, nurse = case_by_code(db, RPT010), staff_id("Trần Thị B")
    actions.close_case(db, case, nurse, NOW)
    row = case_row(db, case)
    assert (row["status"], row["closed_at"], row["closed_by"]) == ("Resolved", "2026-09-27 10:00", nurse)
    assert set(history(db, case)) == {"Not viewed", "Viewed", "Resolved"}


@pytest.mark.parametrize("first", ["view", "escalate"])
def test_status_never_moves_backwards(db, staff_id, first, boundary_case):
    case, nurse = boundary_case, staff_id("Trần Thị B")
    {"view": actions.mark_viewed, "escalate": actions.escalate}[first](db, case, nurse, NOW)
    before = written(db)
    with pytest.raises(actions.ActionError) as e:
        actions.mark_viewed(db, case, nurse, NOW)
    assert e.value.status == 409
    assert written(db) == before


def test_escalation_without_an_active_responsible_doctor_still_goes_through(db, staff_id, user_id, boundary_case):
    """BR-011 step 4 (D-97, proposed) replaces the old refusal: a case must never fall into a gap.
    It becomes "Escalated to doctor" with no single assignee and is visible to every doctor (BR-010)."""
    db.execute("UPDATE PATIENT_ASSIGNMENT SET valid_to = '2026-09-01' WHERE user_id = ?", (user_id("tci-000126"),))
    db.execute("UPDATE STAFF SET on_duty = 0 WHERE role = 'Doctor'")      # nobody on duty either
    case, nurse = boundary_case, staff_id("Trần Thị B")
    assert actions.escalate(db, case, nurse, NOW) is None
    row = case_row(db, case)
    assert row["status"] == "Escalated to doctor" and row["assigned_doctor_id"] is None
    for doctor, in db.execute("SELECT staff_id FROM STAFF WHERE role = 'Doctor'"):
        assert case in [r["case_id"] for r in queue.list_cases(db, viewer=doctor)]
