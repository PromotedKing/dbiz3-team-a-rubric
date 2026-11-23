"""S-061 "Cases to handle": CLI FR-002, FR-020, BR-007; doctor badge (ALR FR-009, DM-32 — derived, not stored)."""
import sqlite3
from datetime import date

from ..alr import thresholds
from ..alr.reports import gestational_week
from ..bot.chat import danger_of
from ..clock import now
from . import actions
from .urgency import (
    ALARM_SYMPTOMS,
    STATUS_ESCALATED,
    STATUS_NOT_VIEWED,
    STATUS_RESOLVED,
    STATUS_VIEWED,
    STATUSES,
    URGENCY_CRITICAL,
    URGENCY_NORMAL,
    URGENCY_WARNING,
    evaluate_case_urgency,
    format_waiting_time,
    gestational_stage_text,
)

SYMPTOM_LABELS = {
    "Waters breaking or fluid leakage": "Waters breaking / fluid leakage",
    "Severe headache, dizziness or blurred vision": "Severe headache / dizziness / blurred vision",
}


def symptom_text(conn: sqlite3.Connection, report_id: str) -> str:
    rows = conn.execute("SELECT symptom FROM REPORT_SYMPTOM WHERE report_id = ? ORDER BY symptom", (report_id,))
    return ", ".join(SYMPTOM_LABELS.get(r[0], r[0]) for r in rows)


def list_cases(
    conn: sqlite3.Connection,
    status: str | None = None,
    viewer: str | None = None,
    sort: str = "newest",
    q: str | None = None,
) -> list[dict]:
    """`viewer` applies BR-010 (D-96, proposed); left out, nothing is filtered.

    sort: 'priority' (khẩn lên đầu, chờ lâu lên trước) hoặc 'newest' (mới nhất lên trước).
    q: lọc theo tên mẹ (nếu có).
    """
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
    current_time = now()
    today = current_time.date()
    mine = actions.visible_users(conn, viewer, today) if viewer else None
    result = []
    for row in rows:
        if mine is not None and row["user_id"] not in mine and not (      # BR-010
                row["assigned_doctor_id"] is None and row["status"] == STATUS_ESCALATED):   # BR-011 step 4
            continue
        if q and q.strip().lower() not in row["full_name"].lower():
            continue

        raw_symptoms = []
        if row["report_id"]:
            raw_symptoms = [r[0] for r in conn.execute("SELECT symptom FROM REPORT_SYMPTOM WHERE report_id = ? ORDER BY symptom", (row["report_id"],))]

        if row["case_source"] == "Chatbot":
            content, value, label = row["question"], None, thresholds.NOT_ASSESSED
            main_symptom = row["question"]
        elif row["value"] is None:     # symptom report
            content, value, label = symptom_text(conn, row["report_id"]), None, thresholds.NOT_ASSESSED
            main_symptom = content
        else:
            content = row["metric"]
            value = f"{row['value']} {row['unit']}" if row["unit"] else row["value"]
            label = thresholds.evaluate(conn, row["metric"], row["value"], row["glucose_context"])
            symp = symptom_text(conn, row["report_id"])
            real_symps = [s for s in raw_symptoms if s != "No symptoms"]
            if real_symps:
                main_symptom = f"{row['metric']} · {symp}"
            else:
                main_symptom = row["metric"]

        submitted_at = row["submitted_at"] or row["created_at"]
        waited = format_waiting_time(submitted_at, current_time)
        danger = (row["case_source"] == "Chatbot" and danger_of(row))

        # Đánh giá mức khẩn qua hàm dùng chung
        urgency = evaluate_case_urgency(
            conn,
            label=label,
            symptoms=raw_symptoms,
            danger=danger,
            case_source=row["case_source"],
            waited_minutes=waited["total_minutes"],
        )
        waited["is_overdue"] = urgency["is_overdue"]

        # Kiểm tra cờ bác sĩ trả về: Ca ở Chưa xem và đã từng được chuyển bác sĩ hoặc đổi bởi Doctor
        returned_by_doctor = False
        if row["status"] == STATUS_NOT_VIEWED:
            hist = conn.execute(
                "SELECT 1 FROM CASE_STATUS_HISTORY WHERE case_id = ? AND (role = 'Doctor' OR status = ?)",
                (row["case_id"], STATUS_ESCALATED),
            ).fetchone()
            if hist:
                returned_by_doctor = True

        stage_text = gestational_stage_text(row["edd"], today)

        result.append({
            "case_id": row["case_id"],
            "mother": row["full_name"],
            "status": row["status"],
            "week": gestational_week(date.fromisoformat(row["edd"]), today) if row["edd"] else None,
            "stage_text": stage_text,
            "case_source": row["case_source"],
            "content": content,
            "value": value,
            "label": label,
            "submitted_at": submitted_at,
            "danger": danger,
            "urgency": urgency,
            "waited": waited,
            "returned_by_doctor": returned_by_doctor,
            "main_symptom": main_symptom,
        })

    if sort == "priority":
        # Sắp xếp theo yêu cầu: ca vượt ngưỡng (khẩn) lên đầu, sau đó ca chờ lâu hơn lên trước
        level_order = {URGENCY_CRITICAL: 0, URGENCY_WARNING: 1, URGENCY_NORMAL: 2}
        result.sort(key=lambda r: (level_order.get(r["urgency"]["level"], 3), -r["waited"]["total_minutes"]))
    else:
        result.sort(key=lambda r: r["submitted_at"], reverse=True)

    return result


def status_counts(conn: sqlite3.Connection, viewer: str | None = None) -> dict[str, int]:
    """Đếm số ca cho 4 tab theo phân quyền của viewer."""
    today = now().date()
    mine = actions.visible_users(conn, viewer, today) if viewer else None
    counts = {s: 0 for s in STATUSES}
    for s in STATUSES:
        rows = conn.execute(
            "SELECT case_id, user_id, assigned_doctor_id, status FROM CARE_CASE WHERE status = ?",
            (s,),
        ).fetchall()
        for r in rows:
            if mine is not None and r["user_id"] not in mine and not (
                r["assigned_doctor_id"] is None and r["status"] == STATUS_ESCALATED
            ):
                continue
            counts[s] += 1
    return counts


def doctor_badge(conn: sqlite3.Connection, staff_id: str) -> int:
    return conn.execute("SELECT COUNT(*) FROM CARE_CASE WHERE status = 'Escalated to doctor' AND assigned_doctor_id = ?",
                        (staff_id,)).fetchone()[0]
