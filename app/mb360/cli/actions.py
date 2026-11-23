"""CLI case handling: responsible doctor (D-68), status machine (BR-002, D-43) and permissions (BR-004).

Every action checks the role and the current status, then writes CARE_CASE + CASE_STATUS_HISTORY
(or STAFF_RESPONSE) in one transaction; a refused action writes nothing (research R2)."""
import sqlite3
import uuid
from datetime import date, datetime

from ..alr import notifications, thresholds
from .urgency import (
    STATUS_ESCALATED,
    STATUS_NOT_VIEWED,
    STATUS_RESOLVED,
    STATUS_VIEWED,
)

DB_TIME = "%Y-%m-%d %H:%M"
NOT_VIEWED, VIEWED, ESCALATED, RESOLVED = (
    STATUS_NOT_VIEWED,
    STATUS_VIEWED,
    STATUS_ESCALATED,
    STATUS_RESOLVED,
)


class ActionError(Exception):
    """status: 403 role not allowed, 404 unknown, 409 status does not allow it, 422 invalid input."""

    def __init__(self, status: int, message: str):
        super().__init__(message)
        self.status, self.message = status, message


def responsible_doctor(conn: sqlite3.Connection, user_id: str, today: date) -> str | None:
    """Active PATIENT_ASSIGNMENT: valid_from <= today <= valid_to (inclusive, spec-CLI §10 Q26 — was Q15 until the duplicate was split), or no valid_to."""
    row = conn.execute(
        """SELECT doctor_id FROM PATIENT_ASSIGNMENT
           WHERE user_id = ? AND valid_from <= ? AND (valid_to IS NULL OR valid_to >= ?)""",
        (user_id, today.isoformat(), today.isoformat()),
    ).fetchone()
    return row[0] if row else None


def visible_users(conn: sqlite3.Connection, staff_id: str, today: date) -> set[str] | None:
    """BR-010 (D-96, proposed): whose mothers this staff member may see. None = every mother.

    A nurse sees all. A doctor sees the mothers he is the active responsible doctor for; while he is on
    duty he also sees the mothers of a responsible doctor marked Away. A case with no assigned doctor is
    visible to every doctor (BR-011 step 4) — that is a case rule, applied where the cases are read.
    """
    if staff_role(conn, staff_id) == "Nurse":
        return None
    day = today.isoformat()
    rows = conn.execute(
        """SELECT p.user_id FROM PATIENT_ASSIGNMENT p
           JOIN STAFF d ON d.staff_id = p.doctor_id
           WHERE p.valid_from <= ? AND (p.valid_to IS NULL OR p.valid_to >= ?)
             AND (p.doctor_id = ?
                  OR (d.availability = 'Away'
                      AND (SELECT on_duty FROM STAFF WHERE staff_id = ?) = 1
                      AND (SELECT availability FROM STAFF WHERE staff_id = ?) = 'Available'))""",
        (day, day, staff_id, staff_id, staff_id),
    )
    return {r[0] for r in rows}


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


def must_escalate(conn: sqlite3.Connection, case_id: str) -> str | None:
    """BR-012 (D-98, proposed): a case a nurse may not close, and why — None when she may.

    "Above threshold" comes from THRESHOLD_RULE, never from a number written here. The chatbot's danger
    flag is CHAT_MESSAGE.`is_risk`, read through CARE_CASE.`chat_message_id` — the option §10 Q24 names
    for the case where the flag is kept only on the message; no new column.
    """
    case = _case(conn, case_id)
    if case["case_source"] == "Chatbot":
        row = conn.execute("SELECT is_risk FROM CHAT_MESSAGE WHERE message_id = ?", (case["chat_message_id"],)).fetchone()
        return "danger" if row is not None and row[0] else None
    row = conn.execute(
        """SELECT h.metric, h.value, h.glucose_context FROM METRIC_REPORT r
           JOIN HEALTH_METRIC_RECORD h ON h.record_id = r.health_metric_record_id
           WHERE r.report_id = ?""",
        (case["metric_report_id"],),
    ).fetchone()
    if row is None:                 # symptom report: no measured value, so no threshold label (BR-005)
        return None
    return "above" if thresholds.evaluate(conn, row["metric"], row["value"], row["glucose_context"]) == thresholds.ABOVE else None


def _by_status(role: str, status: str) -> set[str]:
    """What the status alone allows — permission table of spec-CLI §5.2 (BR-001, BR-004; CLI-02)."""
    if role == "Nurse":
        return {NOT_VIEWED: {"view", "escalate", "guidance", "close"},
                VIEWED: {"escalate", "guidance", "close"},
                ESCALATED: {"guidance"}}.get(status, set())
    return {"guidance", "close"} if status == ESCALATED else set()


def allowed(conn: sqlite3.Connection, case_id: str, staff_id: str) -> set[str]:
    """What this staff member may do with this case now (spec-CLI §5.2; BR-012 narrows the nurse)."""
    role = staff_role(conn, staff_id)
    can = _by_status(role, _case(conn, case_id)["status"])
    if role == "Nurse" and "close" in can and must_escalate(conn, case_id):   # BR-012: escalating is the only way on
        can = can - {"close"}
    return can


