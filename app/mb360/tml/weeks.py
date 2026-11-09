"""S-048 week data: TML FR-003 – FR-006, FR-012, BR-001, BR-003, BR-008; D-04, D-75 (research R1 – R3)."""
import sqlite3
from datetime import date, timedelta

from ..hlt.dashboard import sleep_duration

PREGNANCY_DAYS = 280
FIRST_WEEK, LAST_WEEK = 0, 42          # domain of gestational_week (TML §10 Q14 open)
# FR-004: adjacent weeks prefetched (server side). An entry is reused only while the database has not changed since
# it was built (same connection, same total_changes), so a report or a self-tracked value never shows stale data.
CACHE: dict[tuple[str, int], tuple[tuple[int, int], dict]] = {}
SHORT_DAYS = ("Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun")
LONG_DAYS = ("Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday")


def current_week(edd: date, today: date) -> int:
    return (PREGNANCY_DAYS - (edd - today).days) // 7


def week_range(edd: date, n: int) -> tuple[date, date]:
    start = edd - timedelta(days=PREGNANCY_DAYS) + timedelta(days=7 * n)
    return start, start + timedelta(days=6)


def day_of_week(edd: date, day: date) -> int:
    """Days past the whole gestational week ("Week 24 + 3 days")."""
    return (PREGNANCY_DAYS - (edd - day).days) % 7


def progress(edd: date, today: date) -> int:
    """Share of the 280 days already passed, 0 – 100 (bar on S-008)."""
    return max(0, min(100, round((PREGNANCY_DAYS - (edd - today).days) * 100 / PREGNANCY_DAYS)))


def trimester(week: int) -> str:
    """Stage of a gestational week: boundaries 0 – 13 / 14 – 27 / 28 – 42 of D-75, Pending SME (TML §10 Q16)."""
    return "First trimester" if week <= 13 else "Second trimester" if week <= 27 else "Third trimester"


def week_days(w: dict, today: date) -> list[dict]:
    """The 7 days of a week for the strip and the "This week" list of S-048 (D-80), oldest first."""
    rows = {d["day"]: d["rows"] for d in w["days"]}
    visits = {v["visit_date"] for v in w["visits"]}
    out = []
    for i in range(7):
        day = w["start"] + timedelta(days=i)
        iso = day.isoformat()
        diary = [e for e in w["diary"] if e["entry_date"] == iso]
        out.append({"iso": iso, "num": day.strftime("%d"), "short": SHORT_DAYS[day.weekday()], "long": LONG_DAYS[day.weekday()],
                    "future": day > today, "is_today": day == today, "has_visit": iso in visits, "has_diary": bool(diary),
                    "has_rows": iso in rows, "row_count": len(rows.get(iso, [])),
                    "mood": next((e["mood"] for e in diary if e["mood"]), None), "diary_texts": [e["text"] for e in diary]})
    return out


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
        value = sleep_duration(r["value"]) if r["metric"] == "Sleep" else _with_unit(r["value"], r["unit"])
        days.setdefault(r["measured_at"][:10], []).append(
            {"metric": r["metric"], "value": value, "source": r["source"], "at": r["measured_at"]})
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


def week_content(conn: sqlite3.Connection, user_id: str, edd: date, n: int, current: int) -> dict:
    """One week, freshly read and not cached (S-105)."""
    return _build(conn, user_id, edd, n, current)


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
