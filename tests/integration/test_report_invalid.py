"""T016 — US-1 scenario 7; ALR BR-017: no symptom selected -> not submitted, error under the symptom field."""
from .helpers import bp_form, counts


def test_no_symptom_selected_is_rejected_and_nothing_is_stored(client, db, user_id):
    u09 = user_id("tci-000126")
    before = counts(db)
    r = client.post(f"/m/{u09}/report", data=bp_form(150, 95, []))
    assert r.status_code == 422
    # The error is shown at the symptom field; its wording is still open on S-025A, so only its place is checked.
    assert 'data-error-for="symptoms"' in r.text
    assert counts(db) == before
