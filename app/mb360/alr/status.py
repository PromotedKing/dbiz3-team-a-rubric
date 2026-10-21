"""S-026 "Report status": ALR FR-005, FR-007, BR-011, BR-012 (research R3, R4)."""
import sqlite3
from datetime import datetime

STEPS = ("Not viewed", "Viewed", "Escalated to doctor", "Resolved")


def _show(t: str) -> str:
    return datetime.strptime(t, "%Y-%m-%d %H:%M").strftime("%d/%m/%Y · %H:%M")


def _actor(role: str | None, name: str | None) -> str | None:
    if not name:
        return None
    return f"Dr. {name}" if role == "Doctor" else f"{role} {name}"


def progress(conn: sqlite3.Connection, case_id: str) -> list[dict]:
    hist = {r["status"]: r for r in conn.execute(
        """SELECT h.status, h.changed_at, h.role, s.full_name FROM CASE_STATUS_HISTORY h
           LEFT JOIN STAFF s ON s.staff_id = h.changed_by WHERE h.case_id = ?""", (case_id,))}
    steps = []
    for st in STEPS:
        h = hist.get(st)
        if h:
            steps.append({"status": st, "state": "done", "at": _show(h["changed_at"]),
                          "actor": _actor(h["role"], h["full_name"]),
                          "note": "Report submitted" if st == "Not viewed" else None})
        elif st == "Escalated to doctor" and "Resolved" in hist:
            steps.append({"status": st, "state": "skipped", "at": None, "actor": None, "note": "No doctor escalation needed"})
        else:
            steps.append({"status": st, "state": "pending", "at": None, "actor": None, "note": None})
    return steps


def responses(conn: sqlite3.Connection, case_id: str) -> list[dict]:
    out = []
    for r in conn.execute(
        """SELECT r.sent_at, r.responder_role, s.full_name, r.custom_text, t.content AS template_text
           FROM STAFF_RESPONSE r JOIN STAFF s ON s.staff_id = r.responder_id
           LEFT JOIN GUIDANCE_TEMPLATE t ON t.template_id = r.template_id
           WHERE r.case_id = ? ORDER BY r.sent_at""", (case_id,)):
        text = " ".join(x for x in (r["template_text"], r["custom_text"]) if x)
        out.append({"heading": f"Response from {_actor(r['responder_role'], r['full_name'])}", "text": text, "at": _show(r["sent_at"])})
    return out


def show_safety_note(conn: sqlite3.Connection, case_id: str) -> bool:
    """BR-011: shown only while the case has no response."""
    return conn.execute("SELECT COUNT(*) FROM STAFF_RESPONSE WHERE case_id = ?", (case_id,)).fetchone()[0] == 0
