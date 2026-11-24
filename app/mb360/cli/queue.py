"""S-061 / S-061D "Cases to handle": CLI FR-002, FR-020, FR-027, BR-007; doctor badge (ALR FR-009, DM-32 — derived, not stored).

One list for both roles (D-103, D-107); the role views differ only in the order and the columns:
the nurse's "Priority" order and "Waiting" column (S-061 SR-006, D-104), the doctor's "Responsible
doctor" column with the "Covering" tag (S-061D #14, BR-010). Nothing here is stored.
"""
import sqlite3
from ..bot.chat import danger_of
from datetime import date, datetime

from ..alr import thresholds
from ..alr.reports import gestational_week
from ..clock import now
from . import actions

SYMPTOM_LABELS = {
    "Waters breaking or fluid leakage": "Waters breaking / fluid leakage",
    "Severe headache, dizziness or blurred vision": "Severe headache / dizziness / blurred vision",
}


def symptom_text(conn: sqlite3.Connection, report_id: str) -> str:
    rows = conn.execute("SELECT symptom FROM REPORT_SYMPTOM WHERE report_id = ? ORDER BY symptom", (report_id,))
    return ", ".join(SYMPTOM_LABELS.get(r[0], r[0]) for r in rows)


PRIORITY, NEWEST = "Priority", "Newest"
DB_TIME = "%Y-%m-%d %H:%M"


def waiting_minutes(submitted_at: str, status: str, at: datetime) -> int | None:
    """S-061 #13A: time from submission to now for a case not "Resolved"; None ("—") once it is resolved. No limit, no colour (D-85)."""
    if status == "Resolved":
        return None
    return max(0, int((at - datetime.strptime(submitted_at[:16], DB_TIME)).total_seconds() // 60))


def is_priority(row: dict) -> bool:
    """S-061 SR-006 (D-104): "Above threshold" (THRESHOLD_RULE) and still "Not viewed"."""
    return row["label"] == thresholds.ABOVE and row["status"] == "Not viewed"


def sort_cases(rows: list[dict], order: str) -> list[dict]:
    """"Newest": by submission time, newest first. "Priority" (D-104): above-threshold cases not yet viewed
    first, then every other case by waiting time, longest first; resolved cases (no waiting time) last."""
    rows = sorted(rows, key=lambda r: r["submitted_at"], reverse=True)
    if order == PRIORITY:
        rows.sort(key=lambda r: (not is_priority(r), r["waiting"] is None, -(r["waiting"] or 0)))
    return rows


def responsible(conn: sqlite3.Connection, user_id: str, today: date) -> dict | None:
    """FR-027: the mother's responsible doctor (active Patient Assignment, D-68) and his availability."""
    doctor_id = actions.responsible_doctor(conn, user_id, today)
    if doctor_id is None:
        return None
    row = conn.execute("SELECT staff_id, full_name, availability FROM STAFF WHERE staff_id = ?", (doctor_id,)).fetchone()
    return {"staff_id": row["staff_id"], "name": row["full_name"], "availability": row["availability"]}


def list_cases(conn: sqlite3.Connection, status: str | None = None, viewer: str | None = None,
               order: str = NEWEST) -> list[dict]:
    """`viewer` applies BR-010 (D-96, proposed); left out, nothing is filtered. `order`: "Newest" or "Priority" (D-104)."""
    rows = conn.execute(
        """SELECT c.case_id, c.status, c.case_source, c.created_at, c.user_id, c.assigned_doctor_id, u.full_name, p.edd,
                  r.report_id, r.metric, r.submitted_at, h.value, h.unit, h.glucose_context, m.text AS question,
                  m.text, m.is_risk, m.parsed_intent
           FROM CARE_CASE c
           JOIN USER_ACCOUNT u ON u.user_id = c.user_id
           LEFT JOIN PREGNANCY_PROFILE p ON p.user_id = c.user_id
           LEFT JOIN METRIC_REPORT r ON r.report_id = c.metric_report_id
           LEFT JOIN HEALTH_METRIC_RECORD h ON h.record_id = r.health_metric_record_id
           LEFT JOIN CHAT_MESSAGE m ON m.message_id = c.chat_message_id
           WHERE (? IS NULL OR c.status = ?)""",
        (status, status),
    ).fetchall()
    from .dashboard import ALARM_SYMPTOMS     # local import: dashboard imports this module
    at = now()
    today = at.date()
    mine = actions.visible_users(conn, viewer, today) if viewer else None
    me = conn.execute("SELECT role, on_duty FROM STAFF WHERE staff_id = ?", (viewer,)).fetchone() if viewer else None
    covers = me is not None and me["role"] == "Doctor" and me["on_duty"] == 1
    result = []
    for row in rows:
        if mine is not None and row["user_id"] not in mine and not (      # BR-010
                row["assigned_doctor_id"] is None and row["status"] == "Escalated to doctor"):   # BR-011 step 4
            continue
        if row["case_source"] == "Chatbot":
            content, value, label = row["question"], None, thresholds.NOT_ASSESSED
        elif row["value"] is None:     # symptom report
            content, value, label = symptom_text(conn, row["report_id"]), None, thresholds.NOT_ASSESSED
        else:
            content = row["metric"]
            value = f"{row['value']} {row['unit']}" if row["unit"] else row["value"]
            label = thresholds.evaluate(conn, row["metric"], row["value"], row["glucose_context"])
        danger = row["case_source"] == "Chatbot" and danger_of(row)       # D-101: the bot's danger flag
        symptoms = {r[0] for r in conn.execute("SELECT symptom FROM REPORT_SYMPTOM WHERE report_id = ?", (row["report_id"],))} if row["report_id"] else set()
        result.append({
            "case_id": row["case_id"], "mother": row["full_name"], "status": row["status"],
            "week": gestational_week(date.fromisoformat(row["edd"]), today) if row["edd"] else None,
            "case_source": row["case_source"], "content": content, "value": value, "label": label,
            "submitted_at": row["submitted_at"] or row["created_at"],
            "danger": danger, "alarm": bool(ALARM_SYMPTOMS & symptoms) or danger,     # same test as the dashboard flag "Alarm symptoms" (PRD M3, D-73)
            "waiting": waiting_minutes(row["submitted_at"] or row["created_at"], row["status"], at),
        })
        if me is not None and me["role"] == "Doctor":      # S-061D #14: whose mother, and is he here
            doc = responsible(conn, row["user_id"], today)
            result[-1]["responsible"] = doc
            result[-1]["covering"] = covers and doc is not None and doc["availability"] == "Away" and doc["staff_id"] != viewer
    return sort_cases(result, order)


def doctor_badge(conn: sqlite3.Connection, staff_id: str) -> int:
    return conn.execute("SELECT COUNT(*) FROM CARE_CASE WHERE status = 'Escalated to doctor' AND assigned_doctor_id = ?",
                        (staff_id,)).fetchone()[0]
