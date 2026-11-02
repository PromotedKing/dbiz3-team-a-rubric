"""S-009 notification list: ACC FR-025, FR-026; S-009 SR-001 targets (specs/009-acc-profile, research R3, R6)."""
import sqlite3
from datetime import datetime

TYPES = ("Report", "Visit result", "Appointment", "Instruction reminder")
UNREAD = "Unread"


def list_for(conn: sqlite3.Connection, user_id: str, type_: str | None = None) -> list[sqlite3.Row]:
    sql = "SELECT * FROM NOTIFICATION WHERE user_id = ?"
    args: list = [user_id]
    if type_ in TYPES:
        sql += " AND type = ?"
        args.append(type_)
    elif type_ == UNREAD:
        sql += " AND read_at IS NULL"
    return conn.execute(sql + " ORDER BY created_at DESC, rowid DESC", args).fetchall()


def unread_count(conn: sqlite3.Connection, user_id: str) -> int:
    """Counts every type, whatever the filter (ACC §10 Q16 open)."""
    return conn.execute("SELECT COUNT(*) FROM NOTIFICATION WHERE user_id = ? AND read_at IS NULL", (user_id,)).fetchone()[0]


def _target(conn: sqlite3.Connection, n: sqlite3.Row) -> str:
    base = f"/m/{n['user_id']}"
    if n["type"] == "Visit result":
        return f"{base}/health"
    if n["type"] == "Instruction reminder":
        return f"{base}/instructions"
    if n["type"] == "Appointment":
        return "/tci/booking"
    case = conn.execute("SELECT metric_report_id FROM CARE_CASE WHERE case_id = ?", (n["case_id"],)).fetchone() if n["case_id"] else None
    if case is None:
        return f"{base}/my-reports"
    return f"{base}/reports/{case[0]}" if case[0] else f"{base}/cases/{n['case_id']}"


def open_notice(conn: sqlite3.Connection, user_id: str, notification_id: str, now: datetime) -> str | None:
    """FR-026: read when opened, the first read time is kept. None when it is not this mother's notification."""
    n = conn.execute("SELECT * FROM NOTIFICATION WHERE notification_id = ? AND user_id = ?", (notification_id, user_id)).fetchone()
    if n is None:
        return None
    conn.execute("UPDATE NOTIFICATION SET read_at = ? WHERE notification_id = ? AND read_at IS NULL",
                 (now.strftime("%Y-%m-%d %H:%M"), notification_id))
    conn.commit()
    return _target(conn, n)


def mark_all_read(conn: sqlite3.Connection, user_id: str, now: datetime) -> None:
    conn.execute("UPDATE NOTIFICATION SET read_at = ? WHERE user_id = ? AND read_at IS NULL", (now.strftime("%Y-%m-%d %H:%M"), user_id))
    conn.commit()
