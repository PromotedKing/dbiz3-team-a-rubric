"""T017 — US-1 scenarios 1 - 3; ALR FR-010 - FR-013, BR-006 (S-027 and S-025A)."""
from .helpers import bp_form, counts
from .helpers import vi


def test_instructions_page_lists_active_metrics_and_symptoms(client, user_id):
    u01 = user_id("tci-000123")
    page = client.get(f"/m/{u01}/instructions").text
    assert vi("Blood pressure") in page and vi("Blood glucose") in page
    assert vi("+ Report metric") in page and vi("+ Report symptoms") in page


def test_change_metric_lists_only_active_instructions_plus_symptom_mode(client, user_id):
    u01 = user_id("tci-000123")
    page = client.get(f"/m/{u01}/report", params={"metric": "Blood pressure"}).text
    assert 'value="Blood pressure"' in page and 'value="Blood glucose"' in page and 'value="Symptom"' in page
    assert 'value="Urine protein"' not in page


def test_inactive_instruction_does_not_count(client, user_id):
    u05 = user_id("tci-000127")  # W03 Urine protein active, W08 Blood pressure inactive
    page = client.get(f"/m/{u05}/report", params={"metric": "Urine protein"}).text
    assert 'value="Urine protein"' in page and 'value="Blood pressure"' not in page


def test_instruction_box_shown_for_a_metric_hidden_in_symptom_mode(client, user_id):
    u01 = user_id("tci-000123")
    note = "Measure twice a day, morning and evening"  # W01 note
    assert note in client.get(f"/m/{u01}/report", params={"metric": "Blood pressure"}).text
    assert note not in client.get(f"/m/{u01}/report", params={"metric": "Symptom"}).text


def test_threshold_card_comes_from_threshold_rule(client, db, user_id):
    u01, u05 = user_id("tci-000123"), user_id("tci-000127")
    assert "140/90 mmHg" in client.get(f"/m/{u01}/report", params={"metric": "Blood pressure"}).text
    assert "7.8 mmol/L" in client.get(f"/m/{u01}/report", params={"metric": "Blood glucose", "glucose_context": "post_1h"}).text
    assert "1+" in client.get(f"/m/{u05}/report", params={"metric": "Urine protein"}).text
    assert "data-threshold-card" not in client.get(f"/m/{u01}/report", params={"metric": "Symptom"}).text
    db.execute("UPDATE THRESHOLD_RULE SET threshold_values = '150' WHERE metric = 'Blood pressure' AND component = 'systolic'")
    assert "150/90 mmHg" in client.get(f"/m/{u01}/report", params={"metric": "Blood pressure"}).text


def test_mother_without_instructions_has_symptom_mode_only(client, db, user_id):
    u06 = user_id("tci-000128")
    page = client.get(f"/m/{u06}/instructions").text
    assert vi("+ Report symptoms") in page and vi("+ Report metric") not in page
    before = counts(db)
    r = client.post(f"/m/{u06}/report", data=bp_form(150, 95, ["No symptoms"]))
    assert r.status_code == 422 and counts(db) == before
