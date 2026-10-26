"""S-024 self-tracked metrics: HLT FR-007, BR-003 (research R4).

Group 1 values are never threshold-checked and never create a report (BR-003). No valid range is
checked (D-16 pending SME)."""
import sqlite3
import uuid
from datetime import date, datetime, timedelta

from ..alr.reports import gestational_week

FORM_TIME = "%Y-%m-%dT%H:%M"
DB_TIME = "%Y-%m-%d %H:%M"
FIELDS = (("weight", "Weight", "kg"), ("temperature", "Temperature", "°C"), ("heart_rate", "Heart rate", "bpm"))


class EntryError(Exception):
    def __init__(self, errors: dict):
        super().__init__("invalid self-tracked metrics")
        self.errors = errors


def _time(text: str | None) -> datetime | None:
    try:
        return datetime.strptime(text, FORM_TIME) if text else None
    except ValueError:
        return None


def validate(form: dict, now: datetime) -> tuple[dict, list]:
    errors, rows = {}, []
    for key, metric, unit in FIELDS:
        value = (form.get(key) or "").strip()
        if not value:
            continue
        try:
            float(value)
        except ValueError:
            errors[key] = "Value outside the valid range"
            continue
        at = _time(form.get(f"{key}_at"))
        if at is None:
            errors[f"{key}_at"] = "Enter the measured time."
        elif at > now:   # schema: a record cannot be measured after it is created (HLT §6)
            errors[f"{key}_at"] = "The measured time cannot be later than now."
        else:
            rows.append((metric, value, unit, at))
    bed, wake = _time(form.get("bedtime")), _time(form.get("wakeup"))
    if form.get("bedtime") or form.get("wakeup"):
        if bed is None:
            errors["bedtime"] = "Enter the bedtime."
        elif wake is None:
            errors["wakeup"] = "Enter the wake-up time."
        elif not (bed < wake < bed + timedelta(hours=24)):
            errors["wakeup"] = "The wake-up time must be after the bedtime (within 24 hours)."
        elif wake > now:
            errors["wakeup"] = "The wake-up time cannot be later than now."
        else:
            rows.append(("Sleep", f"{bed:%H:%M}-{wake:%H:%M}", None, wake))
    if not errors and not rows:
        errors["form"] = "Enter at least one metric."
    return errors, rows


def save(conn: sqlite3.Connection, user_id: str, form: dict, now: datetime) -> int:
    errors, rows = validate(form, now)
    if errors:
        raise EntryError(errors)
    edd = conn.execute("SELECT edd FROM PREGNANCY_PROFILE WHERE user_id = ?", (user_id,)).fetchone()
    week = gestational_week(date.fromisoformat(edd[0]), now.date()) if edd else None
    if week is None:
        raise EntryError({"form": "Set up the pregnancy first."})
    try:
        for metric, value, unit, at in rows:
            conn.execute("""INSERT INTO HEALTH_METRIC_RECORD (record_id, user_id, metric, metric_group, value, unit, glucose_context,
                                measured_at, source, visit_id, gestational_week, created_at)
                            VALUES (?, ?, ?, 'Group 1', ?, ?, NULL, ?, 'Self-entered', NULL, ?, ?)""",
                         (str(uuid.uuid4()), user_id, metric, value, unit, at.strftime(DB_TIME), week, now.strftime(DB_TIME)))
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    return len(rows)
