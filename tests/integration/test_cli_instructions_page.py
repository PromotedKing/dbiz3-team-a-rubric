"""T006 — CLI US-3 #1, #2; S-064 #6 - #11; effect on the mother's S-027 / S-025A / S-028."""
from tests.cli_helpers import RPT006, case_by_code
from tests.integration.helpers import counts
from tests.integration.helpers import vi


def _template(db, title):
    return db.execute("SELECT template_id, content FROM GUIDANCE_TEMPLATE WHERE title = ?", (title,)).fetchone()


def test_doctor_sees_edit_and_the_form(client, db, staff_id):
    page = client.get(f"/staff/{staff_id('Phạm Quốc Dũng')}/cases/{case_by_code(db, RPT006)}").text
    assert ">" + vi("Edit") + "<" in page and "data-instruction-form" in page and vi("Add / edit instruction") in page
    for metric in ("Blood pressure", "Blood glucose", "Urine protein"):
        assert f'value="{metric}"' in page
    assert "Blood glucose guidance" in page and vi("Save instruction") in page


def test_doctor_adds_an_instruction_and_the_mother_sees_it(client, db, user_id, staff_id):
    doctor, u09 = staff_id("Phạm Quốc Dũng"), user_id("tci-000131")
    case = case_by_code(db, RPT006)
    tpl = _template(db, "Blood glucose guidance")
    r = client.post(f"/staff/{doctor}/cases/{case}/instructions",
                    data={"metric": "Blood glucose", "note": "Measure fasting every morning", "template_id": tpl["template_id"], "custom_text": ""})
    assert r.status_code == 303 and r.headers["location"] == f"/staff/{doctor}/cases/{case}"
    page = client.get(r.headers["location"]).text
    assert vi("Blood glucose") in page and vi("Assigned {date} · Dr. {name}", date="27/09/2026", name="Phạm Quốc Dũng") in page

    assert "Measure fasting every morning" in client.get(f"/m/{u09}/instructions").text
    assert 'value="Blood glucose"' in client.get(f"/m/{u09}/report", params={"metric": "Blood glucose"}).text
    sent = client.post(f"/m/{u09}/report", data={"metric": "Blood glucose", "value": "6.0", "glucose_context": "fasting",
                                                  "measured_at": "2026-09-27T08:00", "symptoms": ["No symptoms"]})
    assert tpl["content"] in client.get(sent.headers["location"]).text      # S-028 shows the chosen guidance


def test_instruction_without_guidance_uses_the_default_template(client, db, user_id, staff_id):
    doctor, u09 = staff_id("Phạm Quốc Dũng"), user_id("tci-000131")
    client.post(f"/staff/{doctor}/cases/{case_by_code(db, RPT006)}/instructions", data={"metric": "Urine protein", "note": "", "template_id": "", "custom_text": ""})
    sent = client.post(f"/m/{u09}/report", data={"metric": "Urine protein", "level": "2+", "measured_at": "2026-09-27T08:00",
                                                  "symptoms": ["No symptoms"]})
    default = db.execute("SELECT content FROM GUIDANCE_TEMPLATE WHERE is_default = 1").fetchone()[0]
    assert default in client.get(sent.headers["location"]).text


def test_nurse_cannot_edit(client, db, staff_id):
    nurse, case = staff_id("Trần Thị B"), case_by_code(db, RPT006)
    page = client.get(f"/staff/{nurse}/cases/{case}").text
    assert ">" + vi("Edit") + "<" not in page and "data-instruction-form" not in page
    before = db.execute("SELECT COUNT(*) FROM WATCH_FLAG").fetchone()[0]
    r = client.post(f"/staff/{nurse}/cases/{case}/instructions", data={"metric": "Blood glucose", "note": "x"})
    assert r.status_code == 403
    assert db.execute("SELECT COUNT(*) FROM WATCH_FLAG").fetchone()[0] == before
