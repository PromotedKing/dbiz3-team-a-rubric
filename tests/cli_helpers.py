"""Shared helpers for the CLI tests (feature specs/002-cli-core)."""
from datetime import datetime

from mb360.alr import cases, reports

NOW = datetime(2026, 9, 27, 10, 0)


def open_boundary_case(db, user):
    """A new above-threshold report with its initial clinical history."""
    submitted = NOW.replace(hour=7, minute=2)
    report = reports.store_report(db, user, {
        "metric": "Blood pressure",
        "systolic": "140",
        "diastolic": "90",
        "measured_at": "2026-09-27T07:00",
        "symptoms": ["Other"],
        "other_symptom_text": "x" * 100,
    }, submitted)
    case = cases.open_case(db, user, report["report_id"], "Metric report", submitted)
    db.commit()
    return case


def case_by_code(db, report_code):
    return db.execute("""SELECT c.case_id FROM CARE_CASE c JOIN METRIC_REPORT r ON r.report_id = c.metric_report_id
                         WHERE r.report_code = ?""", (report_code,)).fetchone()[0]


def case_row(db, case_id):
    return db.execute("SELECT * FROM CARE_CASE WHERE case_id = ?", (case_id,)).fetchone()


def history(db, case_id):
    return {r["status"]: r for r in db.execute("SELECT * FROM CASE_STATUS_HISTORY WHERE case_id = ?", (case_id,))}


def written(db):
    return {t: db.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
            for t in ("CASE_STATUS_HISTORY", "STAFF_RESPONSE")} | {
        "case_states": tuple(db.execute("SELECT case_id, status, assigned_doctor_id, closed_at FROM CARE_CASE ORDER BY case_id"))}


def a_template(db):
    return db.execute("SELECT template_id FROM GUIDANCE_TEMPLATE WHERE is_default = 0 ORDER BY title LIMIT 1").fetchone()[0]


# Seed cases used by the tests (data/seed/seed-report.md)
RPT010 = "BC-0927-022"   # U01 symptom report, Not viewed, not escalated
RPT004 = "BC-0926-011"   # U04, C4, Escalated to doctor, assigned Nguyễn Văn A
RPT002 = "BC-0926-015"   # U01 (Lan), Resolved; U01 has Self-entered metrics
