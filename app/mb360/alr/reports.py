"""ALR FR-020 (store a report) and FR-015 (gestational week). research.md R4 – R6."""
import sqlite3
import uuid
from datetime import date, datetime

from .validation import parse_time

DB_TIME = "%Y-%m-%d %H:%M"
UNITS = {"Blood pressure": "mmHg", "Blood glucose": "mmol/L", "Urine protein": None}


def gestational_week(edd: date, today: date) -> int:
    """Completed weeks, week 40 = due date (same 280-day rule as the seed; ACC §10 Q10 pending SME)."""
    return (280 - (edd - today).days) // 7


def next_report_code(conn: sqlite3.Connection, submitted: datetime) -> str:
    """Provisional (ALR §10 Q16): BC-MMDD-NNN like the seed and the wireframe, unique."""
    prefix = submitted.strftime("BC-%m%d-")
    codes = [r[0] for r in conn.execute("SELECT report_code FROM METRIC_REPORT WHERE report_code LIKE ?", (prefix + "%",))]
    seq = max((int(c[len(prefix):]) for c in codes if c[len(prefix):].isdigit()), default=0) + 1
    return f"{prefix}{seq:03d}"


def active_flag(conn: sqlite3.Connection, user_id: str, metric: str) -> str | None:
    row = conn.execute("SELECT flag_id FROM WATCH_FLAG WHERE user_id = ? AND metric = ? AND active = 1",
                       (user_id, metric)).fetchone()
    return row[0] if row else None


def value_of(form: dict) -> str | None:
    metric = form["metric"]
    if metric == "Blood pressure":
        return f"{int(form['systolic'])}/{int(form['diastolic'])}"
    if metric == "Blood glucose":
        return str(form["value"]).strip()
    if metric == "Urine protein":
        return form["level"]
    return None


def store_report(conn: sqlite3.Connection, user_id: str, form: dict, now: datetime) -> dict:
    """Write HEALTH_METRIC_RECORD (metric report only), METRIC_REPORT and REPORT_SYMPTOM.
    The caller owns the transaction (commit together with the case — FR-021)."""
    metric = form["metric"]
    submitted = now.strftime(DB_TIME)
    record_id = None
    if metric != "Symptom":
        edd = conn.execute("SELECT edd FROM PREGNANCY_PROFILE WHERE user_id = ?", (user_id,)).fetchone()
        if edd is None:
            raise ValueError("no pregnancy profile: the gestational week cannot be calculated (ACC BR-006)")
        record_id = str(uuid.uuid4())
        conn.execute(
            """INSERT INTO HEALTH_METRIC_RECORD (record_id, user_id, metric, metric_group, value, unit, glucose_context,
                   measured_at, source, visit_id, gestational_week, created_at)
               VALUES (?, ?, ?, 'Group 2', ?, ?, ?, ?, 'Doctor-assigned', NULL, ?, ?)""",
            (record_id, user_id, metric, value_of(form), UNITS[metric],
             form.get("glucose_context") if metric == "Blood glucose" else None,
             parse_time(form["measured_at"]).strftime(DB_TIME),
             gestational_week(date.fromisoformat(edd[0]), now.date()), submitted),
        )
    report_id = str(uuid.uuid4())
    other = (form.get("other_symptom_text") or "").strip() or None
    note = (form.get("note") or "").strip() or None
    conn.execute(
        """INSERT INTO METRIC_REPORT (report_id, report_code, user_id, metric, health_metric_record_id,
               other_symptom_text, note, submitted_at, watch_flag_id)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (report_id, next_report_code(conn, now), user_id, metric, record_id, other, note, submitted,
         active_flag(conn, user_id, metric) if metric != "Symptom" else None),
    )
    conn.executemany("INSERT INTO REPORT_SYMPTOM (report_id, symptom) VALUES (?, ?)",
                     [(report_id, s) for s in form["symptoms"]])
    return {"report_id": report_id, "record_id": record_id, "value": value_of(form)}
