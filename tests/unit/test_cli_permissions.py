"""T007 — CLI BR-001, BR-004 (permission table), BR-008."""
import pytest

from mb360.cli import actions
from tests.cli_helpers import NOW, RPT004, a_template, case_by_code, case_row, written


def test_nurse_allowed_actions_on_a_case_not_escalated(db, staff_id, boundary_case):
    """`boundary_case` is 140/90 = "Above threshold", so BR-012 (D-98, proposed) takes "close" away:
    escalating is the only way on. A case below the threshold keeps it — tests/unit/test_cli_must_escalate.py."""
    assert actions.allowed(db, boundary_case, staff_id("Trần Thị B")) == {"view", "escalate", "guidance"}


def test_nurse_cannot_close_an_escalated_case(db, staff_id):
    case, nurse = case_by_code(db, RPT004), staff_id("Trần Thị B")
    assert "close" not in actions.allowed(db, case, nurse)
    before = written(db)
    with pytest.raises(actions.ActionError):
        actions.close_case(db, case, nurse, NOW)
    assert written(db) == before


def test_doctor_never_marks_as_viewed_or_escalates(db, staff_id, boundary_case):
    doctor = staff_id("Phạm Quốc Dũng")
    case = boundary_case
    for act in (actions.mark_viewed, actions.escalate):
        with pytest.raises(actions.ActionError) as e:
            act(db, case, doctor, NOW)
        assert e.value.status == 403


def test_doctor_acts_only_on_escalated_cases(db, staff_id, boundary_case):
    doctor = staff_id("Nguyễn Văn A")
    assert actions.allowed(db, case_by_code(db, RPT004), doctor) == {"guidance", "close"}
    assert actions.allowed(db, boundary_case, doctor) == set()
    before = written(db)
    for act in (lambda c: actions.send_guidance(db, c, doctor, NOW, custom_text="Rest"),
                lambda c: actions.close_case(db, c, doctor, NOW)):
        with pytest.raises(actions.ActionError) as e:
            act(boundary_case)
        assert e.value.status == 403
    assert written(db) == before


def test_send_guidance_never_changes_the_status(db, staff_id, boundary_case):
    case, nurse = boundary_case, staff_id("Trần Thị B")
    actions.send_guidance(db, case, nurse, NOW, template_id=a_template(db))
    assert case_row(db, case)["status"] == "Not viewed"
    resp = db.execute("SELECT * FROM STAFF_RESPONSE WHERE case_id = ?", (case,)).fetchall()
    assert len(resp) == 1 and resp[0]["responder_role"] == "Nurse" and resp[0]["responder_id"] == nurse


@pytest.mark.parametrize("template, text, ok", [(False, "", False), (False, "x" * 1000, True), (False, "x" * 1001, False),
                                                (True, "", True), (True, "Extra", True)])
def test_guidance_needs_a_template_or_text_up_to_1000(db, staff_id, template, text, ok, boundary_case):
    case, nurse = boundary_case, staff_id("Trần Thị B")
    args = {"template_id": a_template(db) if template else None, "custom_text": text or None}
    if ok:
        actions.send_guidance(db, case, nurse, NOW, **args)
    else:
        with pytest.raises(actions.ActionError) as e:
            actions.send_guidance(db, case, nurse, NOW, **args)
        assert e.value.status == 422
