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


APPOINTMENTS = "TCI_HOST_APPOINTMENT"


def has_appointments(conn):
    return conn.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name=?", (APPOINTMENTS,)).fetchone() is not None


def appointments(conn, user_id, now):
    """Host-owned rows, partitioned the same way for the list and Home."""
    if not has_appointments(conn):
        return [], []
    rows = conn.execute(f"""SELECT a.*,s.full_name AS doctor,v.visit_date AS result_day
                           FROM {APPOINTMENTS} a LEFT JOIN STAFF s ON s.staff_id=a.doctor_id
                           LEFT JOIN VISIT v ON v.visit_id=a.visit_id AND v.user_id=a.user_id
                               AND v.visit_date=substr(a.appointment_at,1,10)
                           WHERE a.user_id=? ORDER BY a.appointment_at,a.appointment_id""", (user_id,)).fetchall()
    current, history = [], []
    for row in rows:
        when = datetime.fromisoformat(row["appointment_at"])
        active = row["status"] in ("Pending", "Confirmed") and when > now
        (current if active else history).append(row)
    return current, history[::-1]


def next_appointment(conn, user_id, now):
    current, _ = appointments(conn, user_id, now)
    if not current:
        return None
    row = current[0]
    when = datetime.fromisoformat(row["appointment_at"])
    return {"long_day": LONG_DAYS[when.weekday()], "at": when.strftime("%d/%m/%Y · %H:%M"),
            "days": (when.date() - now.date()).days, "place": row["facility"]}
