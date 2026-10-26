"""CLI FR-025, BR-001, BR-006: a doctor adds or edits a "Doctor's instructions" entry (Watch-Flag).

One active instruction per (mother, metric) — DM-21 default: saving a metric that already has an
active instruction edits it. A new instruction has no visit (HLT §10 Q19 open). Nothing here removes
or deactivates an instruction (ALR BR-001)."""
import sqlite3
import uuid
from datetime import datetime

from .actions import ActionError, staff_role

GROUP2 = ("Blood pressure", "Blood glucose", "Urine protein")


def save_instruction(conn: sqlite3.Connection, user_id: str, doctor_id: str, now: datetime, metric: str,
                     note: str | None = None, template_id: str | None = None, custom_text: str | None = None) -> str:
    if staff_role(conn, doctor_id) != "Doctor":
        raise ActionError(403, "Only a doctor can add or edit Doctor's instructions")
    if metric not in GROUP2:
        raise ActionError(422, "Choose a group-2 metric")
    note = (note or "").strip() or None
    template_id = template_id or None
    custom_text = (custom_text or "").strip() or None
    if custom_text and len(custom_text) > 1000:
        raise ActionError(422, "At most 1000 characters (D-46)")
    if template_id and conn.execute("SELECT 1 FROM GUIDANCE_TEMPLATE WHERE template_id = ?", (template_id,)).fetchone() is None:
        raise ActionError(422, "Unknown guidance template")
    today = now.date().isoformat()
    existing = conn.execute("SELECT flag_id FROM WATCH_FLAG WHERE user_id = ? AND metric = ? AND active = 1",
                            (user_id, metric)).fetchone()
    try:
        if existing:
            flag_id = existing[0]
            conn.execute("""UPDATE WATCH_FLAG SET note = ?, template_id = ?, custom_text = ?, flagged_by = ?, flagged_at = ?
                            WHERE flag_id = ?""", (note, template_id, custom_text, doctor_id, today, flag_id))
        else:
            flag_id = str(uuid.uuid4())
            conn.execute("""INSERT INTO WATCH_FLAG (flag_id, user_id, visit_id, metric, flagged_by, flagged_at, note,
                                template_id, custom_text, active)
                            VALUES (?, ?, NULL, ?, ?, ?, ?, ?, ?, 1)""",
                         (flag_id, user_id, metric, doctor_id, today, note, template_id, custom_text))
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    return flag_id
