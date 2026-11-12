"""T007 — ACC FR-016, FR-017, BR-006 (Home S-008, minimal)."""
import re

from mb360.acc import entry
from tests.acc_helpers import NOW, new_identity
from tests.integration.helpers import vi


def test_lan_home(client, user_id):
    lan = user_id("tci-000123")
    page = client.get(f"/m/{lan}/home").text
    for text in (vi("Hello, {name}!", name="Lan"), vi("Week {n} + {d} days", n=28, d=0), vi("Due date"), "20/12/2026",
                 vi("Blood pressure"), vi("Report metric / symptom")):
        assert text in page, text
    report = client.get(f"/m/{lan}/report").text        # Màn 4 has no menu: Màn 5 leads to My reports, Màn 12 to the instructions
    assert f'href="/m/{lan}/my-reports"' in report and f'href="/m/{lan}/instructions"' in client.get(f"/m/{lan}/profile").text


def test_home_without_due_date_goes_to_setup(client, user_id, mother_without_profile):
    u07 = user_id("tci-000133")
    r = client.get(f"/m/{u07}/home")
    assert r.status_code == 303 and r.headers["location"] == f"/m/{u07}/setup"


def test_no_alert_word(client, db, user_id):
    uid = entry.agree(db, new_identity(), True, NOW)
    for url in (f"/m/{uid}/guide", f"/m/{uid}/setup", f"/m/{user_id('tci-000123')}/home"):
        assert "alert" not in re.sub(r"<[^>]+>", " ", client.get(url).text).lower(), url
