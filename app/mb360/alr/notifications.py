"""ALR FR-018: "Report" notifications for the mother (research R5; wording S-009 #8, #11; §10 Q23).

`notify` writes one NOTIFICATION row in the caller's transaction (the caller commits); it writes
nothing when the mother's "Report responses" switch (NOTIFICATION_PREFERENCE.report_response) is off."""
import sqlite3
import uuid
from datetime import datetime

from . import thresholds

DB_TIME = "%Y-%m-%d %H:%M"
SYMPTOM_LABELS = {
    "Waters breaking or fluid leakage": "Waters breaking / fluid leakage",
    "Severe headache, dizziness or blurred vision": "Severe headache / dizziness / blurred vision",
}
STATUS_EVENTS = ("Viewed", "Escalated to doctor", "Resolved")


def _subject(conn: sqlite3.Connection, case: sqlite3.Row) -> dict:
    """What the notification is about: metric report, symptom report or chatbot question."""
    if case["case_source"] == "Chatbot":
        q = conn.execute("SELECT text FROM CHAT_MESSAGE WHERE message_id = ?", (case["chat_message_id"],)).fetchone()[0]
        return {"what": "question", "code": None, "detail": q}
    rep = conn.execute("SELECT * FROM METRIC_REPORT WHERE report_id = ?", (case["metric_report_id"],)).fetchone()
    if rep["health_metric_record_id"]:
        h = conn.execute("SELECT * FROM HEALTH_METRIC_RECORD WHERE record_id = ?", (rep["health_metric_record_id"],)).fetchone()
        label = thresholds.evaluate(conn, h["metric"], h["value"], h["glucose_context"])
        value = f"{h['value']} {h['unit']}" if h["unit"] else h["value"]
        detail = f"{value} · {label}"
    else:
        syms = [r[0] for r in conn.execute("SELECT symptom FROM REPORT_SYMPTOM WHERE report_id = ? ORDER BY symptom", (rep["report_id"],))]
        detail = ", ".join(SYMPTOM_LABELS.get(s, s) for s in syms)
    return {"what": f"{rep['metric']} report", "code": rep["report_code"], "detail": detail}


def notify(conn: sqlite3.Connection, case_id: str, event: str, now: datetime, staff_id: str | None = None) -> str | None:
    case = conn.execute("SELECT * FROM CARE_CASE WHERE case_id = ?", (case_id,)).fetchone()
    pref = conn.execute("SELECT report_response FROM NOTIFICATION_PREFERENCE WHERE user_id = ?", (case["user_id"],)).fetchone()
    if pref is not None and not pref[0]:
        return None
    s = _subject(conn, case)
    ref = f"Report {s['code']}" if s["code"] else None
    if event == "created":
        title = ("Your question has been sent to a nurse" if s["what"] == "question"
                 else f"Your {s['what']} has been sent to clinical staff")
        subtitle = s["detail"]
    elif event == "response":
        staff = conn.execute("SELECT full_name, role FROM STAFF WHERE staff_id = ?", (staff_id,)).fetchone()
        title = f"{staff['role']} {staff['full_name']} responded to your {s['what']}"
        subtitle = f"{ref} · {case['status']}" if ref else case["status"]
    elif event in STATUS_EVENTS:
        title = f"Your {s['what']} is {event}"
        subtitle = ref
    else:
        raise ValueError(f"unknown notification event {event!r}")
    notification_id = str(uuid.uuid4())
    conn.execute(
        """INSERT INTO NOTIFICATION (notification_id, user_id, type, title, subtitle, created_at, read_at,
               case_id, visit_id, watch_flag_id, appointment_ref)
           VALUES (?, ?, 'Report', ?, ?, ?, NULL, ?, NULL, NULL, NULL)""",
        (notification_id, case["user_id"], title[:100], subtitle[:200] if subtitle else None, now.strftime(DB_TIME), case_id),
    )
    return notification_id
