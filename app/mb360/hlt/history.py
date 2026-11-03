"""S-025 "Metric history" and S-027 cards: HLT FR-009 – FR-012, BR-003 – BR-005, US-3 (specs/010-hlt-history, research R1 – R5)."""
import sqlite3
from datetime import date, datetime, timedelta

from ..alr import thresholds
from .dashboard import GROUP1, GROUP2, sleep_duration

METRICS = ("Blood pressure", "Blood glucose", "Urine protein", "Fetal heart rate", "Weight", "Temperature", "Heart rate", "Sleep")
CONTEXTS = ("fasting", "post_1h", "post_2h")
DEFAULT_DAYS = 30                       # HLT §10 Q12 open
# Chart box: the viewBox of the UI package (320 x 160)
LEFT, RIGHT, TOP, BOTTOM = 34.0, 312.0, 12.0, 136.0


def _with_unit(value: str, unit: str | None) -> str:
    return f"{value} {unit}" if unit else value


def _sleep_hours(value: str) -> float:
    start, end = (datetime.strptime(x, "%H:%M") for x in value.split("-"))
    return ((end - start).total_seconds() / 60 % (24 * 60)) / 60


def _lines(conn: sqlite3.Connection, metric: str, context: str | None) -> list[dict]:
    """FR-012, read from THRESHOLD_RULE only (hard rule 7). Group 1 has none (BR-003)."""
    if metric == "Fetal heart rate":                       # BR-005: a reference, never a threshold
        row = conn.execute("SELECT threshold_values FROM THRESHOLD_RULE WHERE metric = ? AND purpose = 'Display only'", (metric,)).fetchone()
        return [{"value": float(v), "kind": "reference", "label": v} for v in row[0].split("–")] if row else []
    if metric not in GROUP2 or (metric == "Blood glucose" and not context):
        return []
    rows = thresholds.rules(conn, metric, context)
    if metric == "Blood pressure":
        rows = sorted(rows, key=lambda r: r["component"] != "systolic")
    if metric == "Urine protein":
        return [{"value": float(thresholds.URINE_SCALE.index(r["threshold_values"])), "kind": "threshold", "label": r["threshold_values"]} for r in rows]
    return [{"value": float(r["threshold_values"]), "kind": "threshold", "label": r["threshold_values"]} for r in rows]


def line_text(conn: sqlite3.Connection, metric: str, context: str | None) -> tuple[str, str] | None:
    """Caption of the lines: ("threshold" | "reference", "140/90 mmHg")."""
    if metric == "Fetal heart rate":
        row = conn.execute("SELECT threshold_values, unit FROM THRESHOLD_RULE WHERE metric = ? AND purpose = 'Display only'", (metric,)).fetchone()
        return ("reference", f"{row['threshold_values']} {row['unit']}") if row else None
    lines = _lines(conn, metric, context)
    if not lines:
        return None
    unit = thresholds.rules(conn, metric, context)[0]["unit"]
    text = "/".join(line["label"] for line in lines)
    return "threshold", text if unit in (None, "", "—") else f"{text} {unit}"


def chart(series: list[tuple[str, list[tuple[float, float]]]], lines: list[dict]) -> dict:
    """Inline-SVG geometry: time goes right, higher values go up, everything inside the box (research R4)."""
    xs = [x for _, pts in series for x, _ in pts]
    ys = [y for _, pts in series for _, y in pts] + [line["value"] for line in lines]
    x_lo, x_hi = min(xs), max(xs)
    y_lo, y_hi = min(ys), max(ys)
    pad = (y_hi - y_lo) * 0.1 or 1.0
    y_lo, y_hi = y_lo - pad, y_hi + pad

    def px(x: float) -> float:
        return round(LEFT + (x - x_lo) / (x_hi - x_lo) * (RIGHT - LEFT), 1) if x_hi > x_lo else (LEFT + RIGHT) / 2

    def py(y: float) -> float:
        return round(BOTTOM - (y - y_lo) / (y_hi - y_lo) * (BOTTOM - TOP), 1)

    return {"series": [{"name": name, "points": [{"x": px(x), "y": py(y)} for x, y in pts],
                        "polyline": " ".join(f"{px(x)},{py(y)}" for x, y in pts)} for name, pts in series],
            "lines": [{**line, "y": py(line["value"])} for line in lines],
            "ticks": [{"y": py(v), "text": f"{v:g}"} for v in (round(y_hi), round((y_hi + y_lo) / 2), round(y_lo))],
            "left": LEFT, "right": RIGHT, "bottom": BOTTOM}


