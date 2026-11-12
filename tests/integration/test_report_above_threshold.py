"""T013 — US-1 scenario 4; ALR FR-020, FR-021, FR-015, BR-006."""
from .helpers import bp_form, case_of, counts, latest_report


def test_above_threshold_report_is_stored_and_opens_a_metric_report_case(client, db, user_id):
    u09 = user_id("tci-000126")
    before = counts(db)
    r = client.post(f"/m/{u09}/report", data=bp_form(141, 88, ["No symptoms"]))
    assert r.status_code == 303
    rep = latest_report(db, u09)
    assert r.headers["location"] == f"/m/{u09}/reports/{rep['report_id']}/alert"

    after = counts(db)
    assert {t: after[t] - before[t] for t in after} == {"HEALTH_METRIC_RECORD": 1, "METRIC_REPORT": 1, "REPORT_SYMPTOM": 1,
                                                        "CARE_CASE": 1, "CASE_STATUS_HISTORY": 1}
    hmr = db.execute("SELECT * FROM HEALTH_METRIC_RECORD WHERE record_id = ?", (rep["health_metric_record_id"],)).fetchone()
    assert (hmr["metric"], hmr["metric_group"], hmr["value"], hmr["unit"], hmr["source"]) == \
        ("Blood pressure", "Group 2", "141/88", "mmHg", "Doctor-assigned")
    assert hmr["gestational_week"] == 31
    assert hmr["measured_at"] == "2026-09-27 09:00"
    assert hmr["created_at"] == rep["submitted_at"]

    w09 = db.execute("SELECT flag_id FROM WATCH_FLAG WHERE user_id = ? AND metric = 'Blood pressure' AND active = 1",
                     (u09,)).fetchone()[0]
    assert rep["watch_flag_id"] == w09
    assert rep["report_code"]
    assert db.execute("SELECT COUNT(*) FROM METRIC_REPORT WHERE report_code = ?", (rep["report_code"],)).fetchone()[0] == 1
    assert [s[0] for s in db.execute("SELECT symptom FROM REPORT_SYMPTOM WHERE report_id = ?", (rep["report_id"],))] == ["No symptoms"]

    case = case_of(db, rep["report_id"])
    assert (case["case_source"], case["status"], case["user_id"]) == ("Metric report", "Not viewed", u09)
    hist = db.execute("SELECT * FROM CASE_STATUS_HISTORY WHERE case_id = ?", (case["case_id"],)).fetchall()
    assert [(h["status"], h["role"], h["changed_by"]) for h in hist] == [("Not viewed", "System", None)]
