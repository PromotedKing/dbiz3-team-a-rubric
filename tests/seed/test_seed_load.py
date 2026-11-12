"""T004 — the seed loads as data/seed/seed-report.md states (Session 5 data package)."""
from mb360 import db as dbmod


def test_seed_loads_26_tables_and_141_rows():
    conn = dbmod.build()
    tables = [r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type = 'table'")]
    assert len(tables) == 26
    total = sum(conn.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0] for t in tables)
    assert total == 141


def test_foreign_keys_are_on():
    conn = dbmod.build()
    assert conn.execute("PRAGMA foreign_keys").fetchone()[0] == 1
    assert conn.execute("PRAGMA foreign_key_check").fetchall() == []


def test_rpt004_above_threshold_has_escalated_case_c4():
    """seed-report.md, scenario "ALR": 145/92 RPT-004 -> C4 (Metric report case)."""
    conn = dbmod.build()
    row = conn.execute(
        """SELECT h.value, c.case_source, c.status
           FROM METRIC_REPORT r
           JOIN HEALTH_METRIC_RECORD h ON h.record_id = r.health_metric_record_id
           JOIN CARE_CASE c ON c.metric_report_id = r.report_id
           WHERE r.report_code = 'BC-0926-011'"""
    ).fetchone()
    assert row is not None
    assert row["value"] == "145/92"
    assert row["case_source"] == "Metric report"
    assert row["status"] == "Escalated to doctor"
