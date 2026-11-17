"""BR-010, FR-026, FR-027 on the clinical web (D-96, D-97, proposed)."""
import re
from datetime import date

from mb360 import ui
from mb360.cli import actions

TODAY = date(2026, 9, 27)


def cases_on(client, staff, status="All"):
    page = client.get(f"/staff/{staff}/cases?status={status}").text
    return set(re.findall(r"/cases/([0-9a-f-]{36})", page))


def test_a_doctor_no_longer_sees_every_mothers_case(client, db, staff_id):
    """Before BR-010 every doctor saw all 5 seed cases."""
    nurse_sees = cases_on(client, staff_id("Trần Thị B"))
    assert len(nurse_sees) == db.execute("SELECT COUNT(*) FROM CARE_CASE").fetchone()[0]
    for doctor in ("Nguyễn Văn A", "Phạm Quốc Dũng", "Vũ Minh Hải"):
        seen = cases_on(client, staff_id(doctor))
        assert seen < nurse_sees, f"{doctor} still sees everything"


def test_opening_a_case_of_a_mother_he_does_not_look_after_is_refused(client, db, staff_id):
    doctor = staff_id("Nguyễn Văn A")
    mine = actions.visible_users(db, doctor, TODAY)
    other = db.execute("SELECT case_id FROM CARE_CASE WHERE user_id NOT IN (%s)"
                       % ",".join("?" * len(mine)), tuple(mine)).fetchone()[0]
    assert client.get(f"/staff/{doctor}/cases/{other}").status_code == 403


def test_a_nurse_opens_every_case(client, db, staff_id):
    nurse = staff_id("Trần Thị B")
    for case_id, in db.execute("SELECT case_id FROM CARE_CASE"):
        assert client.get(f"/staff/{nurse}/cases/{case_id}").status_code == 200


def test_the_nurse_is_told_the_case_goes_to_the_doctor_on_duty(client, db, staff_id, boundary_case):
    """FR-026 / FR-027: her mother's responsible doctor is Away in the seed."""
    page = client.get(f"/staff/{staff_id('Trần Thị B')}/cases/{boundary_case}").text
    assert ui.t("Will be sent to the doctor on duty · Responsible doctor: Dr. {name} (Away)",
                name="Phạm Quốc Dũng") in page


def test_the_nurse_is_warned_when_no_doctor_can_take_it(client, db, staff_id, boundary_case):
    db.execute("UPDATE PATIENT_ASSIGNMENT SET valid_to = '2026-09-01'")
    db.execute("UPDATE STAFF SET on_duty = 0 WHERE role = 'Doctor'")
    db.commit()
    page = client.get(f"/staff/{staff_id('Trần Thị B')}/cases/{boundary_case}").text
    assert ui.t("No doctor available: the case is visible to all doctors") in page


def test_every_label_of_the_routing_line_is_in_the_reference_table(client, db, staff_id):
    ui.MISSING.clear()
    for sid, in db.execute("SELECT staff_id FROM STAFF"):
        for case_id, in db.execute("SELECT case_id FROM CARE_CASE"):
            client.get(f"/staff/{sid}/cases/{case_id}")
    assert ui.MISSING == set()
