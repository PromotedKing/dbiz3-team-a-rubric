"""T006 — shared fixtures: a fresh database from schema + seed for every test, and a fixed clock."""
import pytest

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
    yield conn
    conn.close()
    clock.reset()


@pytest.fixture
def client(db):
    from fastapi.testclient import TestClient

    from mb360.main import create_app

    return TestClient(create_app(db), follow_redirects=False)


@pytest.fixture
def user_id(db):
    """Seed mother by TCI reference, e.g. user_id('tci-000131') -> U09."""
    def find(tci_ref: str) -> str:
        return db.execute("SELECT user_id FROM USER_ACCOUNT WHERE tci_account_ref = ?", (tci_ref,)).fetchone()[0]
    return find


@pytest.fixture
def staff_id(db):
    """Seed staff by full name, e.g. staff_id('Trần Thị B')."""
    def find(name: str) -> str:
        return db.execute("SELECT staff_id FROM STAFF WHERE full_name = ?", (name,)).fetchone()[0]
    return find
