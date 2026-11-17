"""D-107 — the "Notifications" page of the clinical web (S-059, S-061 #4)."""
from mb360 import ui
from mb360.cli import actions

from tests.cli_helpers import NOW


def test_nurse_sees_the_bell_with_the_first_look_queue(client, db, staff_id):
    """S-061 #4 for the nurse was [NEEDS CLARIFICATION] before D-107: she had no bell at all."""
    nurse = staff_id("Trần Thị B")
    waiting = db.execute("SELECT COUNT(*) FROM CARE_CASE WHERE status = 'Not viewed'").fetchone()[0]
    page = client.get(f"/staff/{nurse}/dashboard").text
    assert f'href="/staff/{nurse}/notifications"' in page
    assert f'<span class="badge">{waiting}</span>' in page


def test_doctor_bell_opens_the_notifications_page(client, db, staff_id):
    doctor = staff_id("Nguyễn Văn A")
    page = client.get(f"/staff/{doctor}/dashboard").text
    assert f'href="/staff/{doctor}/notifications"' in page and '<span class="badge">1</span>' in page


def test_nurse_page_lists_the_cases_waiting_in_vietnamese(client, db, staff_id):
    nurse = staff_id("Trần Thị B")
    page = client.get(f"/staff/{nurse}/notifications").text
    assert ui.t("Cases waiting for a first look.") in page
    assert ui.t("Cases a nurse escalated to you.") not in page
    for case_id in [r[0] for r in db.execute("SELECT case_id FROM CARE_CASE WHERE status = 'Not viewed'")]:
        assert f'data-case="{case_id}"' in page


def test_doctor_page_names_the_nurse_who_escalated(client, db, staff_id, boundary_case):
    nurse = staff_id("Trần Thị B")
    doctor = actions.escalate(db, boundary_case, nurse, NOW)
    page = client.get(f"/staff/{doctor}/notifications").text
    assert ui.t("Cases a nurse escalated to you.") in page
    assert f'data-case="{boundary_case}"' in page
    assert ui.t("Escalated by Nurse {name} · {time}", name="Trần Thị B", time="27/09/2026 · 10:00") in page


def test_empty_state_for_a_doctor_with_no_escalated_case(client, staff_id):
    page = client.get(f"/staff/{staff_id('Phạm Quốc Dũng')}/notifications").text
    assert ui.t("No notifications.") in page and ui.t("{n} waiting", n=0) in page


def test_unknown_staff_member_gets_404(client):
    assert client.get("/staff/00000000-0000-0000-0000-000000000000/notifications").status_code == 404


def test_every_label_of_the_page_is_in_the_reference_table(client, db, staff_id, boundary_case):
    """D-79: no English text slips onto the screen (ui.MISSING is what the table does not have)."""
    ui.MISSING.clear()
    actions.escalate(db, boundary_case, staff_id("Trần Thị B"), NOW)
    for sid in [r[0] for r in db.execute("SELECT staff_id FROM STAFF")]:
        assert client.get(f"/staff/{sid}/notifications").status_code == 200
    assert ui.MISSING == set()
