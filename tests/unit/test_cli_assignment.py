"""T003 — responsible doctor = active PATIENT_ASSIGNMENT (D-68; research R3; spec-CLI §10 Q15)."""
from datetime import date

from mb360.cli import actions

TODAY = date(2026, 9, 27)


def test_u09_responsible_doctor(db, user_id, staff_id):
    assert actions.responsible_doctor(db, user_id("tci-000131"), TODAY) == staff_id("Phạm Quốc Dũng")


def test_u05_uses_the_current_assignment_not_the_ended_one(db, user_id, staff_id):
    assert actions.responsible_doctor(db, user_id("tci-000127"), TODAY) == staff_id("Phạm Quốc Dũng")


def test_assignment_is_active_on_its_valid_to_day(db, user_id, staff_id):
    u06 = user_id("tci-000128")   # valid_to = 2026-09-27
    assert actions.responsible_doctor(db, u06, TODAY) == staff_id("Phạm Quốc Dũng")
    assert actions.responsible_doctor(db, u06, date(2026, 9, 28)) is None


def test_mother_without_assignment(db, user_id):
    assert actions.responsible_doctor(db, user_id("tci-000129"), TODAY) is None
