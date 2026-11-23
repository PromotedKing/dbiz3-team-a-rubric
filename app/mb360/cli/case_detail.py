"""S-064 data: CLI FR-003, FR-007, FR-008, FR-010, FR-014, FR-015, BR-009 (D-78), CLI-01."""
import sqlite3
from datetime import date

from ..alr import thresholds
from ..alr.reports import gestational_week
from ..bot.chat import danger_of
from ..clock import now
from .queue import symptom_text
from .urgency import (
    ESCALATION_REASONS,
    STATUS_ESCALATED,
    STATUS_NOT_VIEWED,
    STATUS_RESOLVED,
    STATUS_VIEWED,
    evaluate_case_urgency,
    format_waiting_time,
    gestational_stage_text,
)


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
    today = now().date()
    week = gestational_week(date.fromisoformat(profile["edd"]), today) if profile else None

    report = record = None
    symptoms = ""
    raw_symptoms = []
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
        """SELECT s.*, st.full_name, t.content AS template_text, t.title AS template_title FROM STAFF_RESPONSE s
           JOIN STAFF st ON st.staff_id = s.responder_id LEFT JOIN GUIDANCE_TEMPLATE t ON t.template_id = s.template_id
           WHERE s.case_id = ? ORDER BY s.sent_at""", (case_id,)).fetchall()
    latest_visit = visits[0] if visits else None
    latest_values = conn.execute("SELECT * FROM HEALTH_METRIC_RECORD WHERE visit_id = ? ORDER BY metric",
                                 (latest_visit["visit_id"],)).fetchall() if latest_visit else []

    danger = bool(question_id) and danger_of(
        conn.execute("SELECT * FROM CHAT_MESSAGE WHERE message_id = ?", (question_id,)).fetchone())

    # Main symptom text
    if case["case_source"] == "Chatbot":
        main_symptom = conn.execute("SELECT text FROM CHAT_MESSAGE WHERE message_id = ?", (question_id,)).fetchone()[0]
    elif record:
        symp = symptoms if symptoms and symptoms != "No symptoms" else ""
        main_symptom = f"{record['metric']}: {record['value']} {record['unit'] or ''}".strip() + (f" · {symp}" if symp else "")
    else:
        main_symptom = symptoms or "Báo cáo triệu chứng"

    # Waiting time & urgency
    submitted_at = (report["submitted_at"] if report else None) or case["created_at"]
    waited = format_waiting_time(submitted_at, now())
    urgency = evaluate_case_urgency(
        conn,
        label=label,
        symptoms=raw_symptoms,
        danger=danger,
        case_source=case["case_source"],
        waited_minutes=waited["total_minutes"],
    )
    waited["is_overdue"] = urgency["is_overdue"]

    # Cờ bác sĩ trả về
    returned_by_doctor = False
    if case["status"] == STATUS_NOT_VIEWED:
        hist = conn.execute(
            "SELECT 1 FROM CASE_STATUS_HISTORY WHERE case_id = ? AND (role = 'Doctor' OR status = ?)",
            (case_id, STATUS_ESCALATED),
        ).fetchone()
        if hist:
            returned_by_doctor = True

    # Chỉ hiển thị 1 giá trị gần nhất cho màn y tá
    # Giá trị vượt ngưỡng tô đỏ + mũi tên ↑↓; chỉ số bình thường dùng chữ xám nhạt
    latest_metric = None
    if record:
        is_above = (label == thresholds.ABOVE)
        arrow = "↑" if is_above else ""
        latest_metric = {
            "metric": record["metric"],
            "value": record["value"],
            "unit": record["unit"] or "",
            "is_above": is_above,
            "arrow": arrow,
            "display_text": f"{arrow} {record['value']} {record['unit'] or ''}".strip(),
            "measured_at": record["measured_at"],
            "source": record["source"],
            "label": label,
        }

    # Timeline lịch sử xử lý (ai xem, ai chuyển, lúc nào)
    history_rows = conn.execute(
        """SELECT h.status, h.changed_at, h.role, s.full_name
           FROM CASE_STATUS_HISTORY h
           LEFT JOIN STAFF s ON s.staff_id = h.changed_by
           WHERE h.case_id = ?
           ORDER BY h.changed_at""",
        (case_id,),
    ).fetchall()

    history_timeline = []
    # 1. Thời điểm gửi ca
    history_timeline.append({
        "time_text": submitted_at,
        "raw_time": submitted_at,
        "actor_text": f"Thai phụ: {mother['full_name']}",
        "icon": "📝",
        "detail_text": f"Gửi {case['case_source'].lower()} lên hệ thống",
    })

    # 2. Các bước đổi trạng thái
    for h in history_rows:
        role_label = "Y tá" if h["role"] == "Nurse" else ("Bác sĩ" if h["role"] == "Doctor" else "Hệ thống")
        name = f" · {h['full_name']}" if h["full_name"] else ""
        actor = f"{role_label}{name}"
        if h["status"] == STATUS_VIEWED:
            icon = "👁️"
            action_text = "Đã đánh dấu xem ca"
        elif h["status"] == STATUS_ESCALATED:
            icon = "➡️"
            action_text = "Đã chuyển ca cho bác sĩ chuyên khoa"
        elif h["status"] == STATUS_RESOLVED:
            icon = "✅"
            action_text = "Đã hoàn thành và đóng ca"
        else:
            icon = "🔄"
            action_text = f"Cập nhật trạng thái: {h['status']}"

        history_timeline.append({
            "time_text": h["changed_at"],
            "raw_time": h["changed_at"],
            "actor_text": actor,
            "icon": icon,
            "detail_text": action_text,
        })

    # 3. Các phản hồi gửi hướng dẫn
    for r in responses:
        role_label = "Y tá" if r["responder_role"] == "Nurse" else "Bác sĩ"
        tpl_title = r["template_title"] if "template_title" in r.keys() else None
        tpl_note = f" (Mẫu: {tpl_title})" if tpl_title else ""
        content = (r["custom_text"] or r["template_text"] or "").strip()
        history_timeline.append({
            "time_text": r["sent_at"],
            "raw_time": r["sent_at"],
            "actor_text": f"{role_label} · {r['full_name']}",
            "icon": "💬",
            "detail_text": f"Gửi hướng dẫn{tpl_note}: {content}",
        })

    # Sắp xếp timeline theo thời gian tăng dần
    history_timeline.sort(key=lambda x: x["raw_time"])

    stage_text = gestational_stage_text(profile["edd"], today) if profile else "—"

    return {
        "case": case,
        "mother": mother,
        "profile": profile,
        "clinical": clinical,
        "week": week,
        "stage_text": stage_text,
        "flags": flags,
        "report": report,
        "record": record,
        "symptoms": symptoms,
        "label": label,
        "transcript": transcript,
        "question_id": question_id,
        "danger": danger,
        "history_metric": metric,
        "history": history,
        "threshold": threshold,
        "responses": responses,
        "visits": visits,
        "latest_visit": latest_visit,
        "latest_values": latest_values,
        "urgency": urgency,
        "waited": waited,
        "returned_by_doctor": returned_by_doctor,
        "main_symptom": main_symptom,
        "latest_metric": latest_metric,
        "history_timeline": history_timeline,
        "escalation_reasons": ESCALATION_REASONS,
    }
