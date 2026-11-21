"""S-061D #14: the doctor's list shows each mother's responsible doctor, Available / Away, and "Covering" (BR-010)."""
from datetime import datetime

from mb360 import clock

from tests.cli_helpers import open_boundary_case
from tests.integration.helpers import vi


def test_doctor_list_has_the_responsible_doctor_column_and_no_waiting_column(client, staff_id):
    page = client.get(f"/staff/{staff_id('Nguyễn Văn A')}/cases", params={"status": "All"}).text
    assert f"<th>{vi('Responsible doctor')}</th>" in page and f"<th>{vi('Waiting')}</th>" not in page
    assert vi("Dr. {name}", name="Nguyễn Văn A") + " · " + vi("Available") in page


def test_the_nurse_list_has_no_responsible_doctor_column(client, staff_id):
    page = client.get(f"/staff/{staff_id('Trần Thị B')}/cases", params={"status": "All"}).text
    assert "data-responsible" not in page and "data-covering" not in page


def test_a_mother_without_a_responsible_doctor_says_so(client, db, staff_id):
    """Đỗ Thị Hương: the assignment ended on 27/09/2026 — her new case is visible to every doctor (BR-011 step 4)."""
    huong = db.execute("SELECT user_id FROM USER_ACCOUNT WHERE full_name = 'Đỗ Thị Hương'").fetchone()[0]
    case = open_boundary_case(db, huong)
    clock.set(datetime(2026, 9, 28, 10, 0))          # the assignment is valid up to and including 27/09 (CLI §10 Q15)
    db.execute("UPDATE CARE_CASE SET status = 'Escalated to doctor', assigned_doctor_id = NULL WHERE case_id = ?", (case,))
    page = client.get(f"/staff/{staff_id('Vũ Minh Hải')}/cases", params={"status": "All"}).text
    assert f"/cases/{case}" in page and vi("No responsible doctor") in page


def test_the_covering_doctor_sees_the_covering_tag_and_the_away_doctor_of_the_mother(client, db, staff_id, boundary_case):
    """The mother's responsible doctor is Away in the seed; the doctor on duty sees her case with "Covering"."""
    cover = db.execute("SELECT staff_id, full_name FROM STAFF WHERE role = 'Doctor' AND on_duty = 1 AND availability = 'Available'").fetchone()
    db.execute("UPDATE CARE_CASE SET status = 'Escalated to doctor', assigned_doctor_id = ? WHERE case_id = ?", (cover["staff_id"], boundary_case))
    page = client.get(f"/staff/{cover['staff_id']}/cases", params={"status": "All"}).text
    assert f'/cases/{boundary_case}' in page and "data-covering" in page
    assert vi("Away") in page and vi("Covering") in page
