"""T013 — end to end with specs/001-alr-core: mother reports -> nurse escalates -> doctor closes."""
import re


def test_mother_to_nurse_to_doctor(client, db, user_id, staff_id):
    u02 = user_id("tci-000126")   # responsible doctor: Nguyễn Văn A
    r = client.post(f"/m/{u02}/report", data={"metric": "Symptom", "measured_at": "2026-09-27T09:30",
                                               "symptoms": ["Palpitations"]})
    assert r.status_code == 303

    nurse, doctor = staff_id("Trần Thị B"), staff_id("Nguyễn Văn A")
    queue = client.get(f"/staff/{nurse}/cases", params={"status": "Not viewed", "sort": "Newest"}).text   # D-104: newest first on request
    first = re.search(rf'href="/staff/{nurse}/cases/([0-9a-f-]{{36}})"', queue).group(1)
    new_case = db.execute("SELECT case_id FROM CARE_CASE WHERE user_id = ? ORDER BY created_at DESC LIMIT 1", (u02,)).fetchone()[0]
    assert first == new_case

    assert client.post(f"/staff/{nurse}/cases/{new_case}/escalate").status_code == 303
    assert f"/staff/{doctor}/cases/{new_case}" in client.get(f"/staff/{doctor}/cases").text
    assert client.post(f"/staff/{doctor}/cases/{new_case}/close").status_code == 303
    assert db.execute("SELECT status FROM CARE_CASE WHERE case_id = ?", (new_case,)).fetchone()[0] == "Resolved"
