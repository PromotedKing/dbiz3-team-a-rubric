"""T007 — US-2 #2, #3; FR-005, FR-007, BR-011, BR-012 (S-026 page)."""
from tests.alr_status_helpers import RPT002, RPT010, chatbot_case, report_id


def test_resolved_report_with_response(client, db, user_id):
    lan = user_id("tci-000123")
    page = client.get(f"/m/{lan}/reports/{report_id(db, RPT002)}").text
    for text in ("BC-0926-015", "Resolved", "Blood pressure", "Above threshold", "150/95 mmHg",
                 "26/09/2026 · 20:15", "26/09/2026 · 20:17", "Severe headache / dizziness / blurred vision",
                 "Handling progress", "Nurse Trần Thị B", "No doctor escalation needed",
                 "Response from Nurse Trần Thị B", "Emergency call"):
        assert text in page, text
    assert "Safety note" not in page
    assert "alert" not in page.lower()


def test_report_without_response_shows_safety_note(client, db, user_id):
    page = client.get(f"/m/{user_id('tci-000123')}/reports/{report_id(db, RPT010)}").text
    assert "Safety note" in page and "Response from" not in page
    assert page.count('data-step-state="pending"') == 3


def test_chatbot_case_page(client, db, user_id):
    lan = user_id("tci-000123")
    page = client.get(f"/m/{lan}/cases/{chatbot_case(db, lan)}").text
    assert "Chatbot" in page and "Your question:" in page
    assert "I have had a little bleeding since this morning, is that normal?" in page
    assert "Handling progress" in page and "Safety note" in page
