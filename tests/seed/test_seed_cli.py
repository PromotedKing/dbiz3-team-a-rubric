"""T002 — CLI facts stated by data/seed/seed-report.md."""
from collections import Counter

from mb360 import db as dbmod


def test_staff_and_case_counts():
    conn = dbmod.build()
    roles = Counter(r[0] for r in conn.execute("SELECT role FROM STAFF"))
    assert roles == {"Nurse": 4, "Doctor": 3}
    statuses = Counter(r[0] for r in conn.execute("SELECT status FROM CARE_CASE"))
    assert statuses == {"Not viewed": 4, "Viewed": 1, "Escalated to doctor": 1, "Resolved": 4}


def test_c7_viewed_recorded_with_the_escalation_then_closed_by_a_doctor():
    """Seed scenario "ALR BR-016 / D-43": RPT-008 (BC-0926-012) -> C7."""
    conn = dbmod.build()
    rows = conn.execute(
        """SELECT h.status, h.changed_at, h.changed_by, h.role FROM CASE_STATUS_HISTORY h
           JOIN CARE_CASE c ON c.case_id = h.case_id
           JOIN METRIC_REPORT r ON r.report_id = c.metric_report_id
           WHERE r.report_code = 'BC-0926-012' ORDER BY h.changed_at, h.rowid"""
    ).fetchall()
    hist = {r["status"]: r for r in rows}
    assert set(hist) == {"Not viewed", "Viewed", "Escalated to doctor", "Resolved"}   # rows of one minute keep CSV order
    assert hist["Not viewed"]["role"] == "System"
    assert hist["Viewed"]["changed_at"] == hist["Escalated to doctor"]["changed_at"]
    assert hist["Viewed"]["changed_by"] == hist["Escalated to doctor"]["changed_by"]
    assert hist["Viewed"]["role"] == "Nurse" and hist["Resolved"]["role"] == "Doctor"
