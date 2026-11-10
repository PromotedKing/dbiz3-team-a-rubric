"""ACC FR-004, FR-005, D-72: pregnancy setup (S-007 / S-046) — research R5.

EDD from LMP = LMP + 280 days is the team proposal (Naegele), provisional until the SME answers
spec-ACC §10 Q10. No valid range is checked for height / weight (§10 Q11)."""
import sqlite3
import uuid
from datetime import date, datetime, timedelta

from .. import numbers

PREGNANCY_DAYS = 280


class SetupError(Exception):
    def __init__(self, errors: dict):
        super().__init__("invalid pregnancy setup")
        self.errors = errors


def calculate(date_type: str, value: date, today: date) -> dict:
    edd = value + timedelta(days=PREGNANCY_DAYS) if date_type == "LMP" else value
    days = PREGNANCY_DAYS - (edd - today).days
    return {"edd": edd, "week": days // 7, "day": days % 7}


def _date(text: str | None) -> date | None:
    try:
        return date.fromisoformat(text) if text else None
    except ValueError:
        return None


def _number(text: str | None) -> bool:
    try:
        float(text)
        return True
    except (TypeError, ValueError):
        return False


def validate(form: dict, today: date) -> dict:
    errors = {}
    date_type = form.get("date_type")
    if date_type not in ("EDD", "LMP"):
        errors["date_type"] = "Choose: I know my due date, or I know the first day of my last period."
    value = _date(form.get("date"))
    calc = None
    if value is None:
        errors["date"] = "Enter the date."
    elif date_type in ("EDD", "LMP"):
        calc = calculate(date_type, value, today)
        if calc["edd"] < today or not 0 <= calc["week"] <= 42:
            errors["date"] = ("The first day of the last period cannot be in the future, and the week must be 0 – 42." if date_type == "LMP"
                              else "Value outside the valid range: the due date cannot be in the past and the week must be 0 – 42.")
    for field in ("height_cm", "weight_kg"):
        _, error = numbers.read(form.get(field))
        if error:
            errors[field] = error
    first = (form.get("first_visit_date") or "").strip()
    if first:
        fv = _date(first)
        if fv is None or fv > today or (calc and fv < calc["edd"] - timedelta(days=PREGNANCY_DAYS)):
            errors["first_visit_date"] = "The first check-up date must be within this pregnancy and not in the future."
    return errors


def save(conn: sqlite3.Connection, user_id: str, form: dict, now: datetime) -> None:
    today = now.date()
    errors = validate(form, today)
    if errors:
        raise SetupError(errors)
    calc = calculate(form["date_type"], date.fromisoformat(form["date"]), today)
    height = numbers.read(form.get("height_cm"))[0] or ""
    weight = numbers.read(form.get("weight_kg"))[0] or ""
    stamp = now.strftime("%Y-%m-%d %H:%M")
    try:
        conn.execute("""INSERT INTO PREGNANCY_PROFILE (user_id, edd, lmp, edd_source, height_cm, first_visit_date)
                        VALUES (?, ?, ?, 'Self-entered', ?, ?)""",
                     (user_id, calc["edd"].isoformat(), form["date"] if form["date_type"] == "LMP" else None,
                      float(height) if height else None, (form.get("first_visit_date") or "").strip() or None))
        if weight:   # FR-005, D-42: the weight is the first Health Metric Record (Self-entered)
            conn.execute("""INSERT INTO HEALTH_METRIC_RECORD (record_id, user_id, metric, metric_group, value, unit, glucose_context,
                                measured_at, source, visit_id, gestational_week, created_at)
                            VALUES (?, ?, 'Weight', 'Group 1', ?, 'kg', NULL, ?, 'Self-entered', NULL, ?, ?)""",
                         (str(uuid.uuid4()), user_id, weight, stamp, calc["week"], stamp))
        conn.commit()
    except Exception:
        conn.rollback()
        raise
