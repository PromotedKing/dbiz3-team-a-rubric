"""T009 — ALR BR-004, BR-005: threshold check from THRESHOLD_RULE (never hard-coded)."""
import pytest

from mb360.alr import thresholds


@pytest.mark.parametrize("value, label", [
    ("140/90", "Above threshold"),   # exactly on the threshold (>=, D-14)
    ("139/89", "Normal"),
    ("140/80", "Above threshold"),   # systolic alone
    ("120/90", "Above threshold"),   # diastolic alone
    ("120/80", "Normal"),
])
def test_blood_pressure(db, value, label):
    assert thresholds.evaluate(db, "Blood pressure", value) == label


@pytest.mark.parametrize("ctx, at, below", [("fasting", "5.3", "5.2"), ("post_1h", "7.8", "7.7"), ("post_2h", "6.7", "6.6")])
def test_blood_glucose_by_timing(db, ctx, at, below):
    assert thresholds.evaluate(db, "Blood glucose", at, ctx) == "Above threshold"
    assert thresholds.evaluate(db, "Blood glucose", below, ctx) == "Normal"


@pytest.mark.parametrize("level, label", [("Negative", "Normal"), ("Trace", "Normal"), ("1+", "Above threshold"),
                                          ("2+", "Above threshold"), ("3+", "Above threshold")])
def test_urine_protein(db, level, label):
    assert thresholds.evaluate(db, "Urine protein", level) == label


def test_symptom_report_is_not_assessed(db):
    assert thresholds.evaluate(db, "Symptom", None) == "Not assessed"


def test_thresholds_are_read_from_threshold_rule(db):
    """AGENTS.md hard rule 7: change the configuration, the result changes."""
    db.execute("UPDATE THRESHOLD_RULE SET threshold_values = '150' WHERE metric = 'Blood pressure' AND component = 'systolic'")
    assert thresholds.evaluate(db, "Blood pressure", "145/80") == "Normal"
    assert thresholds.evaluate(db, "Blood pressure", "150/80") == "Above threshold"
