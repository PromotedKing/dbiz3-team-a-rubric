"""T007 — US-2 #2, #3; FR-005, FR-007, BR-011, BR-012 (S-026 page)."""
from tests.alr_status_helpers import RPT002, RPT010, chatbot_case, report_id
from tests.integration.helpers import vi


def test_resolved_report_with_response(client, db, user_id):
    lan = user_id("tci-000123")
    page = client.get(f"/m/{lan}/reports/{report_id(db, RPT002)}").text
    for text in ("BC-0926-015", vi("Resolved"), vi("Blood pressure"), vi("Above threshold"), "150/95 mmHg",
                 "26/09/2026 · 20:15", "26/09/2026 · 20:17", vi("Severe headache / dizziness / blurred vision"),
                 vi("Handling progress"), vi("Nurse {name}", name="Trần Thị B"), vi("No doctor escalation needed"),
                 vi("Response from Nurse {name}", name="Trần Thị B"), vi("Emergency call")):
        assert text in page, text
    assert vi("Safety note") not in page
    assert "alert" not in page.lower()


def test_report_without_response_shows_safety_note(client, db, user_id):
    page = client.get(f"/m/{user_id('tci-000123')}/reports/{report_id(db, RPT010)}").text
    assert vi("Safety note") in page and "data-response" not in page
    assert page.count('data-step-state="pending"') == 3


def test_chatbot_case_page(client, db, user_id):
    lan = user_id("tci-000123")
    page = client.get(f"/m/{lan}/cases/{chatbot_case(db, lan)}").text
    assert vi("Chatbot") in page and vi("Your question:") in page
    assert "I have had a little bleeding since this morning, is that normal?" in page
    assert vi("Handling progress") in page and vi("Safety note") in page
