"""T002 — HLT facts of the seed (checked with queries before writing — build log entry 21)."""
from mb360 import db as dbmod


def _lan(conn):
    return conn.execute("SELECT user_id FROM USER_ACCOUNT WHERE tci_account_ref = 'tci-000123'").fetchone()[0]


def test_lan_latest_visit():
    conn = dbmod.build()
    lan = _lan(conn)
    visit = conn.execute("SELECT visit_id, visit_date FROM VISIT WHERE user_id = ? ORDER BY visit_date DESC LIMIT 1", (lan,)).fetchone()
    assert visit["visit_date"] == "2026-09-15"
    values = {r["metric"]: r["value"] for r in conn.execute(
        "SELECT metric, value FROM HEALTH_METRIC_RECORD WHERE visit_id = ? AND source = 'From visit'", (visit["visit_id"],))}
    assert values == {"Blood pressure": "132/84", "Fetal heart rate": "145", "Weight": "56.5", "Urine protein": "Negative"}


def test_lan_latest_self_entered():
    conn = dbmod.build()
    rows = conn.execute("""SELECT metric, value FROM HEALTH_METRIC_RECORD h
                           WHERE user_id = ? AND source = 'Self-entered' AND metric_group = 'Group 1'
                             AND measured_at = (SELECT MAX(measured_at) FROM HEALTH_METRIC_RECORD x
                                                WHERE x.user_id = h.user_id AND x.metric = h.metric AND x.source = 'Self-entered')""",
                        (_lan(conn),)).fetchall()
    assert {r["metric"]: r["value"] for r in rows} == {"Weight": "57.0", "Temperature": "36.8", "Heart rate": "82", "Sleep": "22:30-06:00"}


def test_reference_range_and_group1_sources():
    conn = dbmod.build()
    rows = conn.execute("SELECT metric, threshold_values, unit FROM THRESHOLD_RULE WHERE purpose = 'Display only'").fetchall()
    assert [tuple(r) for r in rows] == [("Fetal heart rate", "110–160", "bpm")]
    assert conn.execute("SELECT COUNT(*) FROM HEALTH_METRIC_RECORD WHERE metric_group = 'Group 1' AND source = 'Doctor-assigned'").fetchone()[0] == 0
