"""CLI case handling: responsible doctor (D-68), status machine (BR-002, D-43) and permissions (BR-004)."""
import sqlite3
from datetime import date


def responsible_doctor(conn: sqlite3.Connection, user_id: str, today: date) -> str | None:
    """Active PATIENT_ASSIGNMENT: valid_from <= today <= valid_to (inclusive, spec-CLI §10 Q15), or no valid_to."""
    row = conn.execute(
        """SELECT doctor_id FROM PATIENT_ASSIGNMENT
           WHERE user_id = ? AND valid_from <= ? AND (valid_to IS NULL OR valid_to >= ?)""",
        (user_id, today.isoformat(), today.isoformat()),
    ).fetchone()
    return row[0] if row else None
