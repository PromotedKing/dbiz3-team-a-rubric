"""T014 — US-1 scenario 5; ALR BR-007 for every symptom of the D-73 list; symptom-mode report."""
import pytest

from .helpers import bp_form, case_of, latest_report

D73 = ["Vaginal bleeding", "Severe abdominal pain", "Waters breaking or fluid leakage",
       "Severe headache, dizziness or blurred vision", "Absence of fetal movement", "Palpitations", "Other"]


def test_normal_value_with_symptom_opens_a_symptom_case_and_shows_status(client, db, user_id):
    u09 = user_id("tci-000131")
    r = client.post(f"/m/{u09}/report", data=bp_form(120, 80, ["Palpitations"]))
    assert r.status_code == 303
    rep = latest_report(db, u09)
    assert r.headers["location"] == f"/m/{u09}/reports/{rep['report_id']}?submitted=1"
    assert case_of(db, rep["report_id"])["case_source"] == "Symptom"
    page = client.get(r.headers["location"]).text
    assert "Report submitted" in page and "Not viewed" in page


@pytest.mark.parametrize("symptom", D73)
def test_every_symptom_creates_a_case(client, db, user_id, symptom):
    u09 = user_id("tci-000131")
    other = "Back ache" if symptom == "Other" else ""
    client.post(f"/m/{u09}/report", data=bp_form(120, 80, [symptom], other))
    case = case_of(db, latest_report(db, u09)["report_id"])
    assert case is not None and case["status"] == "Not viewed"


def test_symptom_mode_report_has_no_record_and_no_instruction(client, db, user_id):
    u06 = user_id("tci-000128")  # no Doctor's instruction
    r = client.post(f"/m/{u06}/report", data={"metric": "Symptom", "measured_at": "2026-09-27T09:00",
                                               "symptoms": ["Absence of fetal movement"]})
    assert r.status_code == 303
    rep = latest_report(db, u06)
    assert rep["metric"] == "Symptom"
    assert rep["health_metric_record_id"] is None and rep["watch_flag_id"] is None
    assert case_of(db, rep["report_id"])["case_source"] == "Symptom"
