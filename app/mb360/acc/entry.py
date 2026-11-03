"""ACC FR-011, FR-015: open the sub-app with a TCI identity, consent, session (research R2, R3).

The identity arrives from the simulated TCI app (`/tci`) because the real mechanism is open
(spec-ACC §10 Q9); it is a demo stand-in, not a security design."""
import sqlite3
import uuid
from datetime import datetime, timedelta

DB_TIME = "%Y-%m-%d %H:%M"
SESSION_HOURS = 12          # provisional: lifetime of the ordinary seed sessions (§10 Q9, Q22)
PREFERENCE_DEFAULTS = (1, 1, 1, 0)   # DM-41 seed defaults (§10 Q22): report, visit result, appointment, instruction reminder
COPY = ("full_name", "phone", "date_of_birth", "record_code")
COOKIE = "mb360_session"
SECURE_COOKIE = False     # mb360.server: True on the hosting platform (HTTPS)


class EntryError(Exception):
    def __init__(self, field: str, message: str):
        super().__init__(message)
        self.field, self.message = field, message


def _account(conn, tci_ref: str):
    return conn.execute("SELECT * FROM USER_ACCOUNT WHERE tci_account_ref = ?", (tci_ref,)).fetchone()


def _new_session(conn, user_id: str, now: datetime) -> str:
    token = f"sess-{uuid.uuid4().hex}"
    conn.execute("INSERT INTO SESSION (session_token, user_id, role, created_at, expires_at) VALUES (?, ?, 'Mother', ?, ?)",
                 (token, user_id, now.strftime(DB_TIME), (now + timedelta(hours=SESSION_HOURS)).strftime(DB_TIME)))
    return token


def _next_step(conn, user_id: str) -> str:
    """BR-006: setup only when there is no due date."""
    has_edd = conn.execute("SELECT 1 FROM PREGNANCY_PROFILE WHERE user_id = ?", (user_id,)).fetchone()
    return "home" if has_edd else "setup"


def _run(conn, write):
    try:
        result = write()
        conn.commit()
        return result
    except Exception:
        conn.rollback()
        raise


def open_subapp(conn: sqlite3.Connection, identity: dict, now: datetime) -> tuple[str, str | None]:
    """FR-015. Returns (outcome, user_id): not_female | consent | setup | home."""
    if identity.get("sex") != "Female":              # BR-007, D-71: nothing is written
        return "not_female", None
    acc = _account(conn, identity["tci_account_ref"])
    if acc is None:                                 # first opening: S-001 state 2 (BR-004)
        return "consent", None
    user_id = acc["user_id"]
    if conn.execute("SELECT 1 FROM CONSENT_RECORD WHERE user_id = ? AND accepted = 1", (user_id,)).fetchone() is None:
        return "consent", None                      # known to the hospital, first opening of the sub-app (BR-004)

    def write():
        # DM-18 default: refresh the copy of the TCI identity at every opening
        conn.execute("UPDATE USER_ACCOUNT SET full_name = ?, phone = ?, date_of_birth = ?, record_code = ? WHERE user_id = ?",
                     (*[identity.get(k) or None for k in COPY], user_id))
        _new_session(conn, user_id, now)
    _run(conn, write)
    return _next_step(conn, user_id), user_id


def agree(conn: sqlite3.Connection, identity: dict, accepted: bool, now: datetime) -> str:
    """FR-011 + FR-015: the box must be ticked (BR-004); creates the account copy, consent, preferences and session."""
    if not accepted:
        raise EntryError("agree", "Please tick the box to agree to the Terms and the Privacy Policy.")
    if identity.get("sex") != "Female":
        raise EntryError("sex", "Mother & Baby 360 is for expectant mothers.")
    acc = _account(conn, identity["tci_account_ref"])
    at = now.strftime(DB_TIME)

    def write():
        if acc is not None:
            user_id = acc["user_id"]
        else:
            user_id = str(uuid.uuid4())
            conn.execute("""INSERT INTO USER_ACCOUNT (user_id, tci_account_ref, full_name, phone, date_of_birth, sex, record_code, role)
                            VALUES (?, ?, ?, ?, ?, 'Female', ?, 'Mother')""",
                         (user_id, identity["tci_account_ref"], identity["full_name"], identity["phone"],
                          identity["date_of_birth"], identity.get("record_code") or None))
            conn.execute("""INSERT INTO NOTIFICATION_PREFERENCE (user_id, report_response, new_visit_result, appointment_reminder,
                                watch_flag_reminder, updated_at) VALUES (?, ?, ?, ?, ?, ?)""", (user_id, *PREFERENCE_DEFAULTS, at))
        if conn.execute("SELECT 1 FROM CONSENT_RECORD WHERE user_id = ? AND accepted_at = ?", (user_id, at)).fetchone() is None:
            conn.execute("""INSERT INTO CONSENT_RECORD (user_id, accepted_at, accepted, terms_version, tci_data_permission)
                            VALUES (?, ?, 1, NULL, 1)""", (user_id, at))
        _new_session(conn, user_id, now)
        return user_id
    return _run(conn, write)


def next_step(conn: sqlite3.Connection, user_id: str) -> str:
    return _next_step(conn, user_id)


def latest_session(conn: sqlite3.Connection, user_id: str) -> str | None:
    row = conn.execute("SELECT session_token FROM SESSION WHERE user_id = ? ORDER BY created_at DESC, rowid DESC LIMIT 1", (user_id,)).fetchone()
    return row[0] if row else None


def valid_session(conn: sqlite3.Connection, token: str | None, user_id: str, now: datetime) -> bool:
    """The token is this mother's and has not expired."""
    if not token:
        return False
    row = conn.execute("SELECT expires_at FROM SESSION WHERE session_token = ? AND user_id = ?", (token, user_id)).fetchone()
    return row is not None and row[0] > now.strftime(DB_TIME)
