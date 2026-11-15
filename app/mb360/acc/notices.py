"""S-009 notification list: ACC FR-025, FR-026; S-009 SR-001 targets (specs/009-acc-profile, research R3, R6)."""
import re
import sqlite3
from datetime import datetime

from .. import tci_feed
from ..alr import thresholds

TYPES = ("Report", "Visit result", "Appointment", "Instruction reminder")
UNREAD = "Unread"


def list_for(conn: sqlite3.Connection, user_id: str, type_: str | None = None, *, unread_only: bool = False) -> list[sqlite3.Row]:
    sql = "SELECT * FROM NOTIFICATION WHERE user_id = ?"
    args: list = [user_id]
    if type_ in TYPES:
        sql += " AND type = ?"
        args.append(type_)
    if unread_only or type_ == UNREAD:
        sql += " AND read_at IS NULL"
    return conn.execute(sql + " ORDER BY created_at DESC, rowid DESC", args).fetchall()


def unread_count(conn: sqlite3.Connection, user_id: str) -> int:
    """Counts every type, whatever the filter (ACC §10 Q16 open)."""
    return conn.execute("SELECT COUNT(*) FROM NOTIFICATION WHERE user_id = ? AND read_at IS NULL", (user_id,)).fetchone()[0]


def _target(conn: sqlite3.Connection, n: sqlite3.Row, now: datetime) -> str:
    base = f"/m/{n['user_id']}"
    if n["type"] == "Visit result":
        return f"{base}/health"          # "New visit results" opens S-023 (Ánh §2, S-008 Q3)
    if n["type"] == "Instruction reminder":
        return f"{base}/instructions"
    if n["type"] == "Appointment":
        path = f"{base}/appointments"
        current, history = tci_feed.appointments(conn, n["user_id"], now)
        for tab, rows in (("current", current), ("history", history)):
            for row in rows:
                if row["appointment_id"] == n["appointment_ref"]:
                    return f"{path}?tab={tab}#appointment-{row['appointment_id']}"
        return path
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
    return _target(conn, n, now)


def mark_all_read(conn: sqlite3.Connection, user_id: str, now: datetime) -> None:
    conn.execute("UPDATE NOTIFICATION SET read_at = ? WHERE user_id = ? AND read_at IS NULL", (now.strftime("%Y-%m-%d %H:%M"), user_id))
    conn.commit()


def parse_response(text: str | None) -> dict:
    """The doctor's free text as Màn 10 shows it: lines starting with "-", "*", "•" or "+" are to-dos, a "Hẹn khám:" line
    (any case, spaces around ":" allowed) is the follow-up, the rest is the comment (U9; Tâm's review)."""
    comment, todo, follow_up = [], [], None
    for line in (text or "").splitlines():
        line = line.strip()
        bullet = re.match(r"^[-*•+–]\s*(.+)$", line)
        visit = re.match(r"^hẹn\s+khám\s*:\s*(.*)$", line, re.IGNORECASE)
        if visit:
            follow_up = visit.group(1).strip() or None
        elif bullet:
            todo.append(bullet.group(1).strip())
        elif line:
            comment.append(line)
    return {"comment": " ".join(comment), "todo": todo, "follow_up": follow_up}


def latest_response(conn: sqlite3.Connection, case_id: str | None) -> sqlite3.Row | None:
    if not case_id:
        return None
    return conn.execute("""SELECT r.custom_text, r.responder_role, r.sent_at, s.full_name, t.content AS template_text
                           FROM STAFF_RESPONSE r JOIN STAFF s ON s.staff_id = r.responder_id
                           LEFT JOIN GUIDANCE_TEMPLATE t ON t.template_id = r.template_id
                           WHERE r.case_id = ? ORDER BY r.sent_at DESC, r.rowid DESC LIMIT 1""", (case_id,)).fetchone()


def _response_text(resp: sqlite3.Row | None) -> str:
    return "\n".join(x for x in (resp["template_text"], resp["custom_text"]) if x) if resp else ""


def _about(conn: sqlite3.Connection, case_id: str | None) -> dict:
    """What the mother reported in this case: "above" when the value is over the threshold (never hard-coded, thresholds module)."""
    empty = {"report": None, "record": None, "symptoms": [], "above": False, "status": None, "question": None}
    case = conn.execute("SELECT * FROM CARE_CASE WHERE case_id = ?", (case_id,)).fetchone() if case_id else None
    if case is None:
        return empty
    out = {**empty, "status": case["status"]}
    if case["chat_message_id"]:
        out["question"] = conn.execute("SELECT text, sent_at FROM CHAT_MESSAGE WHERE message_id = ?", (case["chat_message_id"],)).fetchone()
        return out
    rep = conn.execute("SELECT * FROM METRIC_REPORT WHERE report_id = ?", (case["metric_report_id"],)).fetchone()
    out["report"] = rep
    out["symptoms"] = [r[0] for r in conn.execute("SELECT symptom FROM REPORT_SYMPTOM WHERE report_id = ? ORDER BY symptom", (rep["report_id"],))]
    if rep["health_metric_record_id"]:
        h = conn.execute("SELECT * FROM HEALTH_METRIC_RECORD WHERE record_id = ?", (rep["health_metric_record_id"],)).fetchone()
        out["record"] = h
        out["above"] = thresholds.evaluate(conn, h["metric"], h["value"], h["glucose_context"]) == thresholds.ABOVE
    return out


def card(conn: sqlite3.Connection, n: sqlite3.Row) -> dict:
    """One card of Màn 9: tag, title, preview of the answer, who sent it."""
    about = _about(conn, n["case_id"])
    resp = latest_response(conn, n["case_id"])
    parsed = parse_response(_response_text(resp))
    if n["type"] != "Report":
        tag = (n["type"], "ok" if n["type"] == "Visit result" else "un")
    elif about["status"] == "Resolved":
        tag = ("Resolved", "un")
    elif about["above"]:
        tag = ("Above threshold", "al")
    else:
        tag = (about["status"] or "Report", "inf")
    return {"n": n, "tag": tag, "preview": parsed["comment"] or n["subtitle"], "translate_preview": not parsed["comment"],
            "doctor": resp["full_name"] if resp else None, "role": resp["responder_role"] if resp else None}


def cards_for(conn: sqlite3.Connection, user_id: str, type_: str | None = None, *, unread_only: bool = False) -> list[dict]:
    return [card(conn, n) for n in list_for(conn, user_id, type_, unread_only=unread_only)]


def detail(conn: sqlite3.Connection, user_id: str, notification_id: str) -> dict | None:
    """Màn 10, only for a notification with an answer from clinical staff; the others open their own target."""
    n = conn.execute("SELECT * FROM NOTIFICATION WHERE notification_id = ? AND user_id = ?", (notification_id, user_id)).fetchone()
    resp = latest_response(conn, n["case_id"]) if n else None
    if resp is None:
        return None
    return {"n": n, "resp": resp, "about": _about(conn, n["case_id"]), "card": card(conn, n), **parse_response(_response_text(resp))}


def home_notice(conn: sqlite3.Connection, user_id: str) -> tuple | None:
    """The card on Home (Màn 4): the newest unread answer from clinical staff and how many cases were answered; otherwise the newest unread notice."""
    unread = list_for(conn, user_id, UNREAD)
    answers = [n for n in unread if latest_response(conn, n["case_id"]) is not None]
    if answers:
        return answers[0], len({n["case_id"] for n in answers})     # one case sends several status notices
    return (unread[0], 0) if unread else None
