"""S-048 week data: TML FR-003 – FR-006, FR-012, BR-001, BR-003, BR-008; D-04, D-75 (research R1 – R3)."""
import sqlite3
from datetime import date, timedelta

PREGNANCY_DAYS = 280
FIRST_WEEK, LAST_WEEK = 0, 42          # domain of gestational_week (TML §10 Q14 open)
# FR-004: adjacent weeks prefetched (server side). An entry is reused only while the database has not changed since
# it was built (same connection, same total_changes), so a report or a self-tracked value never shows stale data.
CACHE: dict[tuple[str, int], tuple[tuple[int, int], dict]] = {}


def current_week(edd: date, today: date) -> int:
    return (PREGNANCY_DAYS - (edd - today).days) // 7


def week_range(edd: date, n: int) -> tuple[date, date]:
    start = edd - timedelta(days=PREGNANCY_DAYS) + timedelta(days=7 * n)
    return start, start + timedelta(days=6)


def clear(user_id: str) -> None:
    for key in [k for k in CACHE if k[0] == user_id]:
        del CACHE[key]


def _with_unit(value, unit):
    return f"{value} {unit}" if unit else value


def _build(conn: sqlite3.Connection, user_id: str, edd: date, n: int, current: int) -> dict:
    start, end = week_range(edd, n)
    lo, hi = start.isoformat(), (end + timedelta(days=1)).isoformat()
    days: dict[str, list] = {}
    for r in conn.execute("""SELECT metric, value, unit, source, measured_at FROM HEALTH_METRIC_RECORD
                             WHERE user_id = ? AND measured_at >= ? AND measured_at < ? ORDER BY measured_at DESC, metric""",
                          (user_id, lo, hi)):
        days.setdefault(r["measured_at"][:10], []).append(
            {"metric": r["metric"], "value": _with_unit(r["value"], r["unit"]), "source": r["source"], "at": r["measured_at"]})
    visits = [dict(v) for v in conn.execute(
        """SELECT visit_date, visit_type, ultrasound_image, fetal_length, estimated_fetal_weight, ultrasound_report_date, doctor_note
           FROM VISIT WHERE user_id = ? AND visit_date >= ? AND visit_date < ? ORDER BY visit_date""", (user_id, lo, hi))]
    diary = []
    for e in conn.execute("SELECT * FROM DIARY_ENTRY WHERE user_id = ? AND gestational_week = ? ORDER BY entry_date DESC, rowid DESC", (user_id, n)):
        photo = conn.execute("SELECT file FROM DIARY_IMAGE WHERE diary_id = ? ORDER BY sort_order LIMIT 1", (e["diary_id"],)).fetchone()
        diary.append({"diary_id": e["diary_id"], "entry_date": e["entry_date"], "text": e["text"], "mood": e["mood"],
                      "photo": photo[0] if photo else None})
    messages = [dict(m) for m in conn.execute(
        "SELECT author, text, created_at FROM FAMILY_MESSAGE WHERE user_id = ? AND week = ? ORDER BY created_at", (user_id, n))]
    return {"week": n, "current": current, "start": start, "end": end,
            "prev": n - 1 if n > FIRST_WEEK else None, "next": n + 1 if n < LAST_WEEK else None,
            "days": [{"day": d, "rows": rows} for d, rows in days.items()],     # newest day first (§10 Q17)
            "visits": visits, "diary": diary, "messages": messages}


def load_week(conn: sqlite3.Connection, user_id: str, n: int | None, today: date) -> dict | None:
    edd_row = conn.execute("SELECT edd FROM PREGNANCY_PROFILE WHERE user_id = ?", (user_id,)).fetchone()
    if edd_row is None:
        return None
    edd = date.fromisoformat(edd_row[0])
    current = current_week(edd, today)
    n = min(max(current if n is None else n, FIRST_WEEK), LAST_WEEK)
    stamp = (id(conn), conn.total_changes)
    for k in (n - 1, n, n + 1):                     # FR-004: keep the adjacent weeks ready
        if FIRST_WEEK <= k <= LAST_WEEK:
            cached = CACHE.get((user_id, k))
            if cached is None or cached[0] != stamp or cached[1]["current"] != current:
                CACHE[(user_id, k)] = (stamp, _build(conn, user_id, edd, k, current))
    return CACHE[(user_id, n)][1]
