"""T002 — HLT US-3 #1 – #3, US-4 #1 – #4 (S-027, S-025 pages)."""
from tests.integration.helpers import bp_form, vi


def test_links_to_the_history(client, user_id):
    lan = user_id("tci-000123")
    for path in ("health", "home", "instructions"):
        assert f'/m/{lan}/history' in client.get(f"/m/{lan}/{path}").text, path


def test_history_page(client, user_id):
    lan = user_id("tci-000123")
    client.post(f"/m/{lan}/report", data=bp_form(150, 95, ["No symptoms"]))
    page = client.get(f"/m/{lan}/history", params={"metric": "Blood pressure"}).text
    for t in (vi("Metric history"), vi("Average"), vi("Lowest"), vi("Highest"), "150/95 mmHg", vi("Above threshold"),
              vi("Doctor-assigned"), vi("Threshold {value}", value="140/90 mmHg"), "<svg", "<polyline"):
        assert t in page, t
    assert 'value="2026-08-28"' in page and 'value="2026-09-27"' in page       # default range
    assert "alert" not in page.lower() and vi("Alert") not in page


def test_group1_page_has_no_threshold(client, user_id):
    lan = user_id("tci-000123")
    page = client.get(f"/m/{lan}/history", params={"metric": "Weight"}).text
    assert vi("Self-entered") in page and "57.0 kg" in page
    assert vi("Normal") not in page and vi("Above threshold") not in page and "data-line" not in page


def test_fetal_heart_rate_page_has_reference_lines_and_no_label(client, user_id):
    lan = user_id("tci-000123")
    page = client.get(f"/m/{lan}/history", params={"metric": "Fetal heart rate"}).text
    assert 'data-line="reference"' in page and vi("Reference range {value}", value="110–160 bpm") in page
    assert vi("Normal") not in page and vi("Above threshold") not in page


def test_date_filter_and_empty_state(client, user_id):
    lan = user_id("tci-000123")
    page = client.get(f"/m/{lan}/history", params={"metric": "Blood pressure", "from": "2020-01-01", "to": "2020-01-31"}).text
    assert vi("No data for this period.") in page and "<polyline" not in page and vi("Average") not in page


def test_invalid_range_shows_a_field_error(client, user_id):
    page = client.get(f"/m/{user_id('tci-000123')}/history", params={"from": "2026-09-27", "to": "2026-09-01"})
    assert page.status_code == 200 and 'data-error-for="from"' in page.text


def test_bad_date_text_falls_back_to_the_default_range(client, user_id):
    page = client.get(f"/m/{user_id('tci-000123')}/history", params={"from": "not-a-date"})
    assert page.status_code == 200 and 'value="2026-08-28"' in page.text


def test_glucose_context_selector(client, user_id):
    lan = user_id("tci-000123")
    page = client.get(f"/m/{lan}/history", params={"metric": "Blood glucose"}).text
    assert 'name="context"' in page and vi("Fasting") in page
    assert 'name="context"' not in client.get(f"/m/{lan}/history", params={"metric": "Weight"}).text


def test_history_never_edits_a_value(client, user_id):
    page = client.get(f"/m/{user_id('tci-000123')}/history", params={"metric": "Blood pressure"}).text
    assert 'method="post"' not in page                                         # BR-001


def test_instruction_cards_show_doctor_date_latest_and_history(client, user_id):
    lan = user_id("tci-000123")
    client.post(f"/m/{lan}/report", data=bp_form(150, 95, ["No symptoms"]))
    page = client.get(f"/m/{lan}/instructions").text
    for t in (vi("Doctor-assigned"), "150/95 mmHg", vi("Above threshold"), vi("None yet"), vi("View metric history"),
              vi("+ Report metric"), vi("+ Report symptoms"), f'/m/{lan}/history?metric=Blood%20pressure'):
        assert t in page, t
    assert vi("Weight") not in page and vi("Temperature") not in page          # US-3 #3: no group 1


def test_no_instructions_state(client, user_id):
    page = client.get(f"/m/{user_id('tci-000128')}/instructions").text
    assert vi("Your doctor has not given you any instructions yet.") in page and vi("+ Report symptoms") in page
