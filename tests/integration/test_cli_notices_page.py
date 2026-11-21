"""D-109 — the "Notifications" page of the clinical web (S-059, S-061 #4)."""
from mb360 import ui
from mb360.cli import actions

from tests.cli_helpers import NOW


def test_nurse_has_no_bell_on_any_page(client, db, staff_id):
    """D-105: the Nurse role has no "Notifications" button — the signal is the Priority order, the Waiting column
    and the count on Home (n) (D-104). The Doctor keeps the bell."""
    nurse = staff_id("Trần Thị B")
    for path in ("dashboard", "board", "cases"):
        page = client.get(f"/staff/{nurse}/{path}").text
        assert 'class="bell' not in page and f"/staff/{nurse}/notifications" not in page, path


def test_doctor_bell_opens_the_notifications_page(client, db, staff_id):
    doctor = staff_id("Nguyễn Văn A")
    page = client.get(f"/staff/{doctor}/dashboard").text
    assert f'href="/staff/{doctor}/notifications"' in page and '<span class="badge">1</span>' in page


def test_nurse_has_no_notifications_page(client, staff_id):
    assert client.get(f"/staff/{staff_id('Trần Thị B')}/notifications").status_code == 404


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
    for sid in [r[0] for r in db.execute("SELECT staff_id FROM STAFF WHERE role = 'Doctor'")]:   # the Nurse has none (D-105)
        assert client.get(f"/staff/{sid}/notifications").status_code == 200
    assert ui.MISSING == set()
