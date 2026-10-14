"""T015 — US-1 scenario 6; ALR BR-008 branch 3, BR-009: Normal and "No symptoms" -> no case."""
from .helpers import bp_form, counts


def test_normal_without_symptoms_stores_report_but_no_case(client, db, user_id):
    u09 = user_id("tci-000131")
    before = counts(db)
    r = client.post(f"/m/{u09}/report", data=bp_form(120, 80, ["No symptoms"]))
    assert r.status_code == 303
    assert r.headers["location"] == f"/m/{u09}/instructions?submitted=1"
    after = counts(db)
    assert {t: after[t] - before[t] for t in after} == {"HEALTH_METRIC_RECORD": 1, "METRIC_REPORT": 1, "REPORT_SYMPTOM": 1,
                                                        "CARE_CASE": 0, "CASE_STATUS_HISTORY": 0}
    assert "Report submitted" in client.get(r.headers["location"]).text
