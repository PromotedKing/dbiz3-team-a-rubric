"""S-023 "Health metrics": HLT FR-001, FR-004, FR-005, FR-008, BR-001, BR-004, BR-005 (research R1 – R3)."""
import sqlite3
from datetime import datetime

from ..alr import thresholds

VISIT_ORDER = ("Blood pressure", "Fetal heart rate", "Weight", "Blood glucose", "Urine protein")   # S-023 #7 – #11
GROUP1 = ("Weight", "Temperature", "Heart rate", "Sleep")
GROUP2 = ("Blood pressure", "Blood glucose", "Urine protein")


def _with_unit(value: str, unit: str | None) -> str:
    return f"{value} {unit}" if unit else value


def sleep_duration(value: str) -> str:
    """'22:30-06:00' -> '7 h 30 min' (overnight allowed)."""
    start, end = (datetime.strptime(x, "%H:%M") for x in value.split("-"))
    minutes = int((end - start).total_seconds() // 60) % (24 * 60)
    return f"{minutes // 60} h {minutes % 60:02d} min" if minutes % 60 else f"{minutes // 60} h"


def reference_range(conn: sqlite3.Connection) -> str | None:
    """BR-005, D-12: display-only range for fetal heart rate, read from THRESHOLD_RULE."""
    row = conn.execute("SELECT threshold_values, unit FROM THRESHOLD_RULE WHERE metric = 'Fetal heart rate' AND purpose = 'Display only'").fetchone()
    return f"{row['threshold_values']} {row['unit']}" if row else None


def load(conn: sqlite3.Connection, user_id: str, now: datetime) -> dict:
    visit = conn.execute("SELECT * FROM VISIT WHERE user_id = ? ORDER BY visit_date DESC LIMIT 1", (user_id,)).fetchone()
    visit_rows = []
    if visit:
        recs = {r["metric"]: r for r in conn.execute(
            "SELECT * FROM HEALTH_METRIC_RECORD WHERE visit_id = ? AND source = 'From visit'", (visit["visit_id"],))}
        ref = reference_range(conn)
        for metric in VISIT_ORDER:
            r = recs.get(metric)
            row = {"metric": metric, "value": None, "label": None, "reference": None, "source": "From visit"}
            if r:
                row["value"] = _with_unit(r["value"], r["unit"])
                if metric in GROUP2:                       # FR-001: label computed from THRESHOLD_RULE (ALR BR-004)
                    row["label"] = thresholds.evaluate(conn, metric, r["value"], r["glucose_context"])
                if metric == "Fetal heart rate":           # BR-005: reference only, never a label
                    row["reference"] = ref
            visit_rows.append(row)

    instructions = [r[0] for r in conn.execute("SELECT metric FROM WATCH_FLAG WHERE user_id = ? AND active = 1 ORDER BY metric", (user_id,))]
    open_cases = conn.execute("SELECT status FROM CARE_CASE WHERE user_id = ? AND status <> 'Resolved' ORDER BY created_at DESC", (user_id,)).fetchall()

    self_tracked = []
    for metric in GROUP1:
        r = conn.execute("""SELECT * FROM HEALTH_METRIC_RECORD WHERE user_id = ? AND metric = ? AND source = 'Self-entered'
                            ORDER BY measured_at DESC, created_at DESC LIMIT 1""", (user_id, metric)).fetchone()
        if r:
            value = sleep_duration(r["value"]) if metric == "Sleep" else _with_unit(r["value"], r["unit"])
            self_tracked.append({"metric": metric, "value": value, "at": r["measured_at"], "label": None, "source": "Self-entered"})

    return {"visit_date": visit["visit_date"] if visit else None, "visit_rows": visit_rows, "instructions": instructions,
            "handling": len(open_cases), "latest_status": open_cases[0]["status"] if open_cases else None,
            "self_tracked": self_tracked}
