"""What the simulated TCI host app holds for the signed-in mother: her identity, the due date in the hospital record and her
next appointment. Appointments stay in the TCI app (spec-APT), so none of this is in the MB360 schema: mb360.persona creates the
one host table when the app is served, and the test database simply has no such table."""
import sqlite3
from datetime import datetime

TABLE = "TCI_HOST_FEED"
DDL = f"""CREATE TABLE IF NOT EXISTS {TABLE} (user_id TEXT PRIMARY KEY, hospital_edd TEXT NOT NULL,
          next_appointment TEXT, appointment_place TEXT)"""
LONG_DAYS = ("Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday")


def _row(conn: sqlite3.Connection, user_id: str | None = None) -> sqlite3.Row | None:
    if conn.execute("SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = ?", (TABLE,)).fetchone() is None:
        return None
    if user_id:
        return conn.execute(f"SELECT * FROM {TABLE} WHERE user_id = ?", (user_id,)).fetchone()
    return conn.execute(f"SELECT * FROM {TABLE} LIMIT 1").fetchone()


def host_account(conn: sqlite3.Connection) -> sqlite3.Row | None:
    """The account signed in to the TCI app; without a host feed, the first account of the seed."""
    feed = _row(conn)
    if feed:
        return conn.execute("SELECT * FROM USER_ACCOUNT WHERE user_id = ?", (feed["user_id"],)).fetchone()
    return conn.execute("SELECT * FROM USER_ACCOUNT ORDER BY full_name LIMIT 1").fetchone()


def hospital_edd(conn: sqlite3.Connection, user_id: str) -> str | None:
    feed = _row(conn, user_id)
    return feed["hospital_edd"] if feed else None


def next_appointment(conn: sqlite3.Connection, user_id: str, now: datetime) -> dict | None:
    """The next appointment shown on Home (U2), None when none is booked or it has passed."""
    feed = _row(conn, user_id)
    if not feed or not feed["next_appointment"]:
        return None
    when = datetime.strptime(feed["next_appointment"], "%Y-%m-%d %H:%M")
    if when < now:
        return None
    return {"long_day": LONG_DAYS[when.weekday()], "at": when.strftime("%d/%m/%Y · %H:%M"), "days": (when.date() - now.date()).days,
            "place": feed["appointment_place"]}
