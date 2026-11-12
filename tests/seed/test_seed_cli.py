"""T002 — CLI facts stated by data/seed/seed-report.md."""
from collections import Counter

from mb360 import db as dbmod


def test_staff_and_case_counts():
    conn = dbmod.build()
    roles = Counter(r[0] for r in conn.execute("SELECT role FROM STAFF"))
    assert roles == {"Nurse": 4, "Doctor": 3}
    statuses = Counter(r[0] for r in conn.execute("SELECT status FROM CARE_CASE"))
    assert statuses == {"Not viewed": 2, "Escalated to doctor": 1, "Resolved": 2}


def test_c4_has_a_viewed_step_and_an_assigned_doctor():
    """Seed scenario "ALR BR-016 / D-43": RPT-004 (BC-0926-011) -> C4."""
    conn = dbmod.build()
    rows = conn.execute(
        """SELECT h.status, h.role, c.assigned_doctor_id FROM CASE_STATUS_HISTORY h
           JOIN CARE_CASE c ON c.case_id = h.case_id
           JOIN METRIC_REPORT r ON r.report_id = c.metric_report_id
           WHERE r.report_code = 'BC-0926-011' ORDER BY h.changed_at, h.rowid"""
    ).fetchall()
    hist = {r["status"]: r for r in rows}
    assert list(hist) == ["Not viewed", "Viewed", "Escalated to doctor"]
    assert [row["role"] for row in hist.values()] == ["System", "Nurse", "Nurse"]
    assert hist["Escalated to doctor"]["assigned_doctor_id"]
