"""BR-010 and BR-011 (D-96, D-97, proposed) — who sees which cases, and who receives an escalated one.

Seed roster: Nguyễn Văn A Available (2 mothers), Phạm Quốc Dũng **Away** (1 mother), Vũ Minh Hải
Available and **on duty** (no mother of his own).
"""
from datetime import date

import pytest

from mb360.cli import actions, queue

from tests.cli_helpers import NOW

TODAY = date(2026, 9, 27)


@pytest.fixture
def roster(db, staff_id):
    return {"present": staff_id("Nguyễn Văn A"), "away": staff_id("Phạm Quốc Dũng"),
            "on_duty": staff_id("Vũ Minh Hải"), "nurse": staff_id("Trần Thị B")}


def mothers_of(db, doctor):
    return {r[0] for r in db.execute(
        """SELECT user_id FROM PATIENT_ASSIGNMENT WHERE doctor_id = ? AND valid_from <= ?
           AND (valid_to IS NULL OR valid_to >= ?)""", (doctor, TODAY.isoformat(), TODAY.isoformat()))}


# ---------------------------------------------------------------- BR-010 visibility

def test_a_nurse_sees_every_mother(db, roster):
    assert actions.visible_users(db, roster["nurse"], TODAY) is None     # None = no filter


def test_a_doctor_sees_his_own_mothers(db, roster):
    assert actions.visible_users(db, roster["present"], TODAY) == mothers_of(db, roster["present"])


def test_an_on_duty_doctor_also_sees_the_mothers_of_an_away_doctor(db, roster):
    seen = actions.visible_users(db, roster["on_duty"], TODAY)
    assert mothers_of(db, roster["on_duty"]) == set()        # none of his own
    assert seen == mothers_of(db, roster["away"]) and seen


def test_he_stops_seeing_them_when_that_doctor_is_back(db, roster):
    db.execute("UPDATE STAFF SET availability = 'Available' WHERE staff_id = ?", (roster["away"],))
    assert actions.visible_users(db, roster["on_duty"], TODAY) == set()


def test_a_doctor_who_is_not_on_duty_never_covers(db, roster):
    db.execute("UPDATE STAFF SET on_duty = 0 WHERE staff_id = ?", (roster["on_duty"],))
    assert actions.visible_users(db, roster["on_duty"], TODAY) == set()


def test_the_away_doctor_still_sees_his_own_mothers(db, roster):
    """Away limits what he receives, not what he may read."""
    assert actions.visible_users(db, roster["away"], TODAY) == mothers_of(db, roster["away"])


def test_the_case_list_is_filtered_for_a_doctor_but_not_for_a_nurse(db, roster):
    everything = len(queue.list_cases(db))
    assert len(queue.list_cases(db, viewer=roster["nurse"])) == everything
    for doctor in ("present", "away", "on_duty"):
        rows = queue.list_cases(db, viewer=roster[doctor])
        assert len(rows) < everything
        allowed = actions.visible_users(db, roster[doctor], TODAY)
        for r in rows:
            case = db.execute("SELECT user_id, assigned_doctor_id FROM CARE_CASE WHERE case_id = ?", (r["case_id"],)).fetchone()
            assert case["user_id"] in allowed or case["assigned_doctor_id"] is None


# ---------------------------------------------------------------- BR-011 routing

def test_step_1_the_responsible_doctor_when_he_is_available(db, roster):
    mother = next(iter(mothers_of(db, roster["present"])))
    r = actions.route_to(db, mother, TODAY)
    assert (r["doctor"], r["outcome"], r["availability"]) == (roster["present"], "responsible", "Available")


def test_step_2_the_on_duty_doctor_when_the_responsible_one_is_away(db, roster):
    mother = next(iter(mothers_of(db, roster["away"])))
    r = actions.route_to(db, mother, TODAY)
    assert (r["doctor"], r["outcome"], r["availability"]) == (roster["on_duty"], "on_duty", "Away")
    assert r["responsible"] == roster["away"]            # FR-027 still names who is responsible


def test_step_4_no_active_responsible_doctor(db, roster, user_id):
    mother = user_id("tci-000133")                        # no Patient Assignment in the seed
    r = actions.route_to(db, mother, TODAY)
    assert (r["doctor"], r["outcome"], r["responsible"]) == (None, "none", None)


def test_step_4_away_and_nobody_on_duty(db, roster):
    db.execute("UPDATE STAFF SET on_duty = 0 WHERE role = 'Doctor'")
    mother = next(iter(mothers_of(db, roster["away"])))
    assert actions.route_to(db, mother, TODAY)["outcome"] == "none"


def test_an_on_duty_doctor_who_is_himself_away_does_not_cover(db, roster):
    db.execute("UPDATE STAFF SET availability = 'Away' WHERE staff_id = ?", (roster["on_duty"],))
    mother = next(iter(mothers_of(db, roster["away"])))
    assert actions.route_to(db, mother, TODAY)["outcome"] == "none"


def test_the_escalated_case_goes_to_the_routed_doctor(db, roster, boundary_case):
    """`boundary_case` belongs to the Away doctor's mother, so it lands with the doctor on duty."""
    assert actions.escalate(db, boundary_case, roster["nurse"], NOW) == roster["on_duty"]
    assert db.execute("SELECT assigned_doctor_id FROM CARE_CASE WHERE case_id = ?",
                      (boundary_case,)).fetchone()[0] == roster["on_duty"]


def test_the_case_stays_with_him_after_the_responsible_doctor_returns(db, roster, boundary_case):
    """US-4 scenario 5: it never moves back on its own."""
    actions.escalate(db, boundary_case, roster["nurse"], NOW)
    db.execute("UPDATE STAFF SET availability = 'Available' WHERE staff_id = ?", (roster["away"],))
    assert db.execute("SELECT assigned_doctor_id FROM CARE_CASE WHERE case_id = ?",
                      (boundary_case,)).fetchone()[0] == roster["on_duty"]
    # and the responsible doctor can still read it: she is his mother (BR-010)
    assert boundary_case in [r["case_id"] for r in queue.list_cases(db, viewer=roster["away"])]


def test_a_case_with_no_assignee_is_visible_to_every_doctor(db, roster, boundary_case):
    """BR-011 step 4 + BR-010 exception: the fail-safe must not hide the case from everyone."""
    db.execute("UPDATE PATIENT_ASSIGNMENT SET valid_to = '2026-09-01'")
    db.execute("UPDATE STAFF SET on_duty = 0 WHERE role = 'Doctor'")
    actions.escalate(db, boundary_case, roster["nurse"], NOW)
    for doctor, in db.execute("SELECT staff_id FROM STAFF WHERE role = 'Doctor'"):
        assert boundary_case in [r["case_id"] for r in queue.list_cases(db, viewer=doctor)]
