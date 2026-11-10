"""Clinical dashboard and case board (D-85, after the reference pictures in the v1.0.0 review): counts and groups read from
the cases as they stand. Nothing is stored and no new threshold is made up: "above threshold" comes from THRESHOLD_RULE,
the alarm symptoms are the PRD M3 list (D-73), waiting time is shown, never judged."""
import sqlite3
from datetime import date, datetime

from ..alr import thresholds
from ..alr.reports import gestational_week
from .queue import SYMPTOM_LABELS

STATUSES = ("Not viewed", "Viewed", "Escalated to doctor", "Resolved")
SOURCES = ("Metric report", "Symptom", "Chatbot")
ALARM_SYMPTOMS = {"Vaginal bleeding", "Severe abdominal pain", "Waters breaking or fluid leakage",
                  "Severe headache, dizziness or blurred vision", "Absence of fetal movement"}      # PRD M3 alarm list (D-73)
FLAGS = {   # key: (label, test on an open case)
    "above": ("Above threshold, not viewed", lambda c: c["label"] == thresholds.ABOVE and c["status"] == "Not viewed"),
    "alarm": ("Alarm symptoms", lambda c: c["alarm"]),
    "unanswered": ("No response sent yet", lambda c: not c["answered"]),
    "doctor": ("Escalated, waiting for the doctor", lambda c: c["status"] == "Escalated to doctor" and not c["doctor_answered"]),
    "chatbot": ("From the chatbot", lambda c: c["case_source"] == "Chatbot"),
}
DB_TIME = "%Y-%m-%d %H:%M"


