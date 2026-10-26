"""T004 — ALR BR-001: the system never removes a Doctor's instruction automatically."""
from mb360.cli import actions
from tests.cli_helpers import NOW
from tests.integration.helpers import bp_form, latest_report


def test_report_case_cycle_keeps_the_instructions(client, db, user_id, staff_id):
    u09 = user_id("tci-000131")
    before = [tuple(r) for r in db.execute("SELECT * FROM WATCH_FLAG WHERE user_id = ? ORDER BY flag_id", (u09,))]
    client.post(f"/m/{u09}/report", data=bp_form(160, 100, ["No symptoms"]))
    case = db.execute("SELECT case_id FROM CARE_CASE WHERE metric_report_id = ?", (latest_report(db, u09)["report_id"],)).fetchone()[0]
    actions.escalate(db, case, staff_id("Trần Thị B"), NOW)
    actions.close_case(db, case, staff_id("Phạm Quốc Dũng"), NOW)
    after = [tuple(r) for r in db.execute("SELECT * FROM WATCH_FLAG WHERE user_id = ? ORDER BY flag_id", (u09,))]
    assert after == before
