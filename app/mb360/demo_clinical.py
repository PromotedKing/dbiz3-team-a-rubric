"""Clinical history installed only when creating a fresh demo database."""
import json
import uuid
from datetime import date, datetime, timedelta

from .alr import cases, reports, thresholds
from .bot.chat import HANDOFF_TEXT
from .cli import actions


def _id(user, label):
    return str(uuid.uuid5(uuid.NAMESPACE_URL, f"mb360-demo-clinical/{user}/{label}"))


def install_visits(conn, user, lmp, visits):
    old = conn.execute("SELECT visit_id FROM VISIT WHERE user_id=? ORDER BY visit_date DESC", (user,)).fetchall()
    for index, visit in enumerate(reversed(visits)):
        week, image = visit["week"], visit["image"]
        day = (lmp + timedelta(weeks=week)).isoformat()
        measured = f"{day} 09:00"
        visit_id = old[index][0] if index < len(old) else _id(user, f"visit/{week}")
        conn.execute("""INSERT INTO VISIT (visit_id,user_id,visit_date,facility,visit_type,ultrasound_image,
                            ultrasound_report_date,gestational_week) VALUES (?,?,?,'Bệnh viện Thu Cúc',?,?,?,?)
                        ON CONFLICT(visit_id) DO UPDATE SET visit_date=excluded.visit_date,
                            visit_type=excluded.visit_type, ultrasound_image=excluded.ultrasound_image,
                            ultrasound_report_date=excluded.ultrasound_report_date, gestational_week=excluded.gestational_week,
                            fetal_length=NULL, estimated_fetal_weight=NULL, conclusion=NULL, doctor_note=NULL""",
                     (visit_id, user, day, "Khám thai · OGTT" if week == 27 else "Khám thai định kỳ",
                      image, day if image else None, week))
        for metric, value, unit in visit["metrics"]:
            row = conn.execute("SELECT record_id FROM HEALTH_METRIC_RECORD WHERE visit_id=? AND metric=?",
                               (visit_id, metric)).fetchone()
            group = {"Weight": "Group 1", "Fetal heart rate": "Visit"}.get(metric, "Group 2")
            conn.execute("""INSERT INTO HEALTH_METRIC_RECORD (record_id,user_id,metric,metric_group,value,unit,
                            glucose_context,measured_at,source,visit_id,gestational_week,created_at)
                            VALUES (?,?,?,?,?,?,?,?,'From visit',?,?,?)
                            ON CONFLICT(record_id) DO UPDATE SET value=excluded.value, measured_at=excluded.measured_at,
                            gestational_week=excluded.gestational_week, created_at=excluded.created_at""",
                         (row[0] if row else _id(user, f"visit/{week}/{metric}"), user, metric, group, value, unit,
                          "fasting" if metric == "Blood glucose" else None, measured, visit_id, week, measured))
        conn.execute("UPDATE WATCH_FLAG SET flagged_at=? WHERE visit_id=?", (day, visit_id))
        conn.execute("""UPDATE NOTIFICATION SET subtitle=?, created_at=?,
                            read_at=CASE WHEN read_at IS NULL THEN NULL ELSE ? END
                        WHERE visit_id=? AND type='Visit result'""",
                     (f"Visit {day}", f"{day} 11:00", f"{day} 12:00", visit_id))


