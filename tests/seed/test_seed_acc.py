"""T002 — ACC facts of the seed (data/seed/seed-report.md)."""
from datetime import datetime, timedelta

from mb360 import db as dbmod


def test_accounts_consent_preferences():
    conn = dbmod.build()
    users = conn.execute("SELECT user_id, tci_account_ref, sex, role FROM USER_ACCOUNT").fetchall()
    assert {u["tci_account_ref"] for u in users} == {"tci-000123", "tci-000126", "tci-000128", "tci-000133"}
    assert {(u["sex"], u["role"]) for u in users} == {("Female", "Mother")}   # BR-007, D-71
    for u in users:
        assert conn.execute("SELECT COUNT(*) FROM CONSENT_RECORD WHERE user_id = ?", (u["user_id"],)).fetchone()[0] >= 1
        assert conn.execute("SELECT COUNT(*) FROM NOTIFICATION_PREFERENCE WHERE user_id = ?", (u["user_id"],)).fetchone()[0] == 1


def test_seed_show_accounts_have_due_dates():
    conn = dbmod.build()
    assert conn.execute("SELECT COUNT(*) FROM PREGNANCY_PROFILE WHERE edd IS NOT NULL").fetchone()[0] == 4


def test_ordinary_seed_sessions_last_12_hours():
    """Two ordinary sessions last 12 hours; U06 ends at the fixed seed clock."""
    conn = dbmod.build()
    fmt = "%Y-%m-%d %H:%M"
    spans = [datetime.strptime(s[1], fmt) - datetime.strptime(s[0], fmt) for s in conn.execute("SELECT created_at, expires_at FROM SESSION")]
    assert sum(1 for d in spans if d == timedelta(hours=12)) == 2
