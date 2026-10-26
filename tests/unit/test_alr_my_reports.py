"""T003 — ALR FR-002, FR-003, BR-005, BR-009 (rows of S-029 "My reports")."""
import pytest

from mb360.alr import my_reports
from tests.alr_status_helpers import RPT001, RPT002, RPT010, report_id


def test_lan_rows_newest_first(db, user_id):
    rows = my_reports.list_rows(db, user_id("tci-000123"))
    assert len(rows) == 4
    times = [r["sent_at"] for r in rows]
    assert times == sorted(times, reverse=True)


def test_report_rows(db, user_id):
    rows = {r.get("report_id"): r for r in my_reports.list_rows(db, user_id("tci-000123"))}
    normal = rows[report_id(db, RPT001)]
    assert (normal["label"], normal["status"], normal["case_id"]) == ("Normal", None, None)   # "No action needed"
    above = rows[report_id(db, RPT002)]
    assert (above["title"], above["label"], above["value"], above["status"]) == ("Blood pressure", "Above threshold", "150/95 mmHg", "Resolved")
    symptom = rows[report_id(db, RPT010)]
    assert (symptom["title"], symptom["label"], symptom["value"]) == ("Symptom", "Not assessed", None)
    assert "Severe headache / dizziness / blurred vision" in symptom["symptoms"]


def test_chatbot_row(db, user_id):
    chat = [r for r in my_reports.list_rows(db, user_id("tci-000123")) if r["kind"] == "chatbot"]
    assert len(chat) == 1
    assert (chat[0]["title"], chat[0]["label"], chat[0]["status"]) == ("Chatbot", None, "Not viewed")
    assert chat[0]["question"].startswith("I have had a little bleeding")


@pytest.mark.parametrize("status, n", [("Resolved", 1), ("Not viewed", 2), ("Viewed", 0), (None, 4)])
def test_status_filter(db, user_id, status, n):
    rows = my_reports.list_rows(db, user_id("tci-000123"), status=status)
    assert len(rows) == n
    if status:
        assert all(r["status"] == status for r in rows)    # "No action needed" rows only under All


@pytest.mark.parametrize("kind, n", [("Blood pressure", 2), ("Symptom", 1), ("Chatbot", 1), ("Blood glucose", 0)])
def test_type_filter(db, user_id, kind, n):
    assert len(my_reports.list_rows(db, user_id("tci-000123"), type_=kind)) == n
