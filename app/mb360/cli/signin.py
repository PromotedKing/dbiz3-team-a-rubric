"""Staff sign-in of the clinical web (D-107, spec-CLI §7.3 "Sign-in (Q11)", §10 Q11; S-054 / S-060 have no mockup).

The staff member enters a username (STAFF.`login_account`) and the one shared team password (D-82). The session keeps
`staff_id` and `staff_role` in a signed cookie: nothing is stored, so there is no schema or seed change. The key lives in
the process only, so a restart of the app ends every staff session, as it does for the mother (D-100); "Sign out" ends it
at once. This identifies the role, it is not real authentication (§10 Q11 is still open).

Password rule (team decision 21/11/2026, same as the D-82 gate): with MB360_STAFF_PASSWORD set, only that password is
accepted; without it, a team machine skips the password and the hosting platform refuses every sign-in.
"""
import hashlib
import hmac
import secrets
import sqlite3

COOKIE = "mb360_staff"
PASSWORD: str | None = None      # set by mb360.server from MB360_STAFF_PASSWORD
HOSTED = False                   # set by mb360.server on the hosting platform
SECURE_COOKIE = False
_KEY = secrets.token_bytes(32)


def _sign(payload: str) -> str:
    return hmac.new(_KEY, payload.encode("utf-8"), hashlib.sha256).hexdigest()


def token(staff_id: str, role: str) -> str:
    payload = f"{staff_id}.{role}"
    return f"{payload}.{_sign(payload)}"


def password_ok(given: str | None) -> bool:
    if PASSWORD:
        return secrets.compare_digest((given or "").encode("utf-8"), PASSWORD.encode("utf-8"))
    return not HOSTED


def sign_in(conn: sqlite3.Connection, login: str, password: str | None) -> sqlite3.Row | None:
    """The STAFF row for this username and password, or None. The same answer for an unknown name and a wrong password."""
    row = conn.execute("SELECT staff_id, full_name, role FROM STAFF WHERE login_account = ?", ((login or "").strip(),)).fetchone()
    if not password_ok(password):
        return None
    return row


def session(conn: sqlite3.Connection, cookie: str | None) -> dict | None:
    """{staff_id, staff_role} from a valid cookie whose role still matches STAFF; otherwise None."""
    staff_id, _, rest = (cookie or "").partition(".")
    role, _, signature = rest.partition(".")
    if not signature or not hmac.compare_digest(signature, _sign(f"{staff_id}.{role}")):
        return None
    row = conn.execute("SELECT role FROM STAFF WHERE staff_id = ?", (staff_id,)).fetchone()
    if row is None or row["role"] != role:
        return None
    return {"staff_id": staff_id, "staff_role": role}
