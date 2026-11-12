"""T011 — US-2 #2 - #5, BR-001 (doctor on S-064)."""
from tests.cli_helpers import RPT004, a_template, case_by_code, case_row, written
from tests.integration.helpers import vi


def test_doctor_page_has_no_nurse_buttons(client, db, staff_id):
    page = client.get(f"/staff/{staff_id('Nguyễn Văn A')}/cases/{case_by_code(db, RPT004)}").text
    assert vi("Dr. {name}", name="Nguyễn Văn A") in page
    assert "Mark as viewed" not in page and "Escalate to doctor</button>" not in page


def test_doctor_sends_guidance_then_closes_the_escalated_case(client, db, staff_id):
    doctor, case = staff_id("Nguyễn Văn A"), case_by_code(db, RPT004)
    base = f"/staff/{doctor}/cases/{case}"
    assert client.post(f"{base}/guidance", data={"template_id": a_template(db), "custom_text": "Come to the clinic today."}).status_code == 303
    assert case_row(db, case)["status"] == "Escalated to doctor"
    assert client.post(f"{base}/close").status_code == 303
    row = case_row(db, case)
    assert (row["status"], row["closed_by"]) == ("Resolved", doctor)


def test_doctor_cannot_act_on_a_case_not_escalated(client, db, staff_id, boundary_case):
    doctor, case = staff_id("Nguyễn Văn A"), boundary_case
    base = f"/staff/{doctor}/cases/{case}"
    page = client.get(base).text
    assert "Send guidance</button>" not in page and "Close case" not in page
    before = written(db)
    assert client.post(f"{base}/guidance", data={"custom_text": "x"}).status_code == 403
    assert client.post(f"{base}/close").status_code == 403
    assert written(db) == before
