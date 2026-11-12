"""Shared helpers for the ALR US-2 tests (feature specs/003-alr-status)."""
from datetime import datetime

NOW = datetime(2026, 9, 27, 10, 0)
RPT001, RPT002, RPT010 = "BC-0925-008", "BC-0926-015", "BC-0927-022"


def report_id(db, code):
    return db.execute("SELECT report_id FROM METRIC_REPORT WHERE report_code = ?", (code,)).fetchone()[0]


def case_of_code(db, code):
    return db.execute("""SELECT c.case_id FROM CARE_CASE c JOIN METRIC_REPORT r ON r.report_id = c.metric_report_id
                         WHERE r.report_code = ?""", (code,)).fetchone()[0]


def chatbot_case(db, user):
    return db.execute("SELECT case_id FROM CARE_CASE WHERE user_id = ? AND case_source = 'Chatbot'", (user,)).fetchone()[0]


def notifications(db, user):
    return db.execute("SELECT * FROM NOTIFICATION WHERE user_id = ? ORDER BY created_at, rowid", (user,)).fetchall()
