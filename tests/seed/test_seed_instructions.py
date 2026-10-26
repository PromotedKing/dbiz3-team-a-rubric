"""T002 — Watch-Flag and visit-result facts of the seed (data/seed/seed-report.md)."""
from collections import Counter

from mb360 import db as dbmod


def test_watch_flags():
    conn = dbmod.build()
    rows = conn.execute("SELECT user_id, metric, active, template_id, custom_text FROM WATCH_FLAG").fetchall()
    assert len(rows) == 9
    assert sum(r["active"] for r in rows) == 8
    active = Counter((r["user_id"], r["metric"]) for r in rows if r["active"])
    assert max(active.values()) == 1                                        # DM-21 default
    u04 = conn.execute("SELECT user_id FROM USER_ACCOUNT WHERE tci_account_ref = 'tci-000126'").fetchone()[0]
    w07 = [r for r in rows if r["user_id"] == u04][0]
    assert w07["template_id"] is None and w07["custom_text"] is None         # W07: no guidance (BR-013)


def test_seed_already_holds_visit_result_notifications():
    conn = dbmod.build()
    assert conn.execute("SELECT COUNT(*) FROM NOTIFICATION WHERE type = 'Visit result' AND visit_id IS NOT NULL").fetchone()[0] >= 1
