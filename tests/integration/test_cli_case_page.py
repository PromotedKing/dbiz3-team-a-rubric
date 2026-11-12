"""T012 — CLI FR-003, FR-007, FR-008, FR-010, BR-009, CLI-01 (S-064 content)."""
from tests.cli_helpers import RPT002, case_by_code
from tests.integration.helpers import vi


def test_report_block_and_profile(client, db, staff_id, boundary_case, user_id):
    db.execute("UPDATE PATIENT_CLINICAL_PROFILE SET blood_type = ?, allergies = ? WHERE user_id = ?",
               ("O−", "Seafood", user_id("tci-000126")))
    page = client.get(f"/staff/{staff_id('Trần Thị B')}/cases/{boundary_case}").text
    for text in ("Phạm Ngọc Mai", "TC-00126", vi("Week {n}", n=31), "29/11/2026", "O−", "Seafood",
                 "140/90 mmHg", vi("Above threshold"), "27/09/2026 · 07:00", vi("Doctor-assigned"), vi("Not viewed")):
        assert text in page, text


def test_metric_history_has_no_self_entered_values(client, db, staff_id):
    page = client.get(f"/staff/{staff_id('Trần Thị B')}/cases/{case_by_code(db, RPT002)}").text
    assert vi("Metric history — {metric}", metric=vi("Blood pressure")) in page and "140/90 mmHg" in page          # threshold from THRESHOLD_RULE
    assert vi("From visit") in page
    assert vi("Self-entered") not in page and "57.0" not in page            # Lan's self-entered weight (CLI-01)


def test_chatbot_case_shows_the_whole_conversation(client, db, staff_id):
    case = db.execute("SELECT case_id, chat_message_id FROM CARE_CASE WHERE case_source = 'Chatbot' AND status = 'Not viewed'").fetchone()
    conv = db.execute("SELECT conversation_id FROM CHAT_MESSAGE WHERE message_id = ?", (case["chat_message_id"],)).fetchone()[0]
    texts = [r[0] for r in db.execute("SELECT text FROM CHAT_MESSAGE WHERE conversation_id = ? ORDER BY sent_at", (conv,))]
    assert len(texts) >= 2
    page = client.get(f"/staff/{staff_id('Trần Thị B')}/cases/{case['case_id']}").text
    positions = [page.find(t) for t in texts]
    assert all(p >= 0 for p in positions) and positions == sorted(positions)
    assert "data-escalated-question" in page


def test_no_alert_word_on_the_clinical_web(client, db, staff_id, boundary_case):
    nurse = staff_id("Trần Thị B")
    for url in (f"/staff/{nurse}/cases", f"/staff/{nurse}/cases/{boundary_case}"):
        assert "alert" not in client.get(url).text.lower(), url
