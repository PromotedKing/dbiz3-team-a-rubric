"""S-105 "My journey": TML FR-013, BR-001, BR-007 (specs/011-tml-journey, research R1 – R3). Read-only."""
import sqlite3
from datetime import date, datetime

from . import weeks

# D-75; boundaries Pending SME (TML §10 Q16). Derived from the due date, never stored.
STAGES = ({"name": "First trimester", "first": 0, "last": 13}, {"name": "Second trimester", "first": 14, "last": 27},
          {"name": "Third trimester", "first": 28, "last": 42}, {"name": "Full journey", "first": 0, "last": 42})


def _week_block(conn: sqlite3.Connection, user_id: str, edd: date, n: int, current: int) -> dict | None:
    w = weeks.week_content(conn, user_id, edd, n, current)
    if not (w["visits"] or w["diary"] or w["messages"]):
        return None
    for e in w["diary"]:
        e["photos"] = [r[0] for r in conn.execute("SELECT file FROM DIARY_IMAGE WHERE diary_id = ? ORDER BY sort_order", (e["diary_id"],))]
    return w


def _visit_count(conn: sqlite3.Connection, user_id: str, edd: date, stage: dict, current: int) -> int:
    last = min(stage["last"], current)
    if last < stage["first"]:
        return 0
    start, end = weeks.week_range(edd, stage["first"])[0], weeks.week_range(edd, last)[1]
    return conn.execute("SELECT COUNT(*) FROM VISIT WHERE user_id = ? AND visit_date >= ? AND visit_date <= ?",
                        (user_id, start.isoformat(), end.isoformat())).fetchone()[0]


def load(conn: sqlite3.Connection, user_id: str, stage_name: str | None, now: datetime) -> dict | None:
    row = conn.execute("SELECT edd FROM PREGNANCY_PROFILE WHERE user_id = ?", (user_id,)).fetchone()
    if row is None:
        return None
    edd = date.fromisoformat(row[0])
    current = weeks.current_week(edd, now.date())
    current_stage = weeks.trimester(current)
    stage = next((s for s in STAGES if s["name"] == stage_name), None) or next(s for s in STAGES if s["name"] == current_stage)
    not_reached = stage["first"] > current
    blocks = []
    if not not_reached:
        for n in range(max(stage["first"], weeks.FIRST_WEEK), min(stage["last"], current) + 1):
            block = _week_block(conn, user_id, edd, n, current)
            if block:
                blocks.append(block)
    rows = []
    for s in STAGES[:3]:
        state = "Current" if s["name"] == current_stage else "To come" if s["first"] > current else "Past"
        rows.append({**s, "state": state, "visits": _visit_count(conn, user_id, edd, s, current)})
    return {"stage": stage["name"], "first": stage["first"], "last": stage["last"], "current": current, "not_reached": not_reached,
            "weeks": blocks, "can_export": bool(blocks), "stages": [s["name"] for s in STAGES], "stage_rows": rows,
            "counts": {"visits": sum(len(w["visits"]) for w in blocks), "diary": sum(len(w["diary"]) for w in blocks),
                       "photos": sum(len(e["photos"]) for w in blocks for e in w["diary"])}}
