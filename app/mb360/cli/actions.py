"""CLI case handling: responsible doctor (D-68), status machine (BR-002, D-43) and permissions (BR-004).

Every action checks the role and the current status, then writes CARE_CASE + CASE_STATUS_HISTORY
(or STAFF_RESPONSE) in one transaction; a refused action writes nothing (research R2)."""
import sqlite3
import uuid
from datetime import date, datetime

from ..alr import notifications

DB_TIME = "%Y-%m-%d %H:%M"
NOT_VIEWED, VIEWED, ESCALATED, RESOLVED = "Not viewed", "Viewed", "Escalated to doctor", "Resolved"


class ActionError(Exception):
    """status: 403 role not allowed, 404 unknown, 409 status does not allow it, 422 invalid input."""

    def __init__(self, status: int, message: str):
        super().__init__(message)
        self.status, self.message = status, message


def responsible_doctor(conn: sqlite3.Connection, user_id: str, today: date) -> str | None:
    """Active PATIENT_ASSIGNMENT: valid_from <= today <= valid_to (inclusive, spec-CLI §10 Q15), or no valid_to."""
    row = conn.execute(
        """SELECT doctor_id FROM PATIENT_ASSIGNMENT
           WHERE user_id = ? AND valid_from <= ? AND (valid_to IS NULL OR valid_to >= ?)""",
        (user_id, today.isoformat(), today.isoformat()),
    ).fetchone()
    return row[0] if row else None


def staff_role(conn: sqlite3.Connection, staff_id: str) -> str:
    row = conn.execute("SELECT role FROM STAFF WHERE staff_id = ?", (staff_id,)).fetchone()
    if row is None:
        raise ActionError(404, "Unknown staff member")
    return row[0]


def _case(conn, case_id: str) -> sqlite3.Row:
    row = conn.execute("SELECT * FROM CARE_CASE WHERE case_id = ?", (case_id,)).fetchone()
    if row is None:
        raise ActionError(404, "Unknown case")
    return row


def allowed(conn: sqlite3.Connection, case_id: str, staff_id: str) -> set[str]:
    """Permission table of spec-CLI §5.2 (BR-001, BR-004; CLI-02)."""
    role, status = staff_role(conn, staff_id), _case(conn, case_id)["status"]
    if role == "Nurse":
        return {NOT_VIEWED: {"view", "escalate", "guidance", "close"},
                VIEWED: {"escalate", "guidance", "close"},
                ESCALATED: {"guidance"}}.get(status, set())
    return {"guidance", "close"} if status == ESCALATED else set()


def _check(conn, case_id: str, staff_id: str, action: str, nurse_only: bool = False) -> tuple[str, sqlite3.Row]:
    role, case = staff_role(conn, staff_id), _case(conn, case_id)
    if nurse_only and role != "Nurse":
        raise ActionError(403, "Only a nurse can do this")
    if action not in allowed(conn, case_id, staff_id):
        if role == "Doctor":
            raise ActionError(403, "A doctor acts only on cases escalated to a doctor")
        raise ActionError(409, f"Not possible while the case is {case['status']}")
    return role, case


def _history(conn, case_id: str, status: str, staff_id: str, role: str, at: str) -> None:
    conn.execute("INSERT INTO CASE_STATUS_HISTORY (case_id, status, changed_at, changed_by, role) VALUES (?, ?, ?, ?, ?)",
                 (case_id, status, at, staff_id, role))


def _run(conn, write):
    try:
        result = write()
        conn.commit()
        return result
    except Exception:
        conn.rollback()
        raise


def mark_viewed(conn: sqlite3.Connection, case_id: str, staff_id: str, now: datetime) -> None:
    role, _ = _check(conn, case_id, staff_id, "view", nurse_only=True)
    at = now.strftime(DB_TIME)

    def write():
        conn.execute("UPDATE CARE_CASE SET status = ? WHERE case_id = ?", (VIEWED, case_id))
        _history(conn, case_id, VIEWED, staff_id, role, at)
        notifications.notify(conn, case_id, VIEWED, now)   # ALR FR-018
    _run(conn, write)


def escalate(conn: sqlite3.Connection, case_id: str, staff_id: str, now: datetime) -> str:
    role, case = _check(conn, case_id, staff_id, "escalate", nurse_only=True)
    doctor = responsible_doctor(conn, case["user_id"], now.date())
    if doctor is None:
        raise ActionError(409, "The mother has no active responsible doctor (spec-CLI §10 Q10)")
    at = now.strftime(DB_TIME)

    def write():
        if case["status"] == NOT_VIEWED:      # D-43: record the skipped step, same person and time
            _history(conn, case_id, VIEWED, staff_id, role, at)
        conn.execute("UPDATE CARE_CASE SET status = ?, assigned_doctor_id = ? WHERE case_id = ?", (ESCALATED, doctor, case_id))
        _history(conn, case_id, ESCALATED, staff_id, role, at)
        notifications.notify(conn, case_id, ESCALATED, now)   # one notification per action (§10 Q23)
        return doctor
    return _run(conn, write)


def close_case(conn: sqlite3.Connection, case_id: str, staff_id: str, now: datetime) -> None:
    role, case = _check(conn, case_id, staff_id, "close")
    at = now.strftime(DB_TIME)

    def write():
        if case["status"] == NOT_VIEWED:
            _history(conn, case_id, VIEWED, staff_id, role, at)
        conn.execute("UPDATE CARE_CASE SET status = ?, closed_at = ?, closed_by = ? WHERE case_id = ?",
                     (RESOLVED, at, staff_id, case_id))
        _history(conn, case_id, RESOLVED, staff_id, role, at)
        notifications.notify(conn, case_id, RESOLVED, now)
    _run(conn, write)


def send_guidance(conn: sqlite3.Connection, case_id: str, staff_id: str, now: datetime,
                  template_id: str | None = None, custom_text: str | None = None) -> str:
    role, _ = _check(conn, case_id, staff_id, "guidance")
    template_id = template_id or None
    custom_text = (custom_text or "").strip() or None
    if not template_id and not custom_text:
        raise ActionError(422, "Choose a guidance template or write the text")
    if custom_text and len(custom_text) > 1000:
        raise ActionError(422, "At most 1000 characters (D-46)")
    if template_id and conn.execute("SELECT 1 FROM GUIDANCE_TEMPLATE WHERE template_id = ?", (template_id,)).fetchone() is None:
        raise ActionError(422, "Unknown guidance template")
    response_id = str(uuid.uuid4())

    def write():   # BR-008: the status does not change
        conn.execute("""INSERT INTO STAFF_RESPONSE (response_id, case_id, responder_id, responder_role, template_id, custom_text, sent_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?)""",
                     (response_id, case_id, staff_id, role, template_id, custom_text, now.strftime(DB_TIME)))
        notifications.notify(conn, case_id, "response", now, staff_id=staff_id)
        return response_id
    return _run(conn, write)