def waited(created_at: str, now: datetime) -> dict:
    minutes = max(0, int((now - datetime.strptime(created_at, DB_TIME)).total_seconds() // 60))
    return {"days": minutes // 1440, "hours": minutes % 1440 // 60, "minutes": minutes % 60, "total": minutes}


def cases(conn: sqlite3.Connection, now: datetime, source: str | None = None, start: date | None = None,
          end: date | None = None, doctor_id: str | None = None) -> list[dict]:
    """Every case with what the dashboard and the board need, newest first."""
    sql = """SELECT c.case_id, c.status, c.case_source, c.created_at, c.closed_at, c.assigned_doctor_id, u.full_name, u.record_code, p.edd,
                    r.report_id, r.metric, h.value, h.unit, h.glucose_context, m.text AS question, d.full_name AS doctor,
                    (SELECT COUNT(*) FROM STAFF_RESPONSE s WHERE s.case_id = c.case_id) AS responses,
                    (SELECT COUNT(*) FROM STAFF_RESPONSE s WHERE s.case_id = c.case_id AND s.responder_role = 'Doctor') AS doctor_responses
             FROM CARE_CASE c JOIN USER_ACCOUNT u ON u.user_id = c.user_id
             LEFT JOIN PREGNANCY_PROFILE p ON p.user_id = c.user_id
             LEFT JOIN METRIC_REPORT r ON r.report_id = c.metric_report_id
             LEFT JOIN HEALTH_METRIC_RECORD h ON h.record_id = r.health_metric_record_id
             LEFT JOIN CHAT_MESSAGE m ON m.message_id = c.chat_message_id
             LEFT JOIN STAFF d ON d.staff_id = c.assigned_doctor_id
             WHERE (? IS NULL OR c.case_source = ?) AND (? IS NULL OR c.created_at >= ?) AND (? IS NULL OR c.created_at < date(?, '+1 day'))
               AND (? IS NULL OR c.assigned_doctor_id = ?)
             ORDER BY c.created_at DESC"""
    s, e = (start.isoformat() if start else None), (end.isoformat() if end else None)
    out = []
    for row in conn.execute(sql, (source, source, s, s, e, e, doctor_id, doctor_id)):
        symptoms = [r[0] for r in conn.execute("SELECT symptom FROM REPORT_SYMPTOM WHERE report_id = ? ORDER BY symptom", (row["report_id"],))] if row["report_id"] else []
        if row["case_source"] == "Chatbot":
            content, value, label = row["question"], None, thresholds.NOT_ASSESSED
        elif row["value"] is None:
            content, value, label = ", ".join(SYMPTOM_LABELS.get(x, x) for x in symptoms), None, thresholds.NOT_ASSESSED
        else:
            content, label = row["metric"], thresholds.evaluate(conn, row["metric"], row["value"], row["glucose_context"])
            value = f"{row['value']} {row['unit']}" if row["unit"] else row["value"]
        real_symptoms = [x for x in symptoms if x != "No symptoms"]
        out.append({
            "case_id": row["case_id"], "status": row["status"], "case_source": row["case_source"], "created_at": row["created_at"],
            "mother": row["full_name"], "record_code": row["record_code"], "doctor": row["doctor"],
            "week": gestational_week(date.fromisoformat(row["edd"]), now.date()) if row["edd"] else None,
            "content": content, "value": value, "label": label,
            "with_symptoms": ", ".join(SYMPTOM_LABELS.get(x, x) for x in real_symptoms) if row["value"] is not None else "",
            "alarm": bool(ALARM_SYMPTOMS.intersection(symptoms)), "answered": row["responses"] > 0, "doctor_answered": row["doctor_responses"] > 0,
            "waited": waited(row["created_at"], now) if row["status"] != "Resolved" else None,
        })
    return out


def summary(rows: list[dict], me_id: str | None = None, mine: list[dict] | None = None) -> dict:
    open_rows = [r for r in rows if r["status"] != "Resolved"]
    not_viewed = [r for r in rows if r["status"] == "Not viewed"]
    oldest = max((r["waited"]["total"] for r in not_viewed), default=None)
    by_status = [{"status": s, "count": sum(1 for r in rows if r["status"] == s)} for s in STATUSES]
    top = max([b["count"] for b in by_status] + [1])
    flags = [{"key": k, "label": label, "count": sum(1 for r in open_rows if test(r))} for k, (label, test) in FLAGS.items()]
    top_flag = max([f["count"] for f in flags] + [1])
    return {
        "total": len(rows), "open": len(open_rows), "not_viewed": len(not_viewed),
        "oldest": {"days": oldest // 1440, "hours": oldest % 1440 // 60, "minutes": oldest % 60} if oldest is not None else None,
        "above_open": sum(1 for r in open_rows if r["label"] == thresholds.ABOVE),
        "escalated": sum(1 for r in rows if r["status"] == "Escalated to doctor"),
        "mine": len([r for r in (mine or []) if r["status"] == "Escalated to doctor"]) if mine is not None else None,
        "by_status": [{**b, "width": round(b["count"] * 100 / top)} for b in by_status],
        "by_source": [{"source": s, "count": sum(1 for r in rows if r["case_source"] == s)} for s in SOURCES],
        "flags": [{**f, "width": round(f["count"] * 100 / top_flag)} for f in flags],
        "open_flagged": sum(1 for r in open_rows if any(test(r) for _, test in FLAGS.values())),
        "latest_open": sorted(open_rows, key=lambda r: (r["status"] != "Not viewed", r["label"] != thresholds.ABOVE, r["created_at"]))[:6],
    }


def board(rows: list[dict], done_limit: int = 12) -> list[dict]:
    """The columns of the board: open cases oldest first (who waits longest is on top), resolved newest first."""
    cols = []
    for s in STATUSES:
        items = [r for r in rows if r["status"] == s]
        if s == "Resolved":
            cols.append({"status": s, "count": len(items), "cases": items[:done_limit], "more": max(0, len(items) - done_limit)})
        else:
            cols.append({"status": s, "count": len(items), "cases": sorted(items, key=lambda r: r["created_at"]), "more": 0})
    return cols


def flagged_ids(rows: list[dict], flag: str) -> set[str]:
    test = FLAGS[flag][1]
    return {r["case_id"] for r in rows if r["status"] != "Resolved" and test(r)}
