"""D-109 — the "Notifications" page of the clinical web (S-059, S-061 #4)."""
from mb360 import ui
from mb360.cli import actions

from tests.cli_helpers import NOW


def test_nurse_has_no_bell_and_sees_the_count_on_the_case_list(client, db, staff_id):
    """D-105 (built 21/11/2026; the nurse bell of D-109 is dropped — Chi to confirm, spec-CLI §10 Q5): no Notifications button for the nurse;
    the number of cases waiting for her sits next to the case list instead (S-061 #2, D-104)."""
    nurse = staff_id("Trần Thị B")
    waiting = db.execute("SELECT COUNT(*) FROM CARE_CASE WHERE status = 'Not viewed'").fetchone()[0]
    for path in ("dashboard", "board", "cases"):
        page = client.get(f"/staff/{nurse}/{path}").text
        assert f'href="/staff/{nurse}/notifications"' not in page
        assert f"<span data-home-count>({waiting})</span>" in page


def test_doctor_bell_opens_the_notifications_page(client, db, staff_id):
    doctor = staff_id("Nguyễn Văn A")
    page = client.get(f"/staff/{doctor}/dashboard").text
    assert f'href="/staff/{doctor}/notifications"' in page and '<span class="badge">1</span>' in page


def test_nurse_notifications_address_opens_her_priority_list(client, staff_id):
    """D-105: an old link to the nurse's notification list lands on her case list, ordered by Priority (D-104)."""
    nurse = staff_id("Trần Thị B")
    r = client.get(f"/staff/{nurse}/notifications", follow_redirects=False)
    assert r.status_code == 303 and r.headers["location"] == f"/staff/{nurse}/cases"


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


def test_unknown_staff_member_is_sent_to_sign_in(client):
    """D-107: an id with no session behind it never reaches a page (was 404 before the sign-in)."""
    r = client.get("/staff/00000000-0000-0000-0000-000000000000/notifications")
    assert r.status_code == 303 and r.headers["location"] == "/staff"


def test_every_label_of_the_page_is_in_the_reference_table(client, db, staff_id, boundary_case):
    """D-79: no English text slips onto the screen (ui.MISSING is what the table does not have)."""
    ui.MISSING.clear()
    actions.escalate(db, boundary_case, staff_id("Trần Thị B"), NOW)
    for sid in [r[0] for r in db.execute("SELECT staff_id FROM STAFF WHERE role = 'Doctor'")]:   # D-105: doctors only
        assert client.get(f"/staff/{sid}/notifications").status_code == 200
    assert ui.MISSING == set()
