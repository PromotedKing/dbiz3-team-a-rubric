"""T011 — ALR BR-008 routing and BR-002 (only above threshold leads to the Metric alert)."""
import pytest

from mb360.alr import routing


@pytest.mark.parametrize("symptoms", [["No symptoms"], ["Palpitations"]])
def test_above_threshold_goes_to_metric_alert(symptoms):
    assert routing.route("Above threshold", symptoms) == ("S-028", "Metric report")


def test_normal_with_symptom_goes_to_report_status():
    assert routing.route("Normal", ["Vaginal bleeding"]) == ("S-026", "Symptom")


def test_normal_without_symptoms_goes_back_to_instructions_without_case():
    assert routing.route("Normal", ["No symptoms"]) == ("S-027", None)


def test_symptom_report_goes_to_report_status():
    assert routing.route("Not assessed", ["Absence of fetal movement"]) == ("S-026", "Symptom")
