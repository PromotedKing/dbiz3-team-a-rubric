"""T-02 — staff sign-in by role (D-107, D-82; spec-CLI §7.3 "Sign-in (Q11)", §5.3 E-4, E-5)."""
import pytest

from mb360 import ui
from mb360.cli import signin
from tests.cli_helpers import NOW


@pytest.fixture
def web(client):
    client.auto_sign_in = False         # these tests sign in themselves
    return client


@pytest.fixture
def team_password():
    """The hosted setting: MB360_STAFF_PASSWORD is set."""
    before = signin.PASSWORD, signin.HOSTED
    signin.PASSWORD, signin.HOSTED = "mật-khẩu-nhóm", True
    yield signin.PASSWORD
    signin.PASSWORD, signin.HOSTED = before


def sign_in(web, login, password=""):
    return web.post("/staff", data={"login": login, "password": password})


def test_nurse_signs_in_with_her_username_and_lands_on_her_own_dashboard(web, staff_id, team_password):
    nurse = staff_id("Trần Thị B")
    r = sign_in(web, "nurse.tranthib", team_password)
    assert r.status_code == 303 and r.headers["location"] == f"/staff/{nurse}/dashboard"
    page = web.get(f"/staff/{nurse}/cases").text
    assert ui.t("Nurse: {name}", name="Trần Thị B") in page and "data-sign-out" in page


def test_the_role_comes_from_staff_not_from_the_form(web, staff_id, team_password):
    """D-107: one form for both roles; the doctor gets the doctor view (S-061D)."""
    doctor = staff_id("Nguyễn Văn A")
    sign_in(web, "dr.nguyenvana", team_password)
    page = web.get(f"/staff/{doctor}/cases").text
    assert 'data-active-filter="Escalated to doctor"' in page and 'class="bell' in page
    assert ui.t("Dr. {name}", name="Nguyễn Văn A") in page


@pytest.mark.parametrize("login, password", [("nurse.tranthib", "sai"), ("không-có", "mật-khẩu-nhóm"), ("", "mật-khẩu-nhóm")])
def test_wrong_username_or_password_is_refused_with_one_message(web, team_password, login, password):
    r = sign_in(web, login, password)
    assert r.status_code == 401 and "data-login-error" in r.text
    assert ui.t("Wrong username or password.") in r.text
    assert signin.COOKIE not in r.cookies


def test_without_a_password_a_team_machine_needs_only_the_username(web, staff_id):
    """Team decision 21/11/2026: like the D-82 gate, no MB360_STAFF_PASSWORD on a team machine = no password asked."""
    assert sign_in(web, "nurse.tranthib").status_code == 303


def test_without_a_password_the_hosted_app_refuses_every_sign_in(web):
    before = signin.PASSWORD, signin.HOSTED
    signin.PASSWORD, signin.HOSTED = None, True
    try:
        assert sign_in(web, "nurse.tranthib", "").status_code == 401
    finally:
        signin.PASSWORD, signin.HOSTED = before


def test_pages_without_a_session_go_to_the_sign_in_form(web, staff_id, db):
    nurse = staff_id("Trần Thị B")
    case_id = db.execute("SELECT case_id FROM CARE_CASE LIMIT 1").fetchone()[0]
    for path in ("", "/dashboard", "/board", "/cases", f"/cases/{case_id}", "/notifications"):
        r = web.get(f"/staff/{nurse}{path}")
        assert r.status_code == 303 and r.headers["location"] == "/staff", path
    r = web.post(f"/staff/{nurse}/cases/{case_id}/view")
    assert r.status_code == 303 and r.headers["location"] == "/staff"


def test_e4_another_staff_members_id_is_refused_with_no_case_data(web, db, staff_id, team_password):
    """spec-CLI E-4: signed in as the nurse, the doctor's pages answer 403 and show no case."""
    sign_in(web, "nurse.tranthib", team_password)
    doctor = staff_id("Nguyễn Văn A")
    mai = db.execute("SELECT case_id FROM CARE_CASE WHERE status = 'Escalated to doctor'").fetchone()[0]
    for path in ("/dashboard", "/cases", f"/cases/{mai}", "/notifications"):
        r = web.get(f"/staff/{doctor}{path}")
        assert r.status_code == 403, path
        assert mai not in r.text and "data-case" not in r.text and ui.t("View report") not in r.text
        assert ui.t("This page belongs to another staff member.") in r.text


def test_e4_an_action_under_another_id_is_refused_and_writes_nothing(web, db, staff_id, team_password):
    sign_in(web, "dr.nguyenvana", team_password)
    nurse = staff_id("Trần Thị B")
    case_id = db.execute("SELECT case_id FROM CARE_CASE WHERE status = 'Not viewed'").fetchone()[0]
    assert web.post(f"/staff/{nurse}/cases/{case_id}/view").status_code == 403
    assert db.execute("SELECT status FROM CARE_CASE WHERE case_id = ?", (case_id,)).fetchone()[0] == "Not viewed"


def test_e5_a_nurse_cannot_do_a_doctor_only_action_whatever_she_sends(web, db, staff_id, team_password, boundary_case):
    """spec-CLI E-5: the server refuses, the buttons on the screen do not matter."""
    from mb360.cli import actions
    nurse = staff_id("Trần Thị B")
    actions.escalate(db, boundary_case, nurse, NOW)
    sign_in(web, "nurse.tranthib", team_password)
    r = web.post(f"/staff/{nurse}/cases/{boundary_case}/close")       # refused: shown as "already updated", nothing written
    assert r.status_code == 303 and r.headers["location"].endswith("?updated=1")
    assert web.post(f"/staff/{nurse}/cases/{boundary_case}/instructions", data={"metric": "Blood pressure"}).status_code == 403
    assert db.execute("SELECT status FROM CARE_CASE WHERE case_id = ?", (boundary_case,)).fetchone()[0] == "Escalated to doctor"


def test_a_forged_or_changed_cookie_is_not_a_session(web, staff_id):
    nurse, doctor = staff_id("Trần Thị B"), staff_id("Nguyễn Văn A")
    good = signin.token(nurse, "Nurse")
    for forged in (f"{nurse}.Doctor.{good.rsplit('.', 1)[1]}", f"{doctor}.Nurse.{good.rsplit('.', 1)[1]}", "rac", ""):
        web.cookies.set(signin.COOKIE, forged)
        assert web.get(f"/staff/{nurse}/cases").status_code == 303, forged


def test_sign_out_ends_the_session(web, staff_id, team_password):
    nurse = staff_id("Trần Thị B")
    sign_in(web, "nurse.tranthib", team_password)
    r = web.post("/staff/logout")
    assert r.status_code == 303 and r.headers["location"] == "/staff"
    web.cookies.delete(signin.COOKIE)        # the browser drops the cookie the response deleted
    assert web.get(f"/staff/{nurse}/cases").status_code == 303


def test_signed_in_the_sign_in_page_goes_to_the_own_dashboard(web, staff_id, team_password):
    sign_in(web, "dr.vuminhhai", team_password)
    r = web.get("/staff")
    assert r.status_code == 303 and r.headers["location"] == f"/staff/{staff_id('Vũ Minh Hải')}/dashboard"


def test_every_label_of_the_sign_in_is_in_the_reference_table(web, staff_id, team_password):
    ui.MISSING.clear()
    web.get("/staff")
    sign_in(web, "nurse.tranthib", "sai")
    sign_in(web, "nurse.tranthib", team_password)
    web.get(f"/staff/{staff_id('Nguyễn Văn A')}/cases")
    assert ui.MISSING == set()
