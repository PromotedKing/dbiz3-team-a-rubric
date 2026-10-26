"""T004 — HLT FR-007, BR-003 (S-024 self-tracked metrics)."""
import pytest

from mb360.hlt import self_tracked
from tests.acc_helpers import NOW


def form(**kw):
    base = {"weight": "", "weight_at": "2026-09-27T09:00", "temperature": "", "temperature_at": "2026-09-27T09:00",
            "heart_rate": "", "heart_rate_at": "2026-09-27T09:00", "bedtime": "", "wakeup": ""}
    base.update(kw)
    return base


def counts(db):
    return {t: db.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
            for t in ("HEALTH_METRIC_RECORD", "METRIC_REPORT", "CARE_CASE", "NOTIFICATION")}


def test_save_writes_group1_records_only(db, user_id):
    lan = user_id("tci-000123")
    before = counts(db)
    self_tracked.save(db, lan, form(weight="57.4", temperature="36.9"), NOW)
    after = counts(db)
    assert {t: after[t] - before[t] for t in after} == {"HEALTH_METRIC_RECORD": 2, "METRIC_REPORT": 0, "CARE_CASE": 0, "NOTIFICATION": 0}
    rows = db.execute("SELECT * FROM HEALTH_METRIC_RECORD WHERE user_id = ? AND created_at = '2026-09-27 10:00' ORDER BY metric", (lan,)).fetchall()
    assert [(r["metric"], r["value"], r["unit"], r["metric_group"], r["source"], r["gestational_week"]) for r in rows] == \
        [("Temperature", "36.9", "°C", "Group 1", "Self-entered", 28), ("Weight", "57.4", "kg", "Group 1", "Self-entered", 28)]


def test_sleep_is_stored_as_bedtime_wakeup(db, user_id):
    lan = user_id("tci-000123")
    self_tracked.save(db, lan, form(bedtime="2026-09-26T22:00", wakeup="2026-09-27T06:30"), NOW)
    r = db.execute("SELECT * FROM HEALTH_METRIC_RECORD WHERE user_id = ? AND metric = 'Sleep' ORDER BY created_at DESC LIMIT 1", (lan,)).fetchone()
    assert (r["value"], r["unit"], r["measured_at"]) == ("22:00-06:30", None, "2026-09-27 06:30")


@pytest.mark.parametrize("kw, field", [
    ({"weight": "abc"}, "weight"),
    ({"weight": "57", "weight_at": ""}, "weight_at"),
    ({"temperature": "36.9", "temperature_at": "2026-09-27T11:00"}, "temperature_at"),   # after now (schema: measured <= created)
    ({"bedtime": "2026-09-26T22:00"}, "wakeup"),
    ({"bedtime": "2026-09-27T06:00", "wakeup": "2026-09-26T22:00"}, "wakeup"),
    ({}, "form"),                                                                         # nothing entered
])
def test_invalid_input_writes_nothing(db, user_id, kw, field):
    lan = user_id("tci-000123")
    before = counts(db)
    with pytest.raises(self_tracked.EntryError) as e:
        self_tracked.save(db, lan, form(**kw), NOW)
    assert field in e.value.errors
    assert counts(db) == before


@pytest.mark.xfail(reason="D-16 — valid ranges pending SME; no range is invented", strict=True)
def test_valid_range_blocks_typing_errors(db, user_id):
    with pytest.raises(self_tracked.EntryError):
        self_tracked.save(db, user_id("tci-000123"), form(weight="999"), NOW)
