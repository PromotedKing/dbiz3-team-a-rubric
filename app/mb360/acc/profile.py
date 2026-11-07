"""S-103, S-011, S-010: ACC US-3, FR-017, FR-020, FR-022 – FR-024, BR-002, BR-003 (specs/009-acc-profile, research R1, R2, R5)."""
import sqlite3
from datetime import date, datetime

from ..alr.reports import gestational_week
from ..alr.validation import GROUP2
from ..tml.weeks import day_of_week
from .. import numbers
from . import setup

DEFAULTS = {"report_response": 1, "new_visit_result": 1, "appointment_reminder": 1, "watch_flag_reminder": 0}  # ACC Q22 (a)
SWITCHES = ("new_visit_result", "appointment_reminder", "watch_flag_reminder")     # S-010: "Report responses" locked on (Q13)


class ProfileError(Exception):
    def __init__(self, errors: dict):
        super().__init__("invalid profile")
        self.errors = errors


def mask_phone(phone: str | None) -> str:
    return f"{phone[:4]} ••• {phone[-3:]}" if phone else ""


def latest_link(conn: sqlite3.Connection, user_id: str) -> sqlite3.Row | None:
    return conn.execute("SELECT * FROM EMR_LINKAGE_REQUEST WHERE user_id = ? ORDER BY requested_at DESC LIMIT 1", (user_id,)).fetchone()


def is_linked(conn: sqlite3.Connection, user_id: str) -> bool:
    link = latest_link(conn, user_id)
    return link is not None and link["status"] == "Linked"


def preferences(conn: sqlite3.Connection, user_id: str) -> dict:
    row = conn.execute("""SELECT report_response, new_visit_result, appointment_reminder, watch_flag_reminder
                          FROM NOTIFICATION_PREFERENCE WHERE user_id = ?""", (user_id,)).fetchone()
    return dict(row) if row else dict(DEFAULTS)


def load(conn: sqlite3.Connection, user_id: str, now: datetime) -> dict:
    user = conn.execute("SELECT * FROM USER_ACCOUNT WHERE user_id = ?", (user_id,)).fetchone()
    p = conn.execute("SELECT * FROM PREGNANCY_PROFILE WHERE user_id = ?", (user_id,)).fetchone()
    consent = conn.execute("SELECT accepted FROM CONSENT_RECORD WHERE user_id = ? ORDER BY accepted_at DESC LIMIT 1", (user_id,)).fetchone()
    flags = conn.execute("SELECT metric FROM WATCH_FLAG WHERE user_id = ? AND active = 1 ORDER BY metric", (user_id,)).fetchall()
    edd = date.fromisoformat(p["edd"]) if p else None
    prefs = preferences(conn, user_id)
    return {"phone": mask_phone(user["phone"]), "edd": p["edd"] if p else None, "lmp": p["lmp"] if p else None,
            "edd_source": p["edd_source"] if p else None, "height_cm": p["height_cm"] if p else None,
            "first_visit_date": p["first_visit_date"] if p else None,
            "week": gestational_week(edd, now.date()) if p else None, "week_day": day_of_week(edd, now.date()) if p else None,
            "link": latest_link(conn, user_id), "linked": is_linked(conn, user_id), "consent": bool(consent and consent["accepted"]),
            "instructions": [m for m in GROUP2 if m in {f["metric"] for f in flags}], "reminders_on": any(prefs[k] for k in SWITCHES)}


def save(conn: sqlite3.Connection, user_id: str, form: dict, now: datetime) -> None:
    """S-011 "Save changes": FR-020 validates, FR-022 stores. The due date of a linked mother never changes (BR-003)."""
    errors = {}
    height, error = numbers.read(form.get("height_cm"))
    height = height or ""
    if error:
        errors["height_cm"] = error
    linked = is_linked(conn, user_id)
    current = conn.execute("SELECT edd FROM PREGNANCY_PROFILE WHERE user_id = ?", (user_id,)).fetchone()
    edd = current["edd"]
    if not linked:
        edd = (form.get("edd") or "").strip()
        date_errors = setup.validate({"date_type": "EDD", "date": edd}, now.date())
        if "date" in date_errors:
            errors["edd"] = date_errors["date"]
    if errors:
        raise ProfileError(errors)
    try:
        conn.execute("UPDATE PREGNANCY_PROFILE SET height_cm = ? WHERE user_id = ?", (float(height) if height else None, user_id))
        if edd != current["edd"]:       # the old LMP no longer belongs to the new due date
            conn.execute("UPDATE PREGNANCY_PROFILE SET edd = ?, lmp = NULL WHERE user_id = ?", (edd, user_id))
        conn.commit()
    except Exception:
        conn.rollback()
        raise


def set_switch(conn: sqlite3.Connection, user_id: str, key: str, value: bool, now: datetime) -> None:
    """S-010 SR-002: saved as soon as a switch is toggled. `key` is checked against SWITCHES before it reaches the SQL."""
    if key not in SWITCHES:
        raise ProfileError({"key": "This setting cannot be changed."})
    stamp = now.strftime("%Y-%m-%d %H:%M")
    prefs = preferences(conn, user_id)
    prefs[key] = 1 if value else 0
    try:
        conn.execute("""INSERT INTO NOTIFICATION_PREFERENCE (user_id, report_response, new_visit_result, appointment_reminder, watch_flag_reminder, updated_at)
                        VALUES (:user_id, :report_response, :new_visit_result, :appointment_reminder, :watch_flag_reminder, :updated_at)
                        ON CONFLICT (user_id) DO UPDATE SET new_visit_result = :new_visit_result, appointment_reminder = :appointment_reminder,
                            watch_flag_reminder = :watch_flag_reminder, updated_at = :updated_at""",
                     {**prefs, "user_id": user_id, "updated_at": stamp})
        conn.commit()
    except Exception:
        conn.rollback()
        raise
