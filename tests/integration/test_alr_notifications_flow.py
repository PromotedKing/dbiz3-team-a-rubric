"""T008 — ALR FR-018 through the actions of specs/001-alr-core and specs/002-cli-core."""
from tests.alr_status_helpers import RPT010, case_of_code, notifications, report_id
from tests.integration.helpers import bp_form, latest_report
from tests.integration.helpers import vi


def test_report_and_nurse_actions_notify_the_mother(client, db, user_id, staff_id):
    u09, nurse = user_id("tci-000131"), staff_id("Trần Thị B")
    n0 = len(notifications(db, u09))
    client.post(f"/m/{u09}/report", data=bp_form(150, 95, ["No symptoms"]))
    assert len(notifications(db, u09)) == n0 + 1

    case = db.execute("SELECT case_id FROM CARE_CASE WHERE metric_report_id = ?", (latest_report(db, u09)["report_id"],)).fetchone()[0]
    base = f"/staff/{nurse}/cases/{case}"
    client.post(f"{base}/view")
    client.post(f"{base}/guidance", data={"custom_text": "Rest and measure again in 30 minutes."})
    client.post(f"{base}/close")
    assert len(notifications(db, u09)) == n0 + 4


def test_escalation_from_not_viewed_notifies_once(client, db, user_id, staff_id):
    lan = user_id("tci-000123")
    n0 = len(notifications(db, lan))
    client.post(f"/staff/{staff_id('Trần Thị B')}/cases/{case_of_code(db, RPT010)}/escalate")
    assert len(notifications(db, lan)) == n0 + 1


def test_response_replaces_the_safety_note(client, db, user_id, staff_id):
    lan = user_id("tci-000123")
    page = f"/m/{lan}/reports/{report_id(db, RPT010)}"
    assert vi("Safety note") in client.get(page).text
    client.post(f"/staff/{staff_id('Trần Thị B')}/cases/{case_of_code(db, RPT010)}/guidance", data={"custom_text": "Please rest."})
    text = client.get(page).text
    assert vi("Response from Nurse {name}", name="Trần Thị B") in text and vi("Safety note") not in text