def _stats(metric: str, rows: list[sqlite3.Row]) -> dict | None:
    """FR-011. Blood pressure: systolic and diastolic separately. Urine protein and sleep: open (HLT §10 Q12)."""
    if not rows or metric in ("Urine protein", "Sleep"):
        return None
    if metric == "Blood pressure":
        pairs = [tuple(int(x) for x in r["value"].split("/")) for r in rows]
        sys_, dia = [p[0] for p in pairs], [p[1] for p in pairs]
        return {"average": f"{round(sum(sys_) / len(sys_))}/{round(sum(dia) / len(dia))}", "lowest": f"{min(sys_)}/{min(dia)}", "highest": f"{max(sys_)}/{max(dia)}"}
    values = [float(r["value"]) for r in rows]
    decimals = max((len(r["value"].split(".")[1]) if "." in r["value"] else 0) for r in rows)
    fmt = f"{{:.{max(decimals, 1) if len(values) > 1 else decimals}f}}"
    return {"average": fmt.format(sum(values) / len(values)), "lowest": fmt.format(min(values)), "highest": fmt.format(max(values))}


def _series(metric: str, rows: list[sqlite3.Row]) -> list[tuple[str, list[tuple[float, float]]]]:
    def when(r):
        return datetime.strptime(r["measured_at"], "%Y-%m-%d %H:%M").timestamp()

    if metric == "Blood pressure":
        pairs = [(when(r), *(float(x) for x in r["value"].split("/"))) for r in rows]
        return [("Systolic", [(t, s) for t, s, _ in pairs]), ("Diastolic", [(t, d) for t, _, d in pairs])]
    if metric == "Urine protein":
        return [(metric, [(when(r), float(thresholds.URINE_SCALE.index(r["value"]))) for r in rows])]
    if metric == "Sleep":
        return [(metric, [(when(r), _sleep_hours(r["value"])) for r in rows])]
    return [(metric, [(when(r), float(r["value"])) for r in rows])]


def load(conn: sqlite3.Connection, user_id: str, metric: str, start: date | None, end: date | None, context: str | None, now: datetime) -> dict:
    metric = metric if metric in METRICS else METRICS[0]
    context = context if metric == "Blood glucose" and context in CONTEXTS else None
    end = end or now.date()
    start = start or end - timedelta(days=DEFAULT_DAYS)
    out = {"metric": metric, "context": context, "start": start, "end": end, "error": None, "rows": [], "stats": None,
           "chart": None, "lines": [], "line_text": None}
    if start > end:
        out["error"] = "The start date must not be after the end date."
        return out
    sql = """SELECT * FROM HEALTH_METRIC_RECORD WHERE user_id = ? AND metric = ? AND measured_at >= ? AND measured_at < ?"""
    args = [user_id, metric, start.isoformat(), (end + timedelta(days=1)).isoformat()]
    if metric == "Fetal heart rate":                       # BR-005
        sql += " AND source = 'From visit'"
    if context:
        sql += " AND glucose_context = ?"
        args.append(context)
    records = conn.execute(sql + " ORDER BY measured_at, created_at", args).fetchall()
    out["lines"] = _lines(conn, metric, context)
    out["line_text"] = line_text(conn, metric, context)
    for r in reversed(records):
        label = thresholds.evaluate(conn, metric, r["value"], r["glucose_context"]) if metric in GROUP2 else None   # BR-003, BR-005
        value = sleep_duration(r["value"]) if metric == "Sleep" else _with_unit(r["value"], r["unit"])
        out["rows"].append({"value": value, "at": r["measured_at"], "source": r["source"], "label": label, "context": r["glucose_context"]})
    if records:
        out["stats"] = _stats(metric, records)
        out["chart"] = chart(_series(metric, records), out["lines"])
    return out


def instruction_cards(conn: sqlite3.Connection, user_id: str) -> list[dict]:
    """HLT US-3 #1: S-027 cards; group 2 metrics only, because only those can be assigned (D-11)."""
    cards = []
    for f in conn.execute("""SELECT w.metric, w.note, w.flagged_at, s.full_name FROM WATCH_FLAG w JOIN STAFF s ON s.staff_id = w.flagged_by
                             WHERE w.user_id = ? AND w.active = 1 ORDER BY w.metric""", (user_id,)):
        last = conn.execute("""SELECT h.* FROM METRIC_REPORT r JOIN HEALTH_METRIC_RECORD h ON h.record_id = r.health_metric_record_id
                               WHERE r.user_id = ? AND h.metric = ? ORDER BY r.submitted_at DESC, r.rowid DESC LIMIT 1""", (user_id, f["metric"])).fetchone()
        cards.append({"metric": f["metric"], "note": f["note"], "flagged_at": f["flagged_at"], "doctor": f["full_name"],
                      "latest_value": _with_unit(last["value"], last["unit"]) if last else None,
                      "latest_at": last["measured_at"] if last else None,
                      "latest_label": thresholds.evaluate(conn, last["metric"], last["value"], last["glucose_context"]) if last else None})
    return sorted(cards, key=lambda c: GROUP2.index(c["metric"]))
