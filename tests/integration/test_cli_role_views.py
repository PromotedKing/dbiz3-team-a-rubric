"""D-103 – D-105, D-107 — one page per screen, the role view from STAFF.role (S-061 / S-061D, S-064 / S-064D)."""
import re

from mb360 import ui
from mb360.cli import actions, queue

from tests.cli_helpers import NOW


def case_order(page: str, staff: str) -> list[str]:
    return re.findall(rf'href="/staff/{staff}/cases/([0-9a-f-]{{36}})"', page)


# ---------------------------------------------------------------- S-061 nurse: Priority, Waiting, Home (n)

def test_nurse_list_opens_sorted_by_priority(client, db, staff_id, boundary_case):
    """D-104 / SR-006: the above-threshold case not yet viewed comes first, although it is the newest."""
    nurse = staff_id("Trần Thị B")
    page = client.get(f"/staff/{nurse}/cases").text
    assert 'data-sort="Priority"' in page and ui.t("Sort: Priority") in page
    order = case_order(page, nurse)
    assert order[0] == boundary_case
    rows = queue.list_cases(db, "Not viewed", viewer=nurse, order=queue.PRIORITY)
    rest = [r["waiting"] for r in rows[1:]]
    assert rest == sorted(rest, reverse=True)                    # then the longest wait first


def test_priority_puts_above_threshold_first_then_longest_wait(db, staff_id, boundary_case):
    rows = queue.list_cases(db, None, viewer=staff_id("Trần Thị B"), order=queue.PRIORITY)
    assert queue.is_priority(rows[0]) and not any(queue.is_priority(r) for r in rows[1:])
    open_rows = [r for r in rows[1:] if r["waiting"] is not None]
    assert [r["waiting"] for r in open_rows] == sorted((r["waiting"] for r in open_rows), reverse=True)
    assert all(r["waiting"] is None for r in rows[1 + len(open_rows):])     # resolved last, no waiting time


def test_nurse_can_switch_to_newest(client, db, staff_id, boundary_case):
    nurse = staff_id("Trần Thị B")
    page = client.get(f"/staff/{nurse}/cases", params={"status": "All", "sort": "Newest"}).text
    assert 'data-sort="Newest"' in page
    rows = queue.list_cases(db, None, viewer=nurse, order=queue.NEWEST)
    assert [r["submitted_at"] for r in rows] == sorted((r["submitted_at"] for r in rows), reverse=True)
    assert case_order(page, nurse) == [r["case_id"] for r in rows]
    assert case_order(page, nurse)[0] != boundary_case            # a newer chatbot case outranks it here


def test_waiting_column_shows_hours_and_minutes_and_a_dash_when_resolved(client, db, staff_id):
    nurse = staff_id("Trần Thị B")
    page = client.get(f"/staff/{nurse}/cases", params={"status": "All"}).text
    assert f"<th>{ui.t('Waiting')}</th>" in page
    # seed: symptom case of Lan submitted 27/09/2026 09:05, the clock is 10:00 → 55 minutes, no "0 h"
    assert ui.t("{m} min", m=55) in page and ui.t("{h} h {m} min", h=0, m=55) not in page
    # Mai's case submitted 26/09/2026 18:05 → hours past a day stay in hours, as the S-061 mockup ("26 h 47 min")
    assert ui.t("{h} h {m} min", h=15, m=55) in page
    assert '<td data-waiting="">—</td>' in page                    # a resolved case has no waiting time


def test_waiting_minutes_is_not_stored_and_has_no_limit():
    assert queue.waiting_minutes("2026-09-26 07:30", "Not viewed", NOW) == 26 * 60 + 30
    assert queue.waiting_minutes("2026-09-26 07:30", "Resolved", NOW) is None


def test_nurse_has_the_not_viewed_count_on_her_chip_and_next_to_the_case_list(client, db, staff_id):
    nurse = staff_id("Trần Thị B")
    n = db.execute("SELECT COUNT(*) FROM CARE_CASE WHERE status = 'Not viewed'").fetchone()[0]
    page = client.get(f"/staff/{nurse}/cases").text
    assert f"{ui.t('Not viewed')} ({n})" in page
    assert f"<span data-home-count>({n})</span>" in page
    assert 'class="bell' not in page                               # D-105


def test_nurse_list_has_no_responsible_doctor_column(client, staff_id):
    page = client.get(f"/staff/{staff_id('Trần Thị B')}/cases").text
    assert f"<th>{ui.t('Responsible doctor')}</th>" not in page


