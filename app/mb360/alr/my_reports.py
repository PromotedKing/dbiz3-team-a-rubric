"""S-029 "My reports": ALR FR-002, FR-003, BR-005, BR-009 (research R2, R6)."""
import sqlite3

from . import thresholds
from .notifications import SYMPTOM_LABELS

TYPES = ("Blood pressure", "Blood glucose", "Urine protein", "Symptom", "Chatbot")


def list_rows(conn: sqlite3.Connection, user_id: str, status: str | None = None, type_: str | None = None) -> list[dict]:
    rows = []
    for r in conn.execute(
        """SELECT r.report_id, r.metric, r.submitted_at, h.value, h.unit, h.glucose_context, c.case_id, c.status
           FROM METRIC_REPORT r
           LEFT JOIN HEALTH_METRIC_RECORD h ON h.record_id = r.health_metric_record_id
           LEFT JOIN CARE_CASE c ON c.metric_report_id = r.report_id
           WHERE r.user_id = ?""", (user_id,)):
        syms = [x[0] for x in conn.execute("SELECT symptom FROM REPORT_SYMPTOM WHERE report_id = ? ORDER BY symptom", (r["report_id"],))]
        if r["value"] is None:
            label, value = thresholds.NOT_ASSESSED, None
        else:
            label = thresholds.evaluate(conn, r["metric"], r["value"], r["glucose_context"])
            value = f"{r['value']} {r['unit']}" if r["unit"] else r["value"]
        rows.append({"kind": "report", "report_id": r["report_id"], "case_id": r["case_id"], "title": r["metric"],
                     "label": label, "value": value, "symptoms": ", ".join(SYMPTOM_LABELS.get(s, s) for s in syms),
                     "question": None, "sent_at": r["submitted_at"], "status": r["status"]})
    for c in conn.execute(
        """SELECT c.case_id, c.status, c.created_at, m.text FROM CARE_CASE c JOIN CHAT_MESSAGE m ON m.message_id = c.chat_message_id
           WHERE c.user_id = ? AND c.case_source = 'Chatbot'""", (user_id,)):
        rows.append({"kind": "chatbot", "report_id": None, "case_id": c["case_id"], "title": "Chatbot", "label": None,
                     "value": None, "symptoms": "", "question": c["text"], "sent_at": c["created_at"], "status": c["status"]})
    if status:
        rows = [r for r in rows if r["status"] == status]
    if type_:
        rows = [r for r in rows if r["title"] == type_]
    rows.sort(key=lambda r: r["sent_at"], reverse=True)   # newest first (S-029 §4; §10 Q17)
    return rows