def align_cases(conn, user, lmp, today, ref):
    """Shift related event timestamps together, keeping case IDs and time intervals."""
    if ref not in {"tci-000123", "tci-000126", "tci-000128"}:
        return
    latest = conn.execute("SELECT MAX(visit_date) FROM VISIT WHERE user_id=?", (user,)).fetchone()[0]
    anchor = date(2026, 9, 27)
    target = min(today - timedelta(days=1), date.fromisoformat(latest) + timedelta(days=3))
    delta = (target - anchor).days
    modifier = f"{delta:+d} days"
    for table, columns, predicate in (
        ("METRIC_REPORT", ("submitted_at",), "user_id=?"),
        ("CARE_CASE", ("created_at", "closed_at"), "user_id=?"),
        ("CASE_STATUS_HISTORY", ("changed_at",), "case_id IN (SELECT case_id FROM CARE_CASE WHERE user_id=?)"),
        ("STAFF_RESPONSE", ("sent_at",), "case_id IN (SELECT case_id FROM CARE_CASE WHERE user_id=?)"),
        ("CHAT_MESSAGE", ("sent_at",), "conversation_id IN (SELECT conversation_id FROM CONVERSATION WHERE user_id=?)"),
        ("NOTIFICATION", ("created_at", "read_at"), "user_id=? AND type IN ('Report','Instruction reminder')"),
        ("HEALTH_METRIC_RECORD", ("measured_at", "created_at"),
         "record_id IN (SELECT health_metric_record_id FROM METRIC_REPORT WHERE user_id=?)"),
    ):
        updates = ", ".join(f"{col}=strftime('%Y-%m-%d %H:%M', {col}, ?)" for col in columns)
        conn.execute(f"UPDATE {table} SET {updates} WHERE {predicate}", (modifier,) * len(columns) + (user,))
    for row in conn.execute("""SELECT h.record_id,h.measured_at FROM HEALTH_METRIC_RECORD h
                            JOIN METRIC_REPORT r ON r.health_metric_record_id=h.record_id WHERE r.user_id=?""", (user,)):
        week = (date.fromisoformat(row[1][:10]) - lmp).days // 7
        conn.execute("UPDATE HEALTH_METRIC_RECORD SET gestational_week=? WHERE record_id=?", (week, row[0]))
    if ref == "tci-000126":
        conn.execute("UPDATE WATCH_FLAG SET flagged_at=? WHERE user_id=? AND active=1", (latest, user))


def install_case(conn, user, kind, lmp, now):
    if kind == "chatbot":
        conv, question = _id(user, "conversation"), _id(user, "question")
        week = (now.date() - lmp).days // 7
        at = now.strftime(reports.DB_TIME)
        conn.execute("INSERT INTO CONVERSATION VALUES (?,?,?)",
                     (conv, user, json.dumps({"gestational_week": week, "earlier_turns": 0})))
        conn.execute("""INSERT INTO CHAT_MESSAGE (message_id,conversation_id,sender,text,sent_at,parsed_intent,is_risk,handoff_choice)
                        VALUES (?,?,'Mother',?,?,?,1,'Connect to nurse'),
                               (?,?,'Chatbot',?,?,NULL,0,NULL)""",
                     (question, conv, "Em thấy ra máu và muốn hỏi y tá.", at, json.dumps({"intent": "needs_nurse"}), _id(user, "answer"), conv, HANDOFF_TEXT, at))
        conn.execute("INSERT INTO AI_RESPONSE_LOG VALUES (?,?,?,?)",
                     (_id(user, "log"), conv, HANDOFF_TEXT, json.dumps({"client": "demo"})))
        cases.open_chatbot_case(conn, user, question, now)
    elif kind == "escalated_bp":
        measured = datetime.combine(lmp + timedelta(weeks=38), datetime.min.time()).replace(hour=18)
        doctor = conn.execute("SELECT staff_id FROM STAFF WHERE full_name='Phạm Quốc Dũng'").fetchone()[0]
        nurse = conn.execute("SELECT staff_id FROM STAFF WHERE full_name='Trần Thị B'").fetchone()[0]
        conn.execute("UPDATE PATIENT_ASSIGNMENT SET valid_to=NULL, valid_from=? WHERE user_id=? AND doctor_id=?",
                     (measured.date().isoformat(), user, doctor))
        visit = conn.execute("SELECT visit_id FROM VISIT WHERE user_id=? AND gestational_week=38", (user,)).fetchone()[0]
        conn.execute("""INSERT INTO WATCH_FLAG (flag_id,user_id,visit_id,metric,flagged_by,flagged_at,active)
                        VALUES (?,?,?,'Blood pressure',?,?,1)""",
                     (_id(user, "bp"), user, visit, doctor, measured.date().isoformat()))
        report = reports.store_report(conn, user, {"metric": "Blood pressure", "systolic": "140", "diastolic": "90",
                                      "measured_at": measured.isoformat(timespec="minutes"), "symptoms": ["No symptoms"]}, measured)
        assert thresholds.evaluate(conn, "Blood pressure", report["value"]) == "Above threshold"
        case = cases.open_case(conn, user, report["report_id"], "Metric report", measured)
        conn.commit()
        actions.mark_viewed(conn, case, nurse, measured + timedelta(minutes=5))
        actions.escalate(conn, case, nurse, measured + timedelta(minutes=10))