def _check(conn, case_id: str, staff_id: str, action: str, nurse_only: bool = False) -> tuple[str, sqlite3.Row]:
    role, case = staff_role(conn, staff_id), _case(conn, case_id)
    if nurse_only and role != "Nurse":
        raise ActionError(403, "Only a nurse can do this")
    if action not in allowed(conn, case_id, staff_id):
        if role == "Doctor":
            raise ActionError(403, "A doctor acts only on cases escalated to a doctor")
        if action == "close" and action in _by_status(role, case["status"]) and (why := must_escalate(conn, case_id)):
            raise ActionError(403, "This case is above threshold: only a doctor can close it" if why == "above"      # BR-012
                              else "The chatbot marked this question as a danger sign: only a doctor can close it")  # D-98
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


def on_duty_doctor(conn: sqlite3.Connection) -> str | None:
    """A doctor who is on duty and present (BR-011 step 2). Seed data in the MVP (§10 Q22)."""
    row = conn.execute(
        "SELECT staff_id FROM STAFF WHERE role = 'Doctor' AND on_duty = 1 AND availability = 'Available' ORDER BY full_name"
    ).fetchone()
    return row[0] if row else None


def route_to(conn: sqlite3.Connection, user_id: str, today: date) -> dict:
    """BR-011 (D-97, proposed): who receives an escalated case, and what the nurse is told.

    `outcome` is one of "responsible", "on_duty", "unknown", "none"; `doctor` is the receiving doctor,
    None in the fail-safe case (step 4), where the case is visible to every doctor instead (BR-010).
    The nurse never chooses — she only sees the result before she confirms (FR-026).
    """
    responsible = responsible_doctor(conn, user_id, today)
    out = {"doctor": None, "outcome": "none", "responsible": responsible,
           "responsible_name": None, "availability": None}
    if responsible is None:                                   # step 4: no active Patient Assignment
        return out
    row = conn.execute("SELECT full_name, availability FROM STAFF WHERE staff_id = ?", (responsible,)).fetchone()
    out["responsible_name"], out["availability"] = row["full_name"], row["availability"]
    if row["availability"] == "Available":                    # step 1
        return out | {"doctor": responsible, "outcome": "responsible"}
    if row["availability"] is None:                           # step 3: availability cannot be determined
        return out | {"doctor": responsible, "outcome": "unknown"}
    cover = on_duty_doctor(conn)                              # step 2: he is Away
    if cover is not None:
        return out | {"doctor": cover, "outcome": "on_duty"}
    return out                                                # step 4: Away and nobody on duty


def escalate(conn: sqlite3.Connection, case_id: str, staff_id: str, now: datetime,
             reason: str | None = None, note: str | None = None) -> str | None:
    """Returns the receiving doctor, or None in the fail-safe case of BR-011 (visible to every doctor)."""
    role, case = _check(conn, case_id, staff_id, "escalate", nurse_only=True)
    doctor = route_to(conn, case["user_id"], now.date())["doctor"]
    at = now.strftime(DB_TIME)

    def write():
        if case["status"] == NOT_VIEWED:      # D-43: record the skipped step, same person and time
            _history(conn, case_id, VIEWED, staff_id, role, at)
        conn.execute("UPDATE CARE_CASE SET status = ?, assigned_doctor_id = ? WHERE case_id = ?", (ESCALATED, doctor, case_id))
        _history(conn, case_id, ESCALATED, staff_id, role, at)
        if reason or note:
            txt = f"Lý do chuyển: {reason or 'Không có'}" + (f" · Ghi chú: {note}" if note else "")
            conn.execute(
                """INSERT INTO STAFF_RESPONSE (response_id, case_id, responder_id, responder_role, template_id, custom_text, sent_at)
                   VALUES (?, ?, ?, ?, NULL, ?, ?)""",
                (str(uuid.uuid4()), case_id, staff_id, role, txt, at),
            )
        notifications.notify(conn, case_id, ESCALATED, now)   # one notification per action (§10 Q23)
        return doctor
    return _run(conn, write)


def remind_doctor(conn: sqlite3.Connection, case_id: str, staff_id: str, now: datetime) -> str:
    role = staff_role(conn, staff_id)
    case = _case(conn, case_id)
    if case["status"] != ESCALATED:
        raise ActionError(409, "Can only remind for escalated cases")
    at = now.strftime(DB_TIME)
    response_id = str(uuid.uuid4())

    def write():
        conn.execute(
            """INSERT INTO STAFF_RESPONSE (response_id, case_id, responder_id, responder_role, template_id, custom_text, sent_at)
               VALUES (?, ?, ?, ?, NULL, ?, ?)""",
            (response_id, case_id, staff_id, role, "[Nhắc nhở] Y tá nhắc bác sĩ xử lý ca", at),
        )
        return response_id
    return _run(conn, write)


def reopen_case(conn: sqlite3.Connection, case_id: str, staff_id: str, now: datetime) -> None:
    role = staff_role(conn, staff_id)
    case = _case(conn, case_id)
    if case["status"] != RESOLVED:
        raise ActionError(409, "Only a resolved case can be reopened")
    at = now.strftime(DB_TIME)

    def write():
        conn.execute(
            "UPDATE CARE_CASE SET status = ?, closed_at = NULL, closed_by = NULL WHERE case_id = ?",
            (NOT_VIEWED, case_id),
        )
        conn.execute(
            "UPDATE CASE_STATUS_HISTORY SET changed_at = ?, changed_by = ?, role = ? WHERE case_id = ? AND status = ?",
            (at, staff_id, role, case_id, NOT_VIEWED),
        )
    _run(conn, write)


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
