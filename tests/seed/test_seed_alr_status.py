"""T002 — ALR US-2 facts stated by data/seed/seed-report.md (scenario "ALR US-2")."""
from mb360 import db as dbmod


def test_lan_reports_and_chatbot_case():
    conn = dbmod.build()
    lan = conn.execute("SELECT user_id FROM USER_ACCOUNT WHERE tci_account_ref = 'tci-000123'").fetchone()[0]
    reports = {r["report_code"]: r["status"] for r in conn.execute(
        """SELECT r.report_code, c.status FROM METRIC_REPORT r LEFT JOIN CARE_CASE c ON c.metric_report_id = r.report_id
           WHERE r.user_id = ?""", (lan,))}
    assert reports == {"BC-0925-008": None, "BC-0926-015": "Resolved", "BC-0927-022": "Not viewed"}
    chat = conn.execute("SELECT status FROM CARE_CASE WHERE user_id = ? AND case_source = 'Chatbot'", (lan,)).fetchall()
    assert [r[0] for r in chat] == ["Not viewed"]


def test_c1_history_and_response():
    conn = dbmod.build()
    case = conn.execute("""SELECT c.case_id FROM CARE_CASE c JOIN METRIC_REPORT r ON r.report_id = c.metric_report_id
                           WHERE r.report_code = 'BC-0926-015'""").fetchone()[0]
    hist = {r["status"]: r for r in conn.execute(
        "SELECT h.*, s.full_name FROM CASE_STATUS_HISTORY h LEFT JOIN STAFF s ON s.staff_id = h.changed_by WHERE case_id = ?", (case,))}
    assert set(hist) == {"Not viewed", "Viewed", "Resolved"}
    assert (hist["Viewed"]["full_name"], hist["Viewed"]["changed_at"]) == ("Trần Thị B", "2026-09-26 20:25")
    assert hist["Resolved"]["changed_at"] == "2026-09-26 20:40"
    resp = conn.execute("""SELECT s.full_name FROM STAFF_RESPONSE r JOIN STAFF s ON s.staff_id = r.responder_id
                           WHERE r.case_id = ?""", (case,)).fetchall()
    assert [r[0] for r in resp] == ["Trần Thị B"]
