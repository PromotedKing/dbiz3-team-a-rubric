"""Generated demo fixtures for the simulated TCI host, not a production scheduler.

One-day timing and retaining received notices when disabled are demo assumptions.
S-010 Q3/Q4 remain open. No appointment is added to the MB360 schema.
"""
import csv
import json
import sqlite3
import uuid
from datetime import datetime, timedelta

from . import db as dbmod, demo_clinical, demo_diary, tci_feed


def install(conn: sqlite3.Connection, now: datetime, *, fresh_demo: bool = False) -> None:
    """Idempotently add demo cases, also when opening an older local demo DB.

    The host table is the boundary: plain schema/seed databases stay untouched.
    Existing switches, read times and appointments survive re-opening the DB.
    Only a fresh demo rebases the seeded pregnancy profiles.
    """
    if not conn.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name=?", (tci_feed.TABLE,)).fetchone():
        return
    fixtures = json.loads((dbmod.SEED_DIR / "appointment-demo.json").read_text(encoding="utf-8"))
    ids = {row["user_id"] for row in fixtures}
    for path in sorted(dbmod.SEED_DIR.glob("[0-9][0-9]_*.csv")):
        table = path.stem.split("_", 1)[1]
        if table not in {"USER_ACCOUNT", "CONSENT_RECORD", "PREGNANCY_PROFILE", "NOTIFICATION_PREFERENCE"}:
            continue
        with path.open(encoding="utf-8", newline="") as file:
            reader = csv.DictReader(file)
            cols = reader.fieldnames
            for row in reader:
                if row["user_id"] in ids:
                    conn.execute(f"INSERT OR IGNORE INTO {table} ({', '.join(cols)}) VALUES ({', '.join('?' for _ in cols)})",
                                 [row[c] or None for c in cols])
    for fixture in fixtures:
        if not fresh_demo and fixture.get("fresh_only"):
            continue
        user = fixture["user_id"]
        if conn.execute(f"SELECT 1 FROM {tci_feed.TABLE} WHERE user_id=?", (user,)).fetchone():
            continue
        offset = fixture["days_until_appointment"]
        when = f"{now.date() + timedelta(days=offset)} {fixture['time']}" if offset is not None else None
        if fresh_demo:
            lmp = now.date() - timedelta(days=fixture["gestational_days"])
            edd = (lmp + timedelta(days=280)).isoformat()
            demo_clinical.install_visits(conn, user, lmp, fixture["visits"])
            diary = fixture["diary"]
            demo_diary.install(conn, user, lmp, now.date(), diary["counts"], diary["photo_phase"])
            first, last = conn.execute(
                "SELECT MIN(visit_date), MAX(visit_date) FROM VISIT WHERE user_id=?", (user,)
            ).fetchone()
            if fixture.get("appointment_at_last_visit") and last:
                when = f"{last} {fixture['time']}"
            conn.execute("UPDATE PREGNANCY_PROFILE SET edd=?, lmp=?, first_visit_date=? WHERE user_id=?",
                         (edd, lmp.isoformat() if fixture.get("use_lmp") else None, first, user))
            demo_clinical.align_cases(conn, user, lmp, now.date(), fixture["tci_ref"])
            demo_clinical.install_case(conn, user, fixture.get("clinical_case"), lmp, now)
            demo_clinical.install_staff_notices(conn, user, fixture["tci_ref"], now)
        elif fixture["days_until_edd"] is not None:
            edd = (now.date() + timedelta(days=fixture["days_until_edd"])).isoformat()
            conn.execute("UPDATE PREGNANCY_PROFILE SET edd=? WHERE user_id=?", (edd, user))
        else:
            edd = conn.execute("SELECT edd FROM PREGNANCY_PROFILE WHERE user_id=?", (user,)).fetchone()[0]
        conn.execute(f"INSERT INTO {tci_feed.TABLE} VALUES (?, ?, ?, ?)", (user, edd, when, fixture["place"]))
    create_reminders(conn, now)
    conn.commit()


def create_reminders(conn: sqlite3.Connection, now: datetime, user_id: str | None = None) -> None:
    """Demo delivery at startup / Home / S-009 access, at most once per host visit.

    The real TCI delivery channel and scheduling are outside this demo. Disabled
    switches stop NEW reminders; they never delete or hide a received notice.
    """
    if not conn.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name=?", (tci_feed.TABLE,)).fetchone():
        return
    rows = conn.execute(f"""SELECT f.* FROM {tci_feed.TABLE} f
                           JOIN NOTIFICATION_PREFERENCE p ON p.user_id=f.user_id
                           WHERE p.appointment_reminder=1 AND (? IS NULL OR f.user_id=?)""", (user_id, user_id)).fetchall()
    for row in rows:
        if not row["next_appointment"]:
            continue
        when = datetime.strptime(row["next_appointment"], "%Y-%m-%d %H:%M")
        if (when.date() - now.date()).days != 1:
            continue
        reference = f"{row['user_id']}:{when:%Y%m%d%H%M}"
        notification = str(uuid.uuid5(uuid.NAMESPACE_URL, f"mb360-demo-reminder/{reference}"))
        conn.execute("""INSERT OR IGNORE INTO NOTIFICATION
                        (notification_id, user_id, type, title, subtitle, created_at, read_at,
                         case_id, visit_id, watch_flag_id, appointment_ref)
                        VALUES (?, ?, 'Appointment', 'Appointment reminder', ?, ?, NULL, NULL, NULL, NULL, ?)""",
                     (notification, row["user_id"], f"Nhắc mẹ khám thai ngày mai {when:%d/%m/%Y · %H:%M} tại {row['appointment_place']}.",
                      now.strftime("%Y-%m-%d %H:%M"), reference))
    conn.commit()
