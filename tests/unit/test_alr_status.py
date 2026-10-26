"""T004 — ALR BR-012 (progress), BR-011 (Safety note), FR-007 (response) on S-026."""
from mb360.alr import status
from tests.alr_status_helpers import RPT002, RPT008, RPT010, case_of_code


def steps(db, code):
    return {s["status"]: s for s in status.progress(db, case_of_code(db, code))}


def test_c1_progress_with_skipped_escalation(db):
    s = steps(db, RPT002)
    assert list(s) == ["Not viewed", "Viewed", "Escalated to doctor", "Resolved"]
    assert (s["Not viewed"]["state"], s["Not viewed"]["note"], s["Not viewed"]["at"]) == ("done", "Report submitted", "26/09/2026 · 20:17")
    assert (s["Viewed"]["state"], s["Viewed"]["actor"], s["Viewed"]["at"]) == ("done", "Nurse Trần Thị B", "26/09/2026 · 20:25")
    assert (s["Escalated to doctor"]["state"], s["Escalated to doctor"]["note"]) == ("skipped", "No doctor escalation needed")
    assert (s["Resolved"]["state"], s["Resolved"]["at"]) == ("done", "26/09/2026 · 20:40")


def test_not_viewed_case_has_pending_steps(db):
    s = steps(db, RPT010)
    assert s["Not viewed"]["state"] == "done"
    assert [s[k]["state"] for k in ("Viewed", "Escalated to doctor", "Resolved")] == ["pending"] * 3


def test_escalated_then_closed_by_a_doctor(db):
    s = steps(db, RPT008)
    assert all(v["state"] == "done" for v in s.values())
    assert s["Resolved"]["actor"] == "Dr. Nguyễn Văn A"


def test_response_hides_the_safety_note(db):
    c1 = case_of_code(db, RPT002)
    resp = status.responses(db, c1)
    assert len(resp) == 1 and resp[0]["heading"] == "Response from Nurse Trần Thị B" and resp[0]["text"]
    assert status.show_safety_note(db, c1) is False


def test_no_response_shows_the_safety_note(db):
    c = case_of_code(db, RPT010)
    assert status.responses(db, c) == []
    assert status.show_safety_note(db, c) is True
