"""T006 — shared fixtures: a fresh database from schema + seed for every test, and a fixed clock."""
import pytest

from mb360 import clock
from mb360 import db as dbmod


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
