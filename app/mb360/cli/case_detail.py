"""S-064 data: CLI FR-003, FR-007, FR-008, FR-010, FR-014, FR-015, BR-009 (D-78), CLI-01."""
import sqlite3
from ..bot.chat import danger_of
from datetime import date

from ..alr import thresholds
from ..alr.reports import gestational_week
from ..clock import now
from .dashboard import ALARM_SYMPTOMS
from .queue import symptom_text


def load(conn: sqlite3.Connection, case_id: str) -> dict | None:
    case = conn.execute("SELECT * FROM CARE_CASE WHERE case_id = ?", (case_id,)).fetchone()
    if case is None:
        return None
    uid = case["user_id"]
    mother = conn.execute("SELECT * FROM USER_ACCOUNT WHERE user_id = ?", (uid,)).fetchone()
    profile = conn.execute("SELECT * FROM PREGNANCY_PROFILE WHERE user_id = ?", (uid,)).fetchone()
    clinical = conn.execute("SELECT * FROM PATIENT_CLINICAL_PROFILE WHERE user_id = ?", (uid,)).fetchone()
    visits = conn.execute("SELECT * FROM VISIT WHERE user_id = ? ORDER BY visit_date DESC", (uid,)).fetchall()
    flags = conn.execute("""SELECT w.*, s.full_name AS doctor_name FROM WATCH_FLAG w JOIN STAFF s ON s.staff_id = w.flagged_by
                            WHERE w.user_id = ? AND w.active = 1 ORDER BY w.metric""", (uid,)).fetchall()
    week = gestational_week(date.fromisoformat(profile["edd"]), now().date()) if profile else None

    report = record = None
    symptoms = ""
    raw_symptoms: list[str] = []
    label = thresholds.NOT_ASSESSED
    transcript = []
    question_id = case["chat_message_id"]
    if case["metric_report_id"]:
        report = conn.execute("SELECT * FROM METRIC_REPORT WHERE report_id = ?", (case["metric_report_id"],)).fetchone()
        symptoms = symptom_text(conn, report["report_id"])
        raw_symptoms = [r[0] for r in conn.execute("SELECT symptom FROM REPORT_SYMPTOM WHERE report_id = ?", (report["report_id"],))]
        if report["health_metric_record_id"]:
            record = conn.execute("SELECT * FROM HEALTH_METRIC_RECORD WHERE record_id = ?",
                                  (report["health_metric_record_id"],)).fetchone()
            label = thresholds.evaluate(conn, record["metric"], record["value"], record["glucose_context"])
    else:   # chatbot case: the whole conversation of the escalated question (D-78)
        conv = conn.execute("SELECT conversation_id FROM CHAT_MESSAGE WHERE message_id = ?", (question_id,)).fetchone()[0]
        transcript = conn.execute("SELECT * FROM CHAT_MESSAGE WHERE conversation_id = ? ORDER BY sent_at", (conv,)).fetchall()

    metric = record["metric"] if record else (flags[0]["metric"] if flags else "Blood pressure")
    history = conn.execute(   # CLI-01: never Self-entered
        """SELECT * FROM HEALTH_METRIC_RECORD WHERE user_id = ? AND metric = ? AND source IN ('From visit', 'Doctor-assigned')
           ORDER BY measured_at""", (uid, metric)).fetchall()
    threshold = thresholds.card_text(conn, metric, record["glucose_context"] if record else None) if metric != "Fetal heart rate" else None

    responses = conn.execute(
        """SELECT s.*, st.full_name, t.content AS template_text FROM STAFF_RESPONSE s
           JOIN STAFF st ON st.staff_id = s.responder_id LEFT JOIN GUIDANCE_TEMPLATE t ON t.template_id = s.template_id
           WHERE s.case_id = ? ORDER BY s.sent_at""", (case_id,)).fetchall()
    latest_visit = visits[0] if visits else None
    latest_values = conn.execute("SELECT * FROM HEALTH_METRIC_RECORD WHERE visit_id = ? ORDER BY metric",
                                 (latest_visit["visit_id"],)).fetchall() if latest_visit else []
    danger = bool(question_id) and danger_of(conn.execute("SELECT * FROM CHAT_MESSAGE WHERE message_id = ?", (question_id,)).fetchone())
    # Look only, no new rule: the same tests as the dashboard flags (above threshold from THRESHOLD_RULE, PRD M3 alarm list, D-101 danger flag)
    alarm = bool(ALARM_SYMPTOMS.intersection(raw_symptoms)) or danger
    other_cases = conn.execute(
        """SELECT case_id FROM CARE_CASE WHERE user_id = ? AND case_id != ? AND status != 'Resolved'
           ORDER BY created_at""", (uid, case_id)).fetchall()
    return {"case": case, "mother": mother, "profile": profile, "clinical": clinical, "week": week, "flags": flags,
            "report": report, "record": record, "symptoms": symptoms, "label": label, "transcript": transcript,
            "question_id": question_id, "danger": danger, "alarm": alarm, "other_cases": [r["case_id"] for r in other_cases],
            "history_metric": metric, "history": history, "threshold": threshold,
            "responses": responses, "visits": visits, "latest_visit": latest_visit, "latest_values": latest_values}
