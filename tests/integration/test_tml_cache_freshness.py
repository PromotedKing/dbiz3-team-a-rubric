"""Regression test added in Step 6 (build log entry 28): the week cache (FR-004) must not show stale indicators
after a write made on another screen."""
from tests.integration.helpers import bp_form


def test_timeline_shows_a_report_made_after_it_was_cached(client, user_id):
    u09 = user_id("tci-000131")
    today = "/m/%s/timeline/day/2026-09-27" % u09
    client.get(f"/m/{u09}/timeline")
    assert "141/88 mmHg" not in client.get(today).text
    client.post(f"/m/{u09}/report", data=bp_form(141, 88, ["No symptoms"]))
    assert "141/88 mmHg" in client.get(today).text
