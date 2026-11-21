"""T006 — shared fixtures: a fresh database from schema + seed for every test, and a fixed clock."""
import pytest
from uuid import uuid4

from mb360 import clock, ui
from mb360 import db as dbmod


@pytest.fixture(autouse=True)
def every_label_is_in_the_reference():
    """D-79: every text a page shows comes from docs/ui-label-reference.md."""
    ui.MISSING.clear()
    yield
    assert not ui.MISSING, f"labels missing from docs/ui-label-reference.md: {sorted(ui.MISSING)}"


@pytest.fixture
def db():
    clock.reset()
    conn = dbmod.build()
    try:
        yield conn
    finally:
        conn.close()
        clock.reset()


@pytest.fixture
def client(db):
    """D-107: /staff/{id}/... needs a staff session. Tests written before the sign-in reach those pages as that staff
    member, so the client signs in as the {id} of the path. Set `client.auto_sign_in = False` to test the sign-in
    itself (tests/integration/test_cli_sign_in.py)."""
    import re

    from fastapi.testclient import TestClient

    from mb360.cli import signin
    from mb360.main import create_app

    staff_path = re.compile(r"^/staff/([0-9a-f-]{36})(/|$)")

    class StaffClient(TestClient):
        auto_sign_in = True

        def request(self, method, url, *args, **kwargs):
            m = staff_path.match(str(url).split("?", 1)[0].replace(str(self.base_url), ""))
            if self.auto_sign_in and m:
                row = db.execute("SELECT role FROM STAFF WHERE staff_id = ?", (m.group(1),)).fetchone()
                if row is not None:
                    self.cookies.set(signin.COOKIE, signin.token(m.group(1), row["role"]))
            return super().request(method, url, *args, **kwargs)

    return StaffClient(create_app(db), follow_redirects=False)


@pytest.fixture
def user_id(db):
    """Seed mother by TCI reference, e.g. user_id('tci-000123') -> Lan."""
    def find(tci_ref: str) -> str:
        return db.execute("SELECT user_id FROM USER_ACCOUNT WHERE tci_account_ref = ?", (tci_ref,)).fetchone()[0]
    return find


@pytest.fixture
def staff_id(db):
    """Seed staff by full name, e.g. staff_id('Trần Thị B')."""
    def find(name: str) -> str:
        return db.execute("SELECT staff_id FROM STAFF WHERE full_name = ?", (name,)).fetchone()[0]
    return find


@pytest.fixture
def mother_without_profile(db, user_id):
    user = user_id("tci-000133")
    db.execute("DELETE FROM PREGNANCY_PROFILE WHERE user_id = ?", (user,))
    return user


def _pending_link(db, user, code):
    db.execute("""INSERT INTO EMR_LINKAGE_REQUEST
                  (user_id, record_code, facility, status, requested_at)
                  VALUES (?, ?, 'Thu Cuc Hospital', 'Pending', '2026-09-10 08:00')""",
               (user, code))


@pytest.fixture
def pending_mother(db, user_id):
    user = user_id("tci-000133")
    _pending_link(db, user, "TC-DEMO-PENDING")
    return user


@pytest.fixture
def older_pending_link(db, user_id):
    user = user_id("tci-000123")
    _pending_link(db, user, "TC-00123")
    return user


@pytest.fixture
def assigned_mother(db, user_id, staff_id):
    user = user_id("tci-000126")
    db.execute("UPDATE PATIENT_ASSIGNMENT SET doctor_id = ? WHERE user_id = ?",
               (staff_id("Phạm Quốc Dũng"), user))
    return user


@pytest.fixture
def ended_assignment(db, assigned_mother, staff_id):
    db.execute("UPDATE PATIENT_ASSIGNMENT SET valid_from = '2026-09-13' WHERE user_id = ?",
               (assigned_mother,))
    db.execute("""INSERT INTO PATIENT_ASSIGNMENT (user_id, doctor_id, valid_from, valid_to)
                  VALUES (?, ?, '2026-09-01', '2026-09-12')""",
               (assigned_mother, staff_id("Nguyễn Văn A")))


@pytest.fixture
def protein_instruction_mother(db, user_id, staff_id):
    user = user_id("tci-000126")
    db.execute("UPDATE WATCH_FLAG SET active = 0 WHERE user_id = ? AND metric = 'Blood pressure'", (user,))
    db.execute("""INSERT INTO WATCH_FLAG (flag_id, user_id, metric, flagged_by, flagged_at, active)
                  VALUES (?, ?, 'Urine protein', ?, '2026-09-26', 1)""",
               (str(uuid4()), user, staff_id("Nguyễn Văn A")))
    return user


@pytest.fixture
def boundary_case(db, assigned_mother):
    from tests.cli_helpers import open_boundary_case

    return open_boundary_case(db, assigned_mother)


@pytest.fixture
def resolved_escalated_case(db, user_id, staff_id):
    from mb360.cli import actions
    from tests.cli_helpers import NOW, open_boundary_case

    case = open_boundary_case(db, user_id("tci-000126"))
    actions.escalate(db, case, staff_id("Trần Thị B"), NOW)
    actions.close_case(db, case, staff_id("Nguyễn Văn A"), NOW)
    return case
