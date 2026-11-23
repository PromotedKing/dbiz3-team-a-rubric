"""Shared urgency levels, thresholds, case statuses and waiting time rules.

Used by Nurse screens and Doctor screens (CLI-01, CLI-02, D-104).
Never hardcoded across disparate files: Trung and other team members can reuse this module directly.
"""
import sqlite3
from datetime import date, datetime
from typing import Any

from ..alr import thresholds
from ..alr.reports import gestational_week
from ..bot.chat import danger_of

DB_TIME = "%Y-%m-%d %H:%M"

# 1. Tên trạng thái ca dùng chung (Hằng số chuẩn - không hardcode chuỗi)
STATUS_NOT_VIEWED = "Not viewed"
STATUS_VIEWED = "Viewed"
STATUS_ESCALATED = "Escalated to doctor"
STATUS_RESOLVED = "Resolved"

STATUSES = (STATUS_NOT_VIEWED, STATUS_VIEWED, STATUS_ESCALATED, STATUS_RESOLVED)

STATUS_LABELS_VI = {
    STATUS_NOT_VIEWED: "Chưa xem",
    STATUS_VIEWED: "Đã xem",
    STATUS_ESCALATED: "Đã chuyển",
    STATUS_RESOLVED: "Đã xử lý",
}

# 2. Mức độ khẩn (Urgency levels)
URGENCY_CRITICAL = "critical"   # Khẩn (đỏ)
URGENCY_WARNING = "warning"     # Cần theo dõi (vàng / cam)
URGENCY_NORMAL = "normal"       # Bình thường (xanh / xám)

# Triệu chứng báo động (PRD M3 list, D-73)
ALARM_SYMPTOMS = {
    "Vaginal bleeding",
    "Severe abdominal pain",
    "Waters breaking or fluid leakage",
    "Severe headache, dizziness or blurred vision",
    "Absence of fetal movement",
}

# Bảng cấu hình mức khẩn dùng chung
URGENCY_CONFIG = {
    URGENCY_CRITICAL: {
        "level": URGENCY_CRITICAL,
        "label": "KHẨN",
        "icon": "⚠️",
        "color": "#D32F2F",       # Đỏ chuẩn WCAG AA+
        "bg_color": "#FFEBEE",    # Nền đỏ nhạt
        "border_color": "#D32F2F",
        "card_class": "urgency-critical",
        "overdue_minutes": 15,    # Ca khẩn: quá 15 phút tính là quá hạn
    },
    URGENCY_WARNING: {
        "level": URGENCY_WARNING,
        "label": "CẦN THEO DÕI",
        "icon": "⚡",
        "color": "#E65100",       # Cam/vàng đậm đủ tương phản
        "bg_color": "#FFF3E0",    # Nền vàng nhạt
        "border_color": "#E65100",
        "card_class": "urgency-warning",
        "overdue_minutes": 30,    # Ca cần theo dõi: quá 30 phút là quá hạn
    },
    URGENCY_NORMAL: {
        "level": URGENCY_NORMAL,
        "label": "BÌNH THƯỜNG",
        "icon": "✓",
        "color": "#2E7D32",       # Xanh lá đậm đủ tương phản
        "bg_color": "#E8F5E9",    # Nền xanh nhạt
        "border_color": "#757575",
        "card_class": "urgency-normal",
        "overdue_minutes": 60,    # Ca bình thường: quá 60 phút là quá hạn
    },
}

# Danh sách lý do chuyển bác sĩ có sẵn (cho Form chuyển bác sĩ)
ESCALATION_REASONS = [
    "Chỉ số vượt ngưỡng cảnh báo an toàn",
    "Triệu chứng bất thường / dấu hiệu cảnh báo",
    "Thai phụ yêu cầu tư vấn chuyên môn bác sĩ",
    "Câu hỏi Chatbot có dấu hiệu nguy cơ / rủi ro",
    "Cần chỉ định dùng thuốc / xét nghiệm bổ sung",
    "Lý do chuyên môn khác",
]


def format_waiting_time(created_at: str | None, now: datetime) -> dict:
    """Tính toán thời gian chờ từ created_at/submitted_at đến hiện tại."""
    if not created_at:
        return {"total_minutes": 0, "text": "0 phút", "days": 0, "hours": 0, "minutes": 0, "is_overdue": False}
    try:
        t = datetime.strptime(created_at, DB_TIME)
    except ValueError:
        try:
            t = datetime.fromisoformat(created_at)
        except Exception:
            return {"total_minutes": 0, "text": "—", "days": 0, "hours": 0, "minutes": 0, "is_overdue": False}
    minutes = max(0, int((now - t).total_seconds() // 60))
    days = minutes // 1440
    hours = (minutes % 1440) // 60
    rem_min = minutes % 60
    if days > 0:
        text = f"{days} ngày {hours} giờ"
    elif hours > 0:
        text = f"{hours} giờ {rem_min} phút"
    else:
        text = f"{minutes} phút"
    return {
        "total_minutes": minutes,
        "days": days,
        "hours": hours,
        "minutes": rem_min,
        "text": text,
        "is_overdue": False,  # sẽ gán dựa theo mức khẩn
    }


def evaluate_case_urgency(
    conn: sqlite3.Connection,
    label: str | None = None,
    symptoms: list[str] | None = None,
    danger: bool = False,
    case_source: str | None = None,
    waited_minutes: int = 0,
) -> dict:
    """Hàm dùng chung đánh giá mức khẩn của một ca (Khẩn / Cần theo dõi / Bình thường).

    Quy tắc:
    - KHẨN: Chỉ số vượt ngưỡng (Above threshold), hoặc có triệu chứng báo động (ALARM_SYMPTOMS),
            hoặc câu hỏi chatbot có cờ nguy cơ (danger).
    - CẦN THEO DÕI: Có triệu chứng không báo động, hoặc ca đã chờ lâu.
    - BÌNH THƯỜNG: Các ca còn lại.
    """
    symptoms = symptoms or []
    has_alarm = bool(ALARM_SYMPTOMS.intersection(set(symptoms)))
    is_above = (label == thresholds.ABOVE)
    is_chatbot_danger = (case_source == "Chatbot" and danger)

    if is_above or has_alarm or is_chatbot_danger:
        level = URGENCY_CRITICAL
    elif symptoms and set(symptoms) != {"No symptoms"}:
        level = URGENCY_WARNING
    else:
        level = URGENCY_NORMAL

    cfg = dict(URGENCY_CONFIG[level])
    overdue_limit = cfg["overdue_minutes"]
    is_overdue = waited_minutes >= overdue_limit
    cfg["is_overdue"] = is_overdue
    return cfg


def gestational_stage_text(edd: str | None, today: date) -> str:
    """Tính tuần thai hoặc ngày sau sinh theo ngày dự sinh edd."""
    if not edd:
        return "—"
    try:
        edd_date = date.fromisoformat(edd)
    except ValueError:
        return "—"
    week = gestational_week(edd_date, today)
    if week > 42:
        days_after = (today - edd_date).days
        return f"Sau sinh {max(1, days_after)} ngày"
    if week < 1:
        return "Tuần 1"
    return f"Tuần {week}"
