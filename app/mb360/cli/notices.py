"""S-059 "Notifications" inside the clinical web (CLI FR-005, FR-019, FR-020; ALR FR-009; D-109).

Nothing is stored (DM-32): NOTIFICATION holds the mother's notifications only and has no `staff_id`, so
there is no read / unread state, and no push or SMS (ALR-03). Every line is read from CARE_CASE and
CASE_STATUS_HISTORY as they stand, exactly like the doctor's badge.

Nurse: the cases waiting for a first look ("Not viewed" — the badge of S-061 #4, D-109), the ones that are
above threshold (THRESHOLD_RULE, never a number written here) or carry an alarm symptom (PRD M3 list,
D-73) on top. Doctor: the cases a nurse escalated to him (ALR FR-009; responsible doctor = active
PATIENT_ASSIGNMENT, D-68), the one escalated longest ago and still without his answer on top.
"""
import sqlite3
from datetime import datetime

from ..alr import thresholds
from . import dashboard, queue

NOT_VIEWED, ESCALATED = "Not viewed", "Escalated to doctor"


def count(conn: sqlite3.Connection, staff_id: str, role: str) -> int:
    """The number on the bell (S-061 #4): cases waiting for a first look, or escalated to this doctor."""
    if role == "Nurse":
        return conn.execute("SELECT COUNT(*) FROM CARE_CASE WHERE status = ?", (NOT_VIEWED,)).fetchone()[0]
    return queue.doctor_badge(conn, staff_id)


def escalation(conn: sqlite3.Connection, case_id: str) -> dict | None:
    """Who moved the case to the doctor and when (CASE_STATUS_HISTORY, one row per status)."""
    row = conn.execute(
        """SELECT h.changed_at, h.role, s.full_name FROM CASE_STATUS_HISTORY h
           LEFT JOIN STAFF s ON s.staff_id = h.changed_by
           WHERE h.case_id = ? AND h.status = ?""",
        (case_id, ESCALATED),
    ).fetchone()
    return {"at": row["changed_at"], "role": row["role"], "by": row["full_name"]} if row else None


def lines(conn: sqlite3.Connection, staff_id: str, role: str, now: datetime) -> list[dict]:
    """The notification list of this staff member, the case to act on first at the top."""
    if role == "Nurse":
        rows = [c for c in dashboard.cases(conn, now) if c["status"] == NOT_VIEWED]
        for c in rows:
            c["urgent"] = c["label"] == thresholds.ABOVE or c["alarm"]
            c["escalation"] = None
        rows.sort(key=lambda c: (not c["urgent"], c["created_at"]))
        return rows
    # his own escalated cases, plus the fail-safe ones with no single assignee (BR-011 step 4, BR-010)
    rows = [c for c in dashboard.cases(conn, now, viewer=staff_id)
            if c["status"] == ESCALATED and c["assigned_doctor_id"] in (staff_id, None)]
    for c in rows:
        c["urgent"] = c["label"] == thresholds.ABOVE or c["alarm"]
        c["escalation"] = escalation(conn, c["case_id"])
    rows.sort(key=lambda c: (c["doctor_answered"], (c["escalation"] or {}).get("at") or c["created_at"]))
    return rows
