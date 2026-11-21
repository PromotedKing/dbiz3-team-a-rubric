"""S-061 "Cases to handle": CLI FR-002, FR-020, BR-007; Priority order and Waiting column (D-104);
doctor badge (ALR FR-009, DM-32 — derived, not stored)."""
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


SORTS = ("Priority", "Newest")     # S-061 #7: the nurse's default is Priority (D-104); the doctor keeps Newest (S-061D #7)
DB_TIME = "%Y-%m-%d %H:%M"


def waiting(submitted_at: str, status: str, at: datetime) -> dict | None:
    """S-061 #13A: time from submitted_at / created_at to now for a case that is not "Resolved" — calculated,
    not stored, no time limit and no colour threshold (D-85). None for "Resolved"."""
    if status == "Resolved":
        return None
    minutes = max(0, int((at - datetime.strptime(submitted_at, DB_TIME)).total_seconds() // 60))
    return {"days": minutes // 1440, "hours": minutes % 1440 // 60, "minutes": minutes % 60, "total": minutes}


def priority_order(rows: list[dict]) -> list[dict]:
    """S-061 SR-006 (D-104): "Above threshold" and "Not viewed" first, then every other open case by waiting time,
    longest first; "Resolved" cases (no waiting time) last, newest first. Only the order changes — no new status."""
    def key(r):
        if r["status"] == "Resolved":
            return (2, 0, "")
        return (0 if r["label"] == thresholds.ABOVE and r["status"] == "Not viewed" else 1, 0, r["submitted_at"])
    resolved = sorted((r for r in rows if r["status"] == "Resolved"), key=lambda r: r["submitted_at"], reverse=True)
    return sorted((r for r in rows if r["status"] != "Resolved"), key=key) + resolved


def list_cases(conn: sqlite3.Connection, status: str | None = None, viewer: str | None = None,
               sort: str = "Newest") -> list[dict]:
    """`viewer` applies BR-010 (D-96, proposed); left out, nothing is filtered.
    `sort`: "Newest" (default) or "Priority" (D-104, the nurse's list)."""
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
    at = now()
    today = at.date()
    mine = actions.visible_users(conn, viewer, today) if viewer else None
    care: dict[str, dict] = {}       # S-061D #14: the mother's responsible doctor and whether he is Available / Away

    def responsible(user_id: str) -> dict:
        if user_id not in care:
            doctor = actions.responsible_doctor(conn, user_id, today)
            staff = conn.execute("SELECT full_name, availability FROM STAFF WHERE staff_id = ?", (doctor,)).fetchone() if doctor else None
            care[user_id] = {"id": doctor, "name": staff["full_name"] if staff else None,
                             "availability": staff["availability"] if staff else None}
        return care[user_id]
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
        result.append({
            "case_id": row["case_id"], "mother": row["full_name"], "status": row["status"],
            "week": gestational_week(date.fromisoformat(row["edd"]), today) if row["edd"] else None,
            "case_source": row["case_source"], "content": content, "value": value, "label": label,
            "submitted_at": row["submitted_at"] or row["created_at"],
            "danger": row["case_source"] == "Chatbot" and danger_of(row),       # D-101: the bot's danger flag
            "waiting": waiting(row["submitted_at"] or row["created_at"], row["status"], at),
            "responsible": responsible(row["user_id"]),
            # "Covering" tag: the signed-in doctor sees this mother only because he is on duty for an Away doctor (BR-010)
            "covering": bool(viewer) and responsible(row["user_id"])["id"] not in (None, viewer)
                        and actions.staff_role(conn, viewer) == "Doctor",
        })
    if sort == "Priority":
        return priority_order(result)
    result.sort(key=lambda r: r["submitted_at"], reverse=True)
    return result


def doctor_badge(conn: sqlite3.Connection, staff_id: str) -> int:
    return conn.execute("SELECT COUNT(*) FROM CARE_CASE WHERE status = 'Escalated to doctor' AND assigned_doctor_id = ?",
                        (staff_id,)).fetchone()[0]
