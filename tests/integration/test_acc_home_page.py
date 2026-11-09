"""T007 — ACC FR-016, FR-017, BR-006 (Home S-008, minimal)."""
import re

from mb360.acc import entry
from tests.acc_helpers import NOW, new_identity
from tests.integration.helpers import vi


def test_lan_home(client, user_id):
    lan = user_id("tci-000123")
    page = client.get(f"/m/{lan}/home").text
    for text in (vi("Hello, {name}!", name="Lan"), vi("Week {n} + {d} days", n=28, d=0), vi("Due date"), "20/12/2026",
                 vi("Doctor's instructions"), vi("Blood pressure"), vi("Blood glucose"), vi("My reports")):
        assert text in page, text
    assert f'href="/m/{lan}/instructions"' in page and f'href="/m/{lan}/my-reports"' in page


def test_home_without_due_date_goes_to_setup(client, user_id):
    u07 = user_id("tci-000129")
    r = client.get(f"/m/{u07}/home")
    assert r.status_code == 303 and r.headers["location"] == f"/m/{u07}/setup"


def test_no_alert_word(client, db, user_id):
    uid = entry.agree(db, new_identity(), True, NOW)
    for url in (f"/m/{uid}/guide", f"/m/{uid}/setup", f"/m/{user_id('tci-000123')}/home"):
        assert "alert" not in re.sub(r"<[^>]+>", " ", client.get(url).text).lower(), url
