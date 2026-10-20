"""S-061 "Cases to handle": CLI FR-002, FR-020, BR-007; doctor badge (ALR FR-009, DM-32 — derived, not stored)."""
import sqlite3
from datetime import date

from ..alr import thresholds
from ..alr.reports import gestational_week
from ..clock import now

SYMPTOM_LABELS = {
    "Waters breaking or fluid leakage": "Waters breaking / fluid leakage",
    "Severe headache, dizziness or blurred vision": "Severe headache / dizziness / blurred vision",
}


def symptom_text(conn: sqlite3.Connection, report_id: str) -> str:
    rows = conn.execute("SELECT symptom FROM REPORT_SYMPTOM WHERE report_id = ? ORDER BY symptom", (report_id,))
    return ", ".join(SYMPTOM_LABELS.get(r[0], r[0]) for r in rows)


def list_cases(conn: sqlite3.Connection, status: str | None = None) -> list[dict]:
    rows = conn.execute(
        """SELECT c.case_id, c.status, c.case_source, c.created_at, u.full_name, p.edd,
                  r.report_id, r.metric, r.submitted_at, h.value, h.unit, h.glucose_context, m.text AS question
           FROM CARE_CASE c
           JOIN USER_ACCOUNT u ON u.user_id = c.user_id
           LEFT JOIN PREGNANCY_PROFILE p ON p.user_id = c.user_id
           LEFT JOIN METRIC_REPORT r ON r.report_id = c.metric_report_id
           LEFT JOIN HEALTH_METRIC_RECORD h ON h.record_id = r.health_metric_record_id
           LEFT JOIN CHAT_MESSAGE m ON m.message_id = c.chat_message_id
           WHERE (? IS NULL OR c.status = ?)""",
        (status, status),
    ).fetchall()
    today = now().date()
    result = []
    for row in rows:
        if row["case_source"] == "Chatbot":
            content, value, label = row["question"], None, thresholds.NOT_ASSESSED
        elif row["value"] is None:     # symptom report
            content, value, label = symptom_text(conn, row["report_id"]), None, thresholds.NOT_ASSESSED
        else:
            content = row["metric"]
            value = f"{row['value']} {row['unit']}" if row["unit"] else row["value"]
            label = thresholds.evaluate(conn, row["metric"], row["value"], row["glucose_context"])
        result.append({
            "case_id": row["case_id"], "mother": row["full_name"], "status": row["status"],
            "week": gestational_week(date.fromisoformat(row["edd"]), today) if row["edd"] else None,
            "case_source": row["case_source"], "content": content, "value": value, "label": label,
            "submitted_at": row["submitted_at"] or row["created_at"],
        })
    result.sort(key=lambda r: r["submitted_at"], reverse=True)
    return result


def doctor_badge(conn: sqlite3.Connection, staff_id: str) -> int:
    return conn.execute("SELECT COUNT(*) FROM CARE_CASE WHERE status = 'Escalated to doctor' AND assigned_doctor_id = ?",
                        (staff_id,)).fetchone()[0]
