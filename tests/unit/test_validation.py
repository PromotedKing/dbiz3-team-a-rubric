"""T010 — ALR FR-013, FR-014, BR-017 (form rules of S-025A). No numeric range: ALR §10 Q9 is open."""
import pytest

from mb360.alr import validation

ACTIVE = {"Blood pressure", "Blood glucose", "Urine protein"}


def form(**kw):
    base = {"metric": "Blood pressure", "systolic": "120", "diastolic": "80", "value": "", "level": "",
            "glucose_context": "", "measured_at": "2026-09-27T09:00", "symptoms": ["No symptoms"],
            "other_symptom_text": "", "note": ""}
    base.update(kw)
    return base


def test_valid_blood_pressure_form_has_no_error():
    assert validation.validate(form(), ACTIVE) == {}


def test_blood_glucose_needs_measurement_timing():
    errors = validation.validate(form(metric="Blood glucose", value="5.0", glucose_context=""), ACTIVE)
    assert "glucose_context" in errors


def test_at_least_one_symptom_is_required():
    errors = validation.validate(form(symptoms=[]), ACTIVE)
    assert "symptoms" in errors


def test_no_symptoms_excludes_other_items():
    errors = validation.validate(form(symptoms=["No symptoms", "Palpitations"]), ACTIVE)
    assert "symptoms" in errors


def test_other_needs_its_text():
    errors = validation.validate(form(symptoms=["Other"], other_symptom_text=""), ACTIVE)
    assert "other_symptom_text" in errors


def test_other_text_limit_is_100_characters():
    assert validation.validate(form(symptoms=["Other"], other_symptom_text="x" * 100), ACTIVE) == {}
    assert "other_symptom_text" in validation.validate(form(symptoms=["Other"], other_symptom_text="x" * 101), ACTIVE)


def test_symptom_outside_the_d73_list_is_rejected():
    assert "symptoms" in validation.validate(form(symptoms=["Headache"]), ACTIVE)


@pytest.mark.parametrize("systolic, diastolic", [("", "80"), ("120", ""), ("abc", "80"), ("120.5", "80")])
def test_blood_pressure_needs_two_whole_numbers(systolic, diastolic):
    assert validation.validate(form(systolic=systolic, diastolic=diastolic), ACTIVE)


def test_urine_protein_level_must_be_on_the_scale():
    assert validation.validate(form(metric="Urine protein", level="1+"), ACTIVE) == {}
    assert "level" in validation.validate(form(metric="Urine protein", level="4+"), ACTIVE)


def test_measured_at_is_required():
    assert "measured_at" in validation.validate(form(measured_at=""), ACTIVE)


def test_metric_must_be_in_active_instructions_or_symptom_mode():
    """ALR BR-006 / FR-011."""
    assert "metric" in validation.validate(form(), {"Blood glucose"})
    assert validation.validate(form(metric="Symptom", systolic="", diastolic="", symptoms=["Palpitations"]), set()) == {}


@pytest.mark.xfail(reason="ALR Q9 — valid ranges pending Client/SME (D-16); no range is invented", strict=True)
def test_valid_range_blocks_typing_errors():
    assert "systolic" in validation.validate(form(systolic="999"), ACTIVE)
