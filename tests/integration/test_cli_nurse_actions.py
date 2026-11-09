"""T010 — US-1 #5 - #9 (nurse on S-064)."""
from tests.cli_helpers import RPT006, RPT010, a_template, case_by_code, case_row, written
from tests.integration.helpers import vi


def test_nurse_flow_on_rpt006(client, db, staff_id):
    nurse, case = staff_id("Trần Thị B"), case_by_code(db, RPT006)
    base = f"/staff/{nurse}/cases/{case}"

    r = client.post(f"{base}/view")
    assert r.status_code == 303 and r.headers["location"] == base
    assert case_row(db, case)["status"] == "Viewed"

    r = client.post(f"{base}/guidance", data={"template_id": a_template(db), "custom_text": ""})
    assert r.status_code == 303
    assert case_row(db, case)["status"] == "Viewed"
    assert db.execute("SELECT responder_role FROM STAFF_RESPONSE WHERE case_id = ?", (case,)).fetchone()[0] == "Nurse"

    assert client.post(f"{base}/escalate").status_code == 303
    row = case_row(db, case)
    assert row["status"] == "Escalated to doctor" and row["assigned_doctor_id"] == staff_id("Phạm Quốc Dũng")

    page = client.get(base).text
    assert vi("Close case") not in page
    before = written(db)
    assert client.post(f"{base}/close").status_code in (403, 409)
    assert written(db) == before


def test_nurse_closes_a_case_not_escalated(client, db, staff_id):
    nurse, case = staff_id("Trần Thị B"), case_by_code(db, RPT010)
    assert client.post(f"/staff/{nurse}/cases/{case}/close").status_code == 303
    assert case_row(db, case)["status"] == "Resolved"


def test_doctors_instructions_are_view_only_for_the_nurse(client, db, staff_id):
    page = client.get(f"/staff/{staff_id('Trần Thị B')}/cases/{case_by_code(db, RPT006)}").text
    assert vi("Doctor's instructions") in page
    assert ">" + vi("Edit") + "<" not in page and "data-instruction-form" not in page
