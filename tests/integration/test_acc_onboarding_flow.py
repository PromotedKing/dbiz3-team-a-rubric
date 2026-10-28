"""T005 — ACC US-1 #1 - #6 (S-001 states, notice, S-104)."""
import re

from tests.acc_helpers import count, new_identity, seed_identity
from tests.integration.helpers import vi


def test_tci_home_lists_accounts_and_the_simulate_form(client):
    page = client.get("/tci").text
    assert vi("Mother & Baby 360") in page and "Nguyễn Thị Lan" in page and vi("Simulate another TCI account") in page


def test_first_opening_shows_the_consent_sheet(client):
    r = client.post("/tci/open", data=new_identity())
    assert r.status_code == 200
    for text in map(vi, ("Connect to your TCI account", "Full name, date of birth, phone number", "Medical record number at Thu Cuc",
                         "Results of your prenatal visits", "I agree to the Terms and the Privacy Policy", "Agree & continue", "Later")):
        assert text in r.text, text
    assert 'type="password"' not in r.text


def test_unticked_box_and_later_store_nothing(client, db):
    r = client.post("/tci/consent", data={**new_identity(), "action": "agree"})
    assert r.status_code == 422 and 'data-error-for="agree"' in r.text
    r = client.post("/tci/consent", data={**new_identity(), "action": "later", "agree": "on"})
    assert r.status_code == 303 and r.headers["location"] == "/tci"
    assert count(db, "USER_ACCOUNT", "tci_account_ref = 'tci-test-001'") == 0


def test_agree_then_guide_then_setup(client, db):
    r = client.post("/tci/consent", data={**new_identity(), "action": "agree", "agree": "on"})
    assert r.status_code == 303
    uid = db.execute("SELECT user_id FROM USER_ACCOUNT WHERE tci_account_ref = 'tci-test-001'").fetchone()[0]
    assert r.headers["location"] == f"/m/{uid}/guide"
    guide = client.get(r.headers["location"]).text
    assert vi("Skip") in guide and vi("Next") in guide and 'data-guide-pages="4"' in guide
    assert vi("Get started") in client.get(f"/m/{uid}/guide", params={"page": 4}).text
    done = client.get(f"/m/{uid}/guide/done")
    assert done.status_code == 303 and done.headers["location"] == f"/m/{uid}/setup"


def test_non_female_notice(client, db):
    r = client.post("/tci/open", data=new_identity(sex="Male"))
    assert r.status_code == 200
    assert vi("Mother & Baby 360 is for expectant mothers.") in r.text and vi("Back to TCI app") in r.text
    assert count(db, "USER_ACCOUNT", "tci_account_ref = 'tci-test-001'") == 0


def test_returning_mother_goes_home(client, db):
    r = client.post("/tci/open", data=seed_identity(db, "tci-000123"))
    lan = db.execute("SELECT user_id FROM USER_ACCOUNT WHERE tci_account_ref = 'tci-000123'").fetchone()[0]
    assert r.status_code == 303 and r.headers["location"] == f"/m/{lan}/home"


def test_no_alert_word_on_entry_pages(client):
    pages = [client.get("/tci").text, client.post("/tci/open", data=new_identity()).text,
             client.post("/tci/open", data=new_identity(sex="Male")).text]
    for p in pages:
        assert "alert" not in re.sub(r"<[^>]+>", " ", p).lower()
