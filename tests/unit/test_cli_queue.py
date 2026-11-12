"""T008 — CLI FR-002, FR-020, BR-007 (queue rows of S-061)."""
import pytest

from mb360.cli import queue


def test_sorted_newest_first(db):
    rows = queue.list_cases(db)
    assert len(rows) == db.execute("SELECT COUNT(*) FROM CARE_CASE").fetchone()[0]
    times = [r["submitted_at"] for r in rows]
    assert times == sorted(times, reverse=True)


@pytest.mark.parametrize("status", ["Not viewed", "Viewed", "Escalated to doctor", "Resolved", None])
def test_filter_by_status(db, status, boundary_case, staff_id):
    from mb360.cli import actions
    from tests.cli_helpers import NOW

    if status == "Viewed":
        actions.mark_viewed(db, boundary_case, staff_id("Trần Thị B"), NOW)
    n = db.execute("SELECT COUNT(*) FROM CARE_CASE WHERE (? IS NULL OR status = ?)", (status, status)).fetchone()[0]
    assert n > 0
    rows = queue.list_cases(db, status)
    assert len(rows) == n
    assert status is None or {r["status"] for r in rows} == {status}


def test_labels_and_content(db, boundary_case):
    rows = {r["case_id"]: r for r in queue.list_cases(db)}
    by_source = lambda s: [r for r in rows.values() if r["case_source"] == s]
    rpt006 = rows[boundary_case]
    assert rpt006["value"] == "140/90 mmHg"
    assert (rpt006["label"], rpt006["content"]) == ("Above threshold", "Blood pressure")
    for r in by_source("Symptom") + by_source("Chatbot"):
        assert r["label"] == "Not assessed" and r["value"] is None
    symptom = next(r for r in by_source("Symptom") if "dizziness" in r["content"])
    assert "Severe headache / dizziness / blurred vision" in symptom["content"]


def test_chatbot_row_shows_the_question_and_the_case_time(db):
    rows = [r for r in queue.list_cases(db) if r["case_source"] == "Chatbot"]
    assert rows
    assert len(rows) == db.execute("SELECT COUNT(*) FROM CARE_CASE WHERE case_source = 'Chatbot'").fetchone()[0]
    for r in rows:
        case = db.execute("SELECT c.created_at, m.text FROM CARE_CASE c JOIN CHAT_MESSAGE m ON m.message_id = c.chat_message_id "
                          "WHERE c.case_id = ?", (r["case_id"],)).fetchone()
        assert (r["submitted_at"], r["content"]) == (case["created_at"], case["text"])


def test_doctor_badge_counts_escalated_cases_assigned_to_him(db, staff_id):
    assert queue.doctor_badge(db, staff_id("Nguyễn Văn A")) == 1
    assert queue.doctor_badge(db, staff_id("Phạm Quốc Dũng")) == 0
