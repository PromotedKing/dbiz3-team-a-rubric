"""Generated demo fixtures for the simulated TCI host, not a production scheduler.

One-day timing and retaining received notices when disabled are demo assumptions.
S-010 Q3/Q4 remain open. No appointment is added to the MB360 schema.
"""
import csv
import json
import sqlite3
import uuid
from datetime import datetime, timedelta

from . import db as dbmod, demo_clinical, demo_diary, tci_booking, tci_feed


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
            if offset == 0:
                when = tci_booking.same_day_slot(now).strftime("%Y-%m-%d %H:%M")
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
    if fresh_demo:
        if tci_feed.has_appointments(conn):
            conn.execute(f"DELETE FROM {tci_feed.APPOINTMENTS}")
        tci_booking.install(conn, now)
    elif not tci_feed.has_appointments(conn):
        tci_booking.install(conn, now)
    # PR A stored seeded slots without a reminder. Only its stable fixture IDs
    # receive the demo default; explicitly disabled user bookings stay off.
    for user, at, appointment_id in conn.execute(f"SELECT user_id, appointment_at, appointment_id FROM {tci_feed.APPOINTMENTS} WHERE reminder_at IS NULL"):
        fixture_id = str(uuid.uuid5(uuid.NAMESPACE_URL, f"tci-upcoming/{user}"))
        if appointment_id != fixture_id:
            continue
        reminder = (datetime.fromisoformat(at).date() - timedelta(days=1)).isoformat() + " 00:00"
        conn.execute(f"UPDATE {tci_feed.APPOINTMENTS} SET reminder_at=?,reminder_enabled=1 WHERE appointment_id=?",
                     (reminder, fixture_id))
    create_reminders(conn, now)
    conn.commit()


def create_reminders(conn: sqlite3.Connection, now: datetime, user_id: str | None = None) -> None:
    """Demo delivery at startup / Home / S-009 access, at most once per host visit.

    The real TCI delivery channel and scheduling are outside this demo. Disabled
    switches stop NEW reminders; they never delete or hide a received notice.
    """
    if not tci_feed.has_appointments(conn):
        return
    # Only the interactive TCI confirmation writes an estimated fee. Imported
    # visits and seeded upcoming slots leave it NULL.
    events = conn.execute(f"""SELECT a.*, s.full_name AS doctor FROM {tci_feed.APPOINTMENTS} a
                              LEFT JOIN STAFF s ON s.staff_id=a.doctor_id
                              WHERE a.estimated_fee IS NOT NULL AND a.visit_id IS NULL
                                AND (? IS NULL OR a.user_id=?)""", (user_id, user_id))
    current = now.strftime("%Y-%m-%d %H:%M")
    for row in events:
        when = datetime.fromisoformat(row["appointment_at"]).strftime("%d/%m/%Y · %H:%M")
        doctor = row["doctor"] or "Chưa ghi nhận bác sĩ"
        for event, stamp, title, subtitle in (
            ("booked", row["created_at"], "Đã đặt lịch thành công", f"{when} · {doctor}"),
            ("cancelled", row["cancelled_at"], f"Lịch {when} đã được hủy", doctor),
        ):
            if stamp is None or stamp > current:
                continue
            notification = str(uuid.uuid5(uuid.NAMESPACE_URL, f"mb360-appointment/{row['appointment_id']}/{event}"))
            conn.execute("""INSERT OR IGNORE INTO NOTIFICATION
                            (notification_id,user_id,type,title,subtitle,created_at,appointment_ref)
                            VALUES (?,?,'Appointment',?,?,?,?)""",
                         (notification,row["user_id"],title,subtitle,stamp,row["appointment_id"]))

    rows = conn.execute(f"""SELECT f.* FROM {tci_feed.APPOINTMENTS} f
                           JOIN NOTIFICATION_PREFERENCE p ON p.user_id=f.user_id
                           WHERE p.appointment_reminder=1 AND f.reminder_enabled=1 AND f.status IN ('Pending','Confirmed') AND (? IS NULL OR f.user_id=?)""", (user_id, user_id)).fetchall()
    for row in rows:
        when = datetime.fromisoformat(row["appointment_at"])
        reminder = row["reminder_at"]
        if not reminder or not datetime.fromisoformat(reminder) <= now < when:
            continue
        reference = row["appointment_id"]
        legacy = f"{row['user_id']}:{when:%Y%m%d%H%M}"
        if conn.execute("SELECT 1 FROM NOTIFICATION WHERE user_id=? AND type='Appointment' AND appointment_ref=?",
                        (row["user_id"], legacy)).fetchone():
            continue
        day_label = "ngày mai " if (when.date() - now.date()).days == 1 else ""
        notification = str(uuid.uuid5(uuid.NAMESPACE_URL, f"mb360-demo-reminder/{reference}/{reminder}"))
        conn.execute("""INSERT OR IGNORE INTO NOTIFICATION
                        (notification_id, user_id, type, title, subtitle, created_at, read_at,
                         case_id, visit_id, watch_flag_id, appointment_ref)
                        VALUES (?, ?, 'Appointment', 'Appointment reminder', ?, ?, NULL, NULL, NULL, NULL, ?)""",
                     (notification, row["user_id"], f"Nhắc mẹ khám thai {day_label}{when:%d/%m/%Y · %H:%M} tại {row['facility']}.",
                      now.strftime("%Y-%m-%d %H:%M"), reference))
    conn.commit()
