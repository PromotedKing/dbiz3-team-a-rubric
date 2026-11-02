"""T001 — HLT FR-009 – FR-012, BR-003 – BR-005; S-027 cards (specs/010-hlt-history)."""
import uuid
from datetime import date

import pytest

from mb360.hlt import history
from tests.acc_helpers import NOW

FROM, TO = date(2026, 8, 1), date(2026, 8, 10)      # no seed record of Lan's in these days for the metrics used below


def add(db, uid, metric, value, day, unit=None, source="Doctor-assigned", group="Group 2", ctx=None):
    at = f"2026-08-{day:02d} 08:00"
    visit = db.execute("SELECT visit_id FROM VISIT WHERE user_id = ? LIMIT 1", (uid,)).fetchone()[0] if source == "From visit" else None
    db.execute("""INSERT INTO HEALTH_METRIC_RECORD (record_id, user_id, metric, metric_group, value, unit, glucose_context, measured_at, source, visit_id, gestational_week, created_at)
                  VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 20, ?)""", (str(uuid.uuid4()), uid, metric, group, value, unit, ctx, at, source, visit, at))


@pytest.fixture
def lan(db, user_id):
    uid = user_id("tci-000123")
    db.execute("DELETE FROM HEALTH_METRIC_RECORD WHERE user_id = ? AND measured_at >= '2026-08-01' AND measured_at < '2026-08-11' AND record_id NOT IN (SELECT health_metric_record_id FROM METRIC_REPORT WHERE health_metric_record_id IS NOT NULL)", (uid,))
    return uid


def test_default_range_is_the_last_30_days(db, lan):
    h = history.load(db, lan, "Blood pressure", None, None, None, NOW)
    assert (h["start"], h["end"]) == (date(2026, 8, 28), date(2026, 9, 27))


def test_rows_inside_the_range_newest_first(db, lan):
    add(db, lan, "Blood pressure", "120/80", 1, "mmHg")
    add(db, lan, "Blood pressure", "150/95", 10, "mmHg")
    add(db, lan, "Blood pressure", "118/70", 11, "mmHg")      # outside
    h = history.load(db, lan, "Blood pressure", FROM, TO, None, NOW)
    assert [r["value"] for r in h["rows"]] == ["150/95 mmHg", "120/80 mmHg"]
    assert [r["label"] for r in h["rows"]] == ["Above threshold", "Normal"]
    assert all(r["source"] == "Doctor-assigned" for r in h["rows"])          # BR-004


def test_blood_pressure_statistics_are_separate(db, lan):
    add(db, lan, "Blood pressure", "120/90", 1, "mmHg")
    add(db, lan, "Blood pressure", "140/70", 2, "mmHg")
    s = history.load(db, lan, "Blood pressure", FROM, TO, None, NOW)["stats"]
    assert (s["average"], s["lowest"], s["highest"]) == ("130/80", "120/70", "140/90")


def test_numeric_statistics(db, lan):
    add(db, lan, "Weight", "50.0", 1, "kg", "Self-entered", "Group 1")
    add(db, lan, "Weight", "51.0", 2, "kg", "Self-entered", "Group 1")
    s = history.load(db, lan, "Weight", FROM, TO, None, NOW)["stats"]
    assert (s["average"], s["lowest"], s["highest"]) == ("50.5", "50.0", "51.0")


@pytest.mark.parametrize("metric, value", [("Urine protein", "1+"), ("Sleep", "22:30-06:00")])
def test_no_statistics_for_urine_protein_and_sleep(db, lan, metric, value):    # HLT Q12 open
    group = "Group 2" if metric == "Urine protein" else "Group 1"
    add(db, lan, metric, value, 1, None, "Doctor-assigned" if group == "Group 2" else "Self-entered", group)
    assert history.load(db, lan, metric, FROM, TO, None, NOW)["stats"] is None


def test_group1_has_no_label_and_no_line(db, lan):                             # BR-003
    add(db, lan, "Heart rate", "82", 1, "bpm", "Self-entered", "Group 1")
    h = history.load(db, lan, "Heart rate", FROM, TO, None, NOW)
    assert h["rows"][0]["label"] is None and h["lines"] == []


def test_sleep_shows_the_duration(db, lan):
    add(db, lan, "Sleep", "22:30-06:00", 1, None, "Self-entered", "Group 1")
    h = history.load(db, lan, "Sleep", FROM, TO, None, NOW)
    assert h["rows"][0]["value"] == "7 h 30 min" and h["chart"]["series"][0]["points"]


