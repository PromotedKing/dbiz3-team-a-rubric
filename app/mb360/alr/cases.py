"""ALR FR-021: create a case "Not viewed" and its first status-history row (written by the System)."""
import sqlite3
import uuid
from datetime import datetime

from . import notifications
from .reports import DB_TIME


def open_case(conn: sqlite3.Connection, user_id: str, report_id: str, case_source: str, now: datetime) -> str:
    case_id = str(uuid.uuid4())
    at = now.strftime(DB_TIME)
    conn.execute(
        """INSERT INTO CARE_CASE (case_id, user_id, case_source, status, metric_report_id, chat_message_id,
               assigned_doctor_id, created_at, closed_at, closed_by)
           VALUES (?, ?, ?, 'Not viewed', ?, NULL, NULL, ?, NULL, NULL)""",
        (case_id, user_id, case_source, report_id, at),
    )
    conn.execute(
        "INSERT INTO CASE_STATUS_HISTORY (case_id, status, changed_at, changed_by, role) VALUES (?, 'Not viewed', ?, NULL, 'System')",
        (case_id, at),
    )
    notifications.notify(conn, case_id, "created", now)   # FR-018
    return case_id


def open_chatbot_case(conn: sqlite3.Connection, user_id: str, chat_message_id: str, now: datetime) -> str:
    """ALR FR-021 (c): the mother tapped "Connect to nurse" (BOT FR-008, D-34). The caller commits."""
    case_id = str(uuid.uuid4())
    at = now.strftime(DB_TIME)
    conn.execute(
        """INSERT INTO CARE_CASE (case_id, user_id, case_source, status, metric_report_id, chat_message_id,
               assigned_doctor_id, created_at, closed_at, closed_by)
           VALUES (?, ?, 'Chatbot', 'Not viewed', NULL, ?, NULL, ?, NULL, NULL)""",
        (case_id, user_id, chat_message_id, at),
    )
    conn.execute(
        "INSERT INTO CASE_STATUS_HISTORY (case_id, status, changed_at, changed_by, role) VALUES (?, 'Not viewed', ?, NULL, 'System')",
        (case_id, at),
    )
    notifications.notify(conn, case_id, "created", now)   # FR-018
    return case_id
