"""D-104 / S-061 SR-006: the nurse's "Priority" order, the "Waiting" column and the count on the nurse's home."""
from datetime import datetime

from mb360.cli import queue
from tests.cli_helpers import NOW


def row(status, label, submitted_at):
    return {"status": status, "label": label, "submitted_at": submitted_at}


def test_priority_puts_above_threshold_not_viewed_first_then_longest_waiting():
    rows = [row("Viewed", "Normal", "2026-09-26 08:00"),
            row("Not viewed", "Normal", "2026-09-27 08:00"),
            row("Not viewed", "Above threshold", "2026-09-27 09:00"),
            row("Escalated to doctor", "Above threshold", "2026-09-25 07:00"),
            row("Resolved", "Normal", "2026-09-20 07:00")]
    ordered = queue.priority_order(rows)
    assert [(r["status"], r["label"]) for r in ordered] == [
        ("Not viewed", "Above threshold"),          # above threshold AND not viewed come first
        ("Escalated to doctor", "Above threshold"),  # then every other open case, longest waiting first
        ("Viewed", "Normal"),
        ("Not viewed", "Normal"),
        ("Resolved", "Normal")]                       # resolved last


def test_waiting_is_calculated_and_empty_for_resolved():
    assert queue.waiting("2026-09-27 07:45", "Not viewed", NOW) == {"days": 0, "hours": 2, "minutes": 15, "total": 135}
    assert queue.waiting("2026-09-25 09:00", "Viewed", NOW)["days"] == 2
    assert queue.waiting("2026-09-25 09:00", "Resolved", NOW) is None
    assert queue.waiting("2026-09-27 11:00", "Viewed", NOW)["total"] == 0       # never negative


def test_list_cases_sorts_by_priority_without_changing_the_set(db):
    newest, priority = queue.list_cases(db, None), queue.list_cases(db, None, sort="Priority")
    assert {r["case_id"] for r in newest} == {r["case_id"] for r in priority}
    assert all("waiting" in r for r in priority)
    assert all((r["waiting"] is None) == (r["status"] == "Resolved") for r in priority)
