"""D-96 — the "Notifications" list inside the clinical web (S-059; CLI FR-005, FR-019, FR-020; ALR FR-009).

Nothing is stored (DM-32): every line is read from CARE_CASE and CASE_STATUS_HISTORY.
"""
from mb360.cli import actions, notices

from tests.cli_helpers import NOW, RPT004, case_by_code


def stored(db):
    return {t: db.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0] for t in ("NOTIFICATION", "CASE_STATUS_HISTORY")}


# ---------------------------------------------------------------- the bell (S-061 #4)

def test_nurse_badge_counts_every_case_waiting_for_a_first_look(db, staff_id):
    """D-96: the nurse's number is the "Not viewed" queue, whoever the mother's doctor is."""
    expected = db.execute("SELECT COUNT(*) FROM CARE_CASE WHERE status = 'Not viewed'").fetchone()[0]
    assert expected > 0
    assert notices.count(db, staff_id("Trần Thị B"), "Nurse") == expected


def test_doctor_badge_counts_only_his_escalated_cases(db, staff_id):
    assert notices.count(db, staff_id("Nguyễn Văn A"), "Doctor") == 1
    assert notices.count(db, staff_id("Phạm Quốc Dũng"), "Doctor") == 0


def test_nurse_badge_drops_when_the_case_is_viewed(db, staff_id, boundary_case):
    nurse = staff_id("Trần Thị B")
    before = notices.count(db, nurse, "Nurse")
    actions.mark_viewed(db, boundary_case, nurse, NOW)
    assert notices.count(db, nurse, "Nurse") == before - 1


# ---------------------------------------------------------------- nurse list

def test_nurse_sees_only_cases_not_viewed_yet(db, staff_id):
    rows = notices.lines(db, staff_id("Trần Thị B"), "Nurse", NOW)
    assert rows and {r["status"] for r in rows} == {"Not viewed"}
    assert len(rows) == notices.count(db, staff_id("Trần Thị B"), "Nurse")


def test_nurse_list_puts_above_threshold_and_alarm_symptoms_on_top(db, staff_id, boundary_case):
    rows = notices.lines(db, staff_id("Trần Thị B"), "Nurse", NOW)
    urgent = [r["urgent"] for r in rows]
    assert urgent == sorted(urgent, reverse=True)          # every urgent line before the rest
    assert any(urgent), "the seed has an above-threshold or alarm case not viewed yet"
    for r in rows:                                          # the label comes from THRESHOLD_RULE, never a number here
        assert r["urgent"] == (r["label"] == "Above threshold" or r["alarm"])


def test_nurse_list_shows_the_longest_wait_first_inside_a_group(db, staff_id):
    rows = notices.lines(db, staff_id("Trần Thị B"), "Nurse", NOW)
    for group in (True, False):
        times = [r["created_at"] for r in rows if r["urgent"] is group]
        assert times == sorted(times)


# ---------------------------------------------------------------- doctor list

def test_doctor_sees_the_case_a_nurse_escalated_with_who_and_when(db, staff_id):
    rows = notices.lines(db, staff_id("Nguyễn Văn A"), "Doctor", NOW)
    assert len(rows) == 1
    line = rows[0]
    assert line["status"] == "Escalated to doctor" and line["case_id"] == case_by_code(db, RPT004)
    assert line["escalation"]["role"] in ("Nurse", "Doctor", "System")
    assert line["escalation"]["at"] == db.execute(
        "SELECT changed_at FROM CASE_STATUS_HISTORY WHERE case_id = ? AND status = 'Escalated to doctor'",
        (line["case_id"],)).fetchone()[0]


def test_doctor_does_not_see_another_doctors_cases(db, staff_id):
    assert notices.lines(db, staff_id("Phạm Quốc Dũng"), "Doctor", NOW) == []


def test_escalating_adds_a_line_for_the_responsible_doctor_only(db, staff_id, boundary_case):
    """CLI BR-003 / ALR FR-009: the line appears for the mother's own doctor (D-68)."""
    nurse = staff_id("Trần Thị B")
    doctor = actions.escalate(db, boundary_case, nurse, NOW)
    mine = [r["case_id"] for r in notices.lines(db, doctor, "Doctor", NOW)]
    assert boundary_case in mine
    others = {s[0] for s in db.execute("SELECT staff_id FROM STAFF WHERE role = 'Doctor'")} - {doctor}
    for other in others:
        assert boundary_case not in [r["case_id"] for r in notices.lines(db, other, "Doctor", NOW)]


def test_escalation_line_names_the_nurse_who_escalated(db, staff_id, boundary_case):
    nurse = staff_id("Trần Thị B")
    doctor = actions.escalate(db, boundary_case, nurse, NOW)
    line = next(r for r in notices.lines(db, doctor, "Doctor", NOW) if r["case_id"] == boundary_case)
    assert line["escalation"] == {"at": NOW.strftime("%Y-%m-%d %H:%M"), "role": "Nurse",
                                 "by": db.execute("SELECT full_name FROM STAFF WHERE staff_id = ?", (nurse,)).fetchone()[0]}


def test_doctor_list_puts_the_cases_without_his_answer_first(db, staff_id, boundary_case):
    doctor = actions.escalate(db, boundary_case, staff_id("Trần Thị B"), NOW)
    actions.send_guidance(db, boundary_case, doctor, NOW, custom_text="Mời mẹ vào viện kiểm tra.")
    rows = notices.lines(db, doctor, "Doctor", NOW)
    answered = [r["doctor_answered"] for r in rows]
    assert answered == sorted(answered)                    # unanswered first
    assert rows[-1]["case_id"] == boundary_case


# ---------------------------------------------------------------- DM-32

def test_reading_the_list_stores_nothing(db, staff_id):
    before = stored(db)
    notices.lines(db, staff_id("Trần Thị B"), "Nurse", NOW)
    notices.lines(db, staff_id("Nguyễn Văn A"), "Doctor", NOW)
    notices.count(db, staff_id("Trần Thị B"), "Nurse")
    assert stored(db) == before


def test_no_notification_row_is_written_for_staff(db, staff_id, boundary_case):
    """DM-32: NOTIFICATION is the mother's; escalation writes only her row, never one for the doctor."""
    actions.escalate(db, boundary_case, staff_id("Trần Thị B"), NOW)
    staff_ids = {s[0] for s in db.execute("SELECT staff_id FROM STAFF")}
    owners = {r[0] for r in db.execute("SELECT DISTINCT user_id FROM NOTIFICATION")}
    assert owners.isdisjoint(staff_ids)
