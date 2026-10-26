"""T003 — CLI FR-025, BR-001, BR-006; DM-21 default (one active instruction per metric)."""
import pytest

from mb360.cli import actions, instructions
from tests.cli_helpers import NOW, a_template


def flags(db, user):
    return db.execute("SELECT * FROM WATCH_FLAG WHERE user_id = ? ORDER BY metric", (user,)).fetchall()


def test_doctor_adds_an_instruction(db, user_id, staff_id):
    u09, doctor = user_id("tci-000131"), staff_id("Phạm Quốc Dũng")
    tpl = a_template(db)
    flag_id = instructions.save_instruction(db, u09, doctor, NOW, "Blood glucose", note="Measure fasting every morning", template_id=tpl)
    row = db.execute("SELECT * FROM WATCH_FLAG WHERE flag_id = ?", (flag_id,)).fetchone()
    assert (row["user_id"], row["metric"], row["active"], row["flagged_by"], row["flagged_at"]) == (u09, "Blood glucose", 1, doctor, "2026-09-27")
    assert (row["note"], row["template_id"], row["visit_id"]) == ("Measure fasting every morning", tpl, None)


def test_saving_an_existing_metric_edits_it(db, user_id, staff_id):
    u09 = user_id("tci-000131")
    before = flags(db, u09)
    w09 = [f for f in before if f["metric"] == "Blood pressure"][0]["flag_id"]
    flag_id = instructions.save_instruction(db, u09, staff_id("Phạm Quốc Dũng"), NOW, "Blood pressure", note="Twice a day", custom_text="Lie down and call the hospital")
    assert flag_id == w09
    after = flags(db, u09)
    assert len(after) == len(before)
    row = [f for f in after if f["flag_id"] == w09][0]
    assert (row["note"], row["custom_text"]) == ("Twice a day", "Lie down and call the hospital")


def test_nurse_cannot_save(db, user_id, staff_id):
    u09 = user_id("tci-000131")
    before = [tuple(r) for r in flags(db, u09)]
    with pytest.raises(actions.ActionError) as e:
        instructions.save_instruction(db, u09, staff_id("Trần Thị B"), NOW, "Blood glucose", note="x")
    assert e.value.status == 403
    assert [tuple(r) for r in flags(db, u09)] == before


@pytest.mark.parametrize("kw", [{"metric": "Weight"}, {"metric": "Blood glucose", "custom_text": "x" * 1001},
                                {"metric": "Blood glucose", "template_id": "00000000-0000-0000-0000-000000000000"}])
def test_invalid_input_is_refused(db, user_id, staff_id, kw):
    u09 = user_id("tci-000131")
    before = len(flags(db, u09))
    with pytest.raises(actions.ActionError) as e:
        instructions.save_instruction(db, u09, staff_id("Phạm Quốc Dũng"), NOW, **kw)
    assert e.value.status == 422
    assert len(flags(db, u09)) == before


def test_custom_text_of_1000_and_no_guidance_are_allowed(db, user_id, staff_id):
    u09, doctor = user_id("tci-000131"), staff_id("Phạm Quốc Dũng")
    instructions.save_instruction(db, u09, doctor, NOW, "Blood glucose", custom_text="x" * 1000)
    fid = instructions.save_instruction(db, u09, doctor, NOW, "Urine protein")        # no guidance -> S-028 default (D-24)
    row = db.execute("SELECT template_id, custom_text FROM WATCH_FLAG WHERE flag_id = ?", (fid,)).fetchone()
    assert row["template_id"] is None and row["custom_text"] is None
