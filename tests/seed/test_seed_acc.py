"""T002 — ACC facts of the seed (data/seed/seed-report.md)."""
from datetime import datetime, timedelta

from mb360 import db as dbmod


def test_accounts_consent_preferences():
    conn = dbmod.build()
    users = conn.execute("SELECT user_id, sex, role FROM USER_ACCOUNT").fetchall()
    assert len(users) == 12 and {(u["sex"], u["role"]) for u in users} == {("Female", "Mother")}   # BR-007, D-71; U11/U12 demo cases
    for u in users:
        assert conn.execute("SELECT COUNT(*) FROM CONSENT_RECORD WHERE user_id = ?", (u["user_id"],)).fetchone()[0] >= 1
        assert conn.execute("SELECT COUNT(*) FROM NOTIFICATION_PREFERENCE WHERE user_id = ?", (u["user_id"],)).fetchone()[0] == 1


def test_u07_has_no_due_date():
    conn = dbmod.build()
    u07 = conn.execute("SELECT user_id FROM USER_ACCOUNT WHERE tci_account_ref = 'tci-000129'").fetchone()[0]
    assert conn.execute("SELECT COUNT(*) FROM PREGNANCY_PROFILE WHERE user_id = ?", (u07,)).fetchone()[0] == 0


def test_ordinary_seed_sessions_last_12_hours():
    """7 of the 10 seed sessions last 12 hours; U06, U07 and U08 are edge cases (long, one minute, closed early)."""
    conn = dbmod.build()
    fmt = "%Y-%m-%d %H:%M"
    spans = [datetime.strptime(s[1], fmt) - datetime.strptime(s[0], fmt) for s in conn.execute("SELECT created_at, expires_at FROM SESSION")]
    assert sum(1 for d in spans if d == timedelta(hours=12)) == 7