def test_fetal_heart_rate_has_reference_lines_and_no_label(db, lan):           # BR-005; the schema refuses any other source
    add(db, lan, "Fetal heart rate", "145", 1, "bpm", "From visit", "Visit")
    h = history.load(db, lan, "Fetal heart rate", FROM, TO, None, NOW)
    assert [r["value"] for r in h["rows"]] == ["145 bpm"] and h["rows"][0]["label"] is None
    assert [(l["value"], l["kind"]) for l in h["lines"]] == [(110.0, "reference"), (160.0, "reference")]


def test_lines_come_from_threshold_rule(db, lan):                              # hard rule 7
    add(db, lan, "Blood pressure", "120/80", 1, "mmHg")
    assert [(l["value"], l["kind"]) for l in history.load(db, lan, "Blood pressure", FROM, TO, None, NOW)["lines"]] == [(140.0, "threshold"), (90.0, "threshold")]
    db.execute("UPDATE THRESHOLD_RULE SET threshold_values = '150' WHERE metric = 'Blood pressure' AND component = 'systolic'")
    assert 150.0 in [l["value"] for l in history.load(db, lan, "Blood pressure", FROM, TO, None, NOW)["lines"]]


def test_glucose_line_only_for_one_context_and_rows_labelled_by_their_own(db, lan):
    add(db, lan, "Blood glucose", "6.0", 1, "mmol/L", ctx="fasting")           # ≥ 5.3
    add(db, lan, "Blood glucose", "6.0", 2, "mmol/L", ctx="post_1h")           # < 7.8
    h = history.load(db, lan, "Blood glucose", FROM, TO, None, NOW)
    assert h["lines"] == []
    assert [r["label"] for r in h["rows"]] == ["Normal", "Above threshold"]
    one = history.load(db, lan, "Blood glucose", FROM, TO, "fasting", NOW)
    assert len(one["rows"]) == 1 and [l["value"] for l in one["lines"]] == [5.3]


def test_urine_protein_uses_the_dipstick_scale(db, lan):
    add(db, lan, "Urine protein", "Negative", 1)
    add(db, lan, "Urine protein", "2+", 2)
    h = history.load(db, lan, "Urine protein", FROM, TO, None, NOW)
    assert [r["label"] for r in h["rows"]] == ["Above threshold", "Normal"]
    assert [l["value"] for l in h["lines"]] == [2.0]                           # "1+" on the scale Negative, Trace, 1+, 2+, 3+


def test_invalid_range_and_no_data(db, lan):
    bad = history.load(db, lan, "Blood pressure", TO, FROM, None, NOW)
    assert bad["error"] and bad["rows"] == [] and bad["chart"] is None
    empty = history.load(db, lan, "Blood pressure", date(2020, 1, 1), date(2020, 1, 2), None, NOW)
    assert empty["rows"] == [] and empty["stats"] is None and empty["chart"] is None and not empty["error"]


def test_unknown_metric_falls_back(db, lan):
    assert history.load(db, lan, "x", FROM, TO, None, NOW)["metric"] == "Blood pressure"


def test_chart_geometry_stays_inside_the_box():
    c = history.chart([("a", [(0.0, 100.0), (1.0, 200.0)])], [{"value": 150.0, "kind": "threshold", "label": "150"}])
    pts = c["series"][0]["points"]
    assert len(pts) == 2 and pts[0]["x"] < pts[1]["x"] and pts[0]["y"] > pts[1]["y"]     # time goes right, higher values go up
    assert all(history.LEFT <= p["x"] <= history.RIGHT and history.TOP <= p["y"] <= history.BOTTOM for p in pts)
    assert pts[1]["y"] < c["lines"][0]["y"] < pts[0]["y"]
    single = history.chart([("a", [(0.0, 100.0)])], [])
    assert len(single["series"][0]["points"]) == 1


def test_instruction_cards(db, user_id):
    lan = user_id("tci-000123")
    cards = {c["metric"]: c for c in history.instruction_cards(db, lan)}
    bp = cards["Blood pressure"]
    assert bp["doctor"] and bp["flagged_at"] and bp["note"]
    assert bp["latest_value"] and bp["latest_label"] in ("Normal", "Above threshold") and bp["latest_at"]
    assert cards["Blood glucose"]["latest_value"] is None                       # "none yet"
