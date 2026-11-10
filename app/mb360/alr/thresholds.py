"""ALR BR-004 / BR-005: threshold check, read from THRESHOLD_RULE (never hard-coded — AGENTS.md hard rule 7)."""
import sqlite3

NORMAL, ABOVE, NOT_ASSESSED = "Normal", "Above threshold", "Not assessed"

# Order of the dipstick scale (ALR FR-013); the threshold level itself comes from THRESHOLD_RULE.
URINE_SCALE = ["Negative", "Trace", "1+", "2+", "3+"]


def rules(conn: sqlite3.Connection, metric: str, glucose_context: str | None = None) -> list[sqlite3.Row]:
    """THRESHOLD_RULE rows used for the report check of one metric (and blood-glucose timing)."""
    return conn.execute(
        """SELECT * FROM THRESHOLD_RULE
           WHERE metric = ? AND purpose = 'Report check' AND COALESCE(glucose_context, '') = ?""",
        (metric, glucose_context or ""),
    ).fetchall()


def evaluate(conn: sqlite3.Connection, metric: str, value: str | None, glucose_context: str | None = None) -> str:
    if metric == "Symptom":
        return NOT_ASSESSED
    rows = rules(conn, metric, glucose_context)
    if not rows:
        raise LookupError(f"no THRESHOLD_RULE for {metric} {glucose_context or ''}".strip())
    hits = [_meets(row, metric, str(value)) for row in rows]
    combine = rows[0]["combine"] or "any"
    over = any(hits) if combine == "any" else all(hits)
    return ABOVE if over else NORMAL


def _meets(row: sqlite3.Row, metric: str, value: str) -> bool:
    if row["operator"] != "≥":
        raise ValueError(f"operator {row['operator']} is not a report check")
    limit = row["threshold_values"]
    if metric == "Blood pressure":
        systolic, diastolic = (int(x) for x in value.split("/"))
        measured = systolic if row["component"] == "systolic" else diastolic
        return measured >= int(limit)
    if metric == "Urine protein":
        return URINE_SCALE.index(value) >= URINE_SCALE.index(limit)
    return float(value) >= float(limit)


def live_rules(conn: sqlite3.Connection, metric: str) -> dict:
    """The same THRESHOLD_RULE rows for the live hint while the mother types on S-025A; the server still decides on submit."""
    if metric == "Blood pressure":
        return {r["component"]: float(r["threshold_values"]) for r in rules(conn, metric)}
    if metric == "Blood glucose":
        return {c: float(r[0]["threshold_values"]) for c in ("fasting", "post_1h", "post_2h") if (r := rules(conn, metric, c))}
    if metric == "Urine protein":
        limit = rules(conn, metric)[0]["threshold_values"]
        return {"above": URINE_SCALE[URINE_SCALE.index(limit):]}
    return {}


def card_text(conn: sqlite3.Connection, metric: str, glucose_context: str | None = None) -> str | None:
    """Text of the threshold card on S-025A, built from the same rows (US-1 scenario 3)."""
    rows = rules(conn, metric, glucose_context)
    if not rows:
        return None
    unit = rows[0]["unit"]
    if metric == "Blood pressure":
        by = {r["component"]: r["threshold_values"] for r in rows}
        return f"Above threshold when ≥ {by['systolic']}/{by['diastolic']} {unit}"
    suffix = "" if unit in (None, "", "—") else f" {unit}"
    return f"Above threshold when ≥ {rows[0]['threshold_values']}{suffix}"