# ---------------------------------------------------------------- S-061D doctor

def test_doctor_keeps_the_bell_and_sorts_newest_only(client, staff_id):
    doctor = staff_id("Nguyễn Văn A")
    page = client.get(f"/staff/{doctor}/cases", params={"sort": "Priority"}).text
    assert 'class="bell' in page and f'href="/staff/{doctor}/notifications"' in page
    assert "data-sort=" not in page and ui.t("Sort: Newest") in page
    assert f"<th>{ui.t('Waiting')}</th>" not in page
    assert "data-home-count" not in page


def test_doctor_chip_counts_escalated_cases_and_shows_the_responsible_doctor(client, staff_id):
    doctor = staff_id("Nguyễn Văn A")
    page = client.get(f"/staff/{doctor}/cases").text
    assert f"{ui.t('Escalated to doctor')} (1)" in page            # seed: Mai's case, escalated to him
    assert f"<th>{ui.t('Responsible doctor')}</th>" in page
    assert ui.t("Dr. {name}", name="Nguyễn Văn A") + " · <strong>" + ui.t("Available") + "</strong>" in page
    assert "data-covering" not in page


def test_doctor_on_duty_sees_covering_for_an_away_doctor(client, db, staff_id, boundary_case):
    """S-061D #14 / BR-010: Hương's doctor (Phạm Quốc Dũng) is Away, Vũ Minh Hải is on duty."""
    on_duty = actions.escalate(db, boundary_case, staff_id("Trần Thị B"), NOW)
    assert on_duty == staff_id("Vũ Minh Hải")
    page = client.get(f"/staff/{on_duty}/cases").text
    assert boundary_case in page
    assert ui.t("Dr. {name}", name="Phạm Quốc Dũng") + " · <strong>" + ui.t("Away") + "</strong>" in page
    assert "data-covering" in page and ui.t("Covering") in page


# ---------------------------------------------------------------- S-064 / S-064D

def test_case_page_shows_the_responsible_doctor_line_for_both_roles(client, staff_id, boundary_case):
    line = ui.t("Dr. {name}", name="Phạm Quốc Dũng") + " · " + ui.t("Away")
    assert line in client.get(f"/staff/{staff_id('Trần Thị B')}/cases/{boundary_case}").text


def test_nurse_close_is_disabled_with_its_reason_on_a_must_escalate_case(client, staff_id, boundary_case):
    """S-064 #17 (BR-012, D-98)."""
    page = client.get(f"/staff/{staff_id('Trần Thị B')}/cases/{boundary_case}").text
    assert "data-close-disabled" in page and ui.t("This case must be escalated to a doctor") in page
    assert f'/cases/{boundary_case}/close"' not in page


def test_nurse_sees_the_medicine_hint_under_the_guidance(client, staff_id, boundary_case):
    """S-064 #18A (BR-013, D-99)."""
    page = client.get(f"/staff/{staff_id('Trần Thị B')}/cases/{boundary_case}").text
    assert "data-medicine-hint" in page


def test_doctor_page_has_no_nurse_actions_and_shows_the_covering_banner(client, db, staff_id, boundary_case):
    """S-064D: no "Mark as viewed", no "Escalate", no "Will be sent to"; banner 4B for the doctor on duty."""
    doctor = actions.escalate(db, boundary_case, staff_id("Trần Thị B"), NOW)
    page = client.get(f"/staff/{doctor}/cases/{boundary_case}").text
    assert f"/cases/{boundary_case}/view" not in page and f"/cases/{boundary_case}/escalate" not in page
    assert 'class="caption routing' not in page and "data-medicine-hint" not in page
    assert f"/cases/{boundary_case}/close" in page and "data-instruction-form" in page
    assert ui.t("This case was routed to you as the doctor on duty — the responsible doctor, Dr. {name}, is Away.",
                name="Phạm Quốc Dũng") in page


def test_responsible_doctor_sees_no_covering_banner(client, db, staff_id):
    doctor = staff_id("Nguyễn Văn A")
    mai = db.execute("SELECT case_id FROM CARE_CASE WHERE status = 'Escalated to doctor'").fetchone()[0]
    assert "data-covering" not in client.get(f"/staff/{doctor}/cases/{mai}").text


def test_same_routes_for_both_roles(client, staff_id, boundary_case):
    """D-107: one page per screen, the routes /staff/{id}/... unchanged."""
    for name in ("Trần Thị B", "Nguyễn Văn A"):
        sid = staff_id(name)
        assert client.get(f"/staff/{sid}/cases").status_code == 200
