"""D-100 (proposed), 16/11/2026, reported by Sang: after every expired session the hosted app sent the mother through consent
and setup again. Cause: on the free hosting plan the database file is lost at each restart (sleep after ~15 minutes idle,
every deploy), so her consent, profile and session were gone. These tests run mb360.server itself on a temporary file."""
import importlib
import sys

import pytest
from fastapi.testclient import TestClient

from mb360 import clock, persona, ui
from mb360.acc import entry
from mb360.bot import llm


@pytest.fixture
def start(tmp_path, monkeypatch):
    """start() imports mb360.server as the platform starts it; start(wipe=True) first deletes the database file (a restart)."""
    db_file = tmp_path / "mb360-app.sqlite"
    monkeypatch.setenv("MB360_DB", str(db_file))
    monkeypatch.delenv("RENDER", raising=False)
    monkeypatch.setattr(persona, "_copy_art", lambda: None)
    for module, name in ((ui, "SHOWCASE"), (entry, "SECURE_COOKIE"), (llm, "_fallback")):
        monkeypatch.setattr(module, name, getattr(module, name))      # restored after the test
    opened = []

    def run(wipe=False):
        if wipe and db_file.exists():
            for conn in opened:
                conn.close()
            db_file.unlink()
        sys.modules.pop("mb360.server", None)
        server = importlib.import_module("mb360.server")
        opened.append(server.conn)
        return server, TestClient(server.app, follow_redirects=False)
    yield run
    for conn in opened:
        conn.close()
    sys.modules.pop("mb360.server", None)
    clock.reset()


def open_from_tci(client, server):
    me = server.conn.execute("SELECT * FROM USER_ACCOUNT WHERE user_id = ?", (persona.USER,)).fetchone()
    return client.post("/tci/open", data={k: me[k] for k in ("tci_account_ref", "full_name", "phone", "date_of_birth", "record_code")} | {"sex": "Female"})


def test_a_new_database_starts_after_the_first_opening(start):
    """The sample mother has agreed and set up her pregnancy: opening from the TCI app goes straight to Home."""
    server, client = start()
    r = open_from_tci(client, server)
    assert r.status_code == 303 and r.headers["location"] == f"/m/{persona.USER}/home"
    assert client.get(r.headers["location"]).status_code == 200


def test_restart_keeps_her_out_of_consent_and_setup(start):
    server, client = start()
    open_from_tci(client, server)
    server, client2 = start(wipe=True)                                   # the platform restarted: the file is gone
    client2.cookies.update(client.cookies)                                # the phone still has its old session cookie
    r = client2.get(f"/m/{persona.USER}/home")
    assert r.status_code == 303 and r.headers["location"] == f"/m/{persona.USER}/home"   # reopened, not S-043
    assert entry.valid_session(server.conn, r.cookies.get(entry.COOKIE), persona.USER, clock.now())
    assert client2.get(f"/m/{persona.USER}/home").status_code == 200


def test_a_post_with_a_lost_session_goes_back_to_its_page(start):
    server, client = start()
    page = f"http://testserver/m/{persona.USER}/chat"
    r = client.post(f"/m/{persona.USER}/chat", data={"text": "Bà bầu nên ăn gì?"}, headers={"referer": page})
    assert r.status_code == 303 and r.headers["location"] == f"/m/{persona.USER}/chat"
    assert server.conn.execute("SELECT COUNT(*) FROM CHAT_MESSAGE WHERE text = 'Bà bầu nên ăn gì?'").fetchone()[0] == 0   # not replayed


def test_another_mothers_page_still_needs_her_own_session(start):
    server, client = start()
    other = server.conn.execute("SELECT user_id FROM USER_ACCOUNT WHERE tci_account_ref = 'tci-000123'").fetchone()[0]
    r = client.get(f"/m/{other}/home")
    assert r.status_code == 303 and r.headers["location"] == "/session-expired"


def test_the_reset_button_still_shows_the_first_opening(start):
    server, client = start()
    assert client.post("/showcase/reset").status_code == 303
    r = open_from_tci(client, server)
    assert r.status_code == 200 and "/tci/consent" in r.text                # S-001 state 2: consent again, on purpose
